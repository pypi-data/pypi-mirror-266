"""
This module provides a connector to a redis server. It is a wrapper around the
redis library providing a simple interface to send and receive messages from a
redis server.
"""

from __future__ import annotations

import collections
import inspect
import queue
import sys
import threading
import time
import warnings
from dataclasses import dataclass
from functools import wraps
from typing import TYPE_CHECKING

import louie
import redis
import redis.client
import redis.exceptions

from bec_lib.connector import ConnectorBase, MessageObject
from bec_lib.endpoints import EndpointInfo, MessageEndpoints
from bec_lib.logger import bec_logger
from bec_lib.messages import AlarmMessage, BECMessage, LogMessage
from bec_lib.serialization import MsgpackSerialization

if TYPE_CHECKING:
    from bec_lib.alarm_handler import Alarms


def validate_endpoint(endpoint_arg):
    def decorator(func):
        argspec = inspect.getfullargspec(func)
        argument_index = argspec.args.index(endpoint_arg)

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                endpoint = args[argument_index]
                arg = list(args)
            except IndexError:
                endpoint = kwargs[endpoint_arg]
                arg = kwargs
            if isinstance(endpoint, str):
                warnings.warn(
                    "RedisConnector methods with a string topic are deprecated and should not be used anymore. Use RedisConnector methods with an EndpointInfo instead.",
                    DeprecationWarning,
                )
                return func(*args, **kwargs)
            elif isinstance(endpoint, EndpointInfo):
                if func.__name__ not in endpoint.message_op:
                    raise ValueError(
                        f"Endpoint {endpoint} is not compatible with {func.__name__} method"
                    )
                if isinstance(arg, list):
                    arg[argument_index] = endpoint.endpoint
                    return func(*arg, **kwargs)
                else:
                    arg[endpoint_arg] = endpoint.endpoint
                    return func(*args, **arg)
            else:
                raise TypeError(f"Endpoint {endpoint} is not EndpointInfo")

        return wrapper

    return decorator


@dataclass
class StreamTopicInfo:
    topic: str | list[str]
    stream_id: int
    id: str
    newest_only: bool
    from_start: bool
    cb: callable
    kwargs: dict


class StreamRegisterMixin:
    """
    Mixin to add stream registration capabilities to a connector
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stream_topics_cb = collections.defaultdict(list)
        self._stream_events_listener_thread = None
        self._stream_events_dispatcher_thread = None
        self._stream_messages_queue = queue.Queue()
        self._stop_stream_events_listener_thread = threading.Event()
        self._custom_stream_listeners = {}
        self.__stream_counter = 0

    def _stream_counter(self):
        self.__stream_counter += 1
        return self.__stream_counter

    def register_stream(
        self,
        topics: str | list[str] | EndpointInfo | list[EndpointInfo] = None,
        patterns: str | list[str] | EndpointInfo | list[EndpointInfo] = None,
        cb: callable = None,
        from_start: bool = False,
        newest_only: bool = False,
        start_thread: bool = True,
        **kwargs,
    ) -> int:
        """
        Register a callback for a stream topic or pattern

        Args:
            topic (str, optional): Topic. This should be a valid message endpoint in BEC and can be a string or an EndpointInfo object. Defaults to None. Either topic or pattern should be provided.
            pattern (str, optional): Pattern of topics. In contrast to topics, patterns may contain "*" wildcards. The evaluated patterns should be a valid message endpoint in BEC and can be a string or an EndpointInfo object. Defaults to None. Either topic or pattern should be provided.
            cb (callable, optional): callback. Defaults to None.
            from_start (bool, optional): read from start. Defaults to False.
            newest_only (bool, optional): read newest only. Defaults to False.
            start_thread (bool, optional): start the dispatcher thread. Defaults to True.
            **kwargs: additional keyword arguments to be transmitted to the callback

        Returns:
            int: stream id

        Examples:
            >>> def my_callback(msg, **kwargs):
            ...     print(msg)
            ...
            >>> connector.register_stream("test", my_callback)
            >>> connector.register_stream(topic="test", cb=my_callback)
            >>> connector.register_stream(pattern="test:*", cb=my_callback)
            >>> connector.register_stream(pattern="test:*", cb=my_callback, start_thread=False)
            >>> connector.register_stream(pattern="test:*", cb=my_callback, start_thread=False, my_arg="test")
        """

        if topics is None and patterns is None:
            raise ValueError("topics and pattern cannot be both None")

        if newest_only and from_start:
            raise ValueError("newest_only and from_start cannot be both True")

        if not cb:
            raise ValueError("Callback cb cannot be None")

        # make a weakref from the callable, using louie;
        # it can create safe refs for simple functions as well as methods
        cb_ref = louie.saferef.safe_ref(cb)

        if patterns is not None:
            stream_topics = self._convert_endpointinfo_to_str(patterns)
        else:
            stream_topics = self._convert_endpointinfo_to_str(topics)

        if newest_only:
            # if newest_only is True, we need to provide a separate callback for each topic,
            # directly calling the callback. This is because we need to have a backpressure
            # mechanism in place, and we cannot rely on the dispatcher thread to handle it.
            if isinstance(stream_topics, list):
                out = []
                for topic in stream_topics:
                    out.append(self._add_direct_stream_listener(topic, cb_ref, **kwargs))
                return out
            return self._add_direct_stream_listener(stream_topics, cb_ref, **kwargs)

        if self._stream_events_listener_thread is None:
            # create the thread that will get all messages for this connector;
            self._stream_events_listener_thread = threading.Thread(
                target=self._get_stream_messages_loop, daemon=True
            )
            self._stream_events_listener_thread.start()
        if isinstance(stream_topics, list):
            stream_id = []
            for topic in stream_topics:
                stream_id.append(self._stream_counter())
                self._stream_topics_cb[topic].append(
                    StreamTopicInfo(
                        id="0-0",
                        topic=topic,
                        stream_id=stream_id,
                        newest_only=newest_only,
                        from_start=from_start,
                        cb=cb_ref,
                        kwargs=kwargs,
                    )
                )
        else:
            stream_id = self._stream_counter()
            self._stream_topics_cb[stream_topics].append(
                StreamTopicInfo(
                    id="0-0",
                    topic=stream_topics,
                    stream_id=stream_id,
                    newest_only=newest_only,
                    from_start=from_start,
                    cb=cb_ref,
                    kwargs=kwargs,
                )
            )

        if start_thread and self._stream_events_dispatcher_thread is None:
            # start dispatcher thread
            self._stream_events_dispatcher_thread = threading.Thread(
                target=self._dispatch_stream_events, daemon=True
            )
            self._stream_events_dispatcher_thread.start()
        return stream_id

    def unregister_stream(self, stream_id: int) -> bool:
        """
        Unregister a stream listener.

        Args:
            stream_id (int): stream id

        Returns:
            bool: True if the stream listener has been removed, False otherwise
        """

        if stream_id in self._custom_stream_listeners:
            listener = self._custom_stream_listeners.pop(stream_id)
            event = listener["stop_event"]
            thread = listener["thread"]
            event.set()
            thread.join()
            return True
        if stream_id in self._stream_topics_cb:
            self._stream_topics_cb.pop(stream_id)
            return True
        return False

    def _add_direct_stream_listener(self, topic, cb, **kwargs) -> int:
        """
        Add a direct listener for a topic. This is used when newest_only is True.

        Args:
            topic (str): topic
            cb (callable): callback
            kwargs (dict): additional keyword arguments to be transmitted to the callback

        Returns:
            int: stream id
        """
        stream_id = self._stream_counter()
        info = StreamTopicInfo(
            id="0-0",
            topic=topic,
            stream_id=stream_id,
            newest_only=True,
            from_start=False,
            cb=cb,
            kwargs=kwargs,
        )
        event = threading.Event()
        thread = threading.Thread(
            target=self._direct_stream_listener, args=(info, event), daemon=True
        )
        self._custom_stream_listeners[stream_id] = {
            "info": info,
            "thread": thread,
            "stop_event": event,
        }
        thread.start()

        return stream_id

    def _direct_stream_listener(self, info: StreamTopicInfo, stop_event: threading.Event):
        while not stop_event.is_set():
            msg = self.xread(info.topic, count=1, block=1000)
            if not msg:
                time.sleep(0.1)
                continue
            cb = info.cb()
            if not cb:
                return
            try:
                cb(msg[0], **info.kwargs)
            # pylint: disable=broad-except
            except Exception:
                sys.excepthook(*sys.exc_info())

    def _dispatch_stream_events(self):
        while self.poll_stream_messages():
            ...

    def _get_stream_topics(self) -> dict:
        stream_topics = {}
        for topic, subscriber in self._stream_topics_cb.items():
            for info in subscriber:
                stream_topics[topic] = info.id
        return stream_topics

    def _get_stream_messages_loop(self) -> None:
        """
        Get stream messages loop. This method is run in a separate thread and listens
        for messages from the redis server.
        """
        error = False
        while not self._stop_stream_events_listener_thread.is_set():
            try:
                stream_topics = self._get_stream_topics()
                if not stream_topics:
                    continue
                msg = self._redis_conn.xread(streams=stream_topics, block=1000)
                print(stream_topics)

            except redis.exceptions.ConnectionError:
                if not error:
                    error = True
                    bec_logger.logger.error("Failed to connect to redis. Is the server running?")
                time.sleep(1)
            # pylint: disable=broad-except
            except Exception:
                sys.excepthook(*sys.exc_info())
            else:
                error = False
                if msg is not None:
                    self._stream_messages_queue.put(msg)

    def poll_stream_messages(self, timeout=None) -> None:
        """
        Poll for new messages, receive them and execute callbacks

        Args:
            timeout ([type], optional): timeout in seconds. Defaults to None.
        """
        while True:
            try:
                msg = self._stream_messages_queue.get(timeout=timeout)
            except queue.Empty as exc:
                raise TimeoutError(
                    f"{self}: poll_stream_messages: did not receive a message within {timeout} seconds"
                ) from exc
            if msg is StopIteration:
                return False
            if self._handle_stream_message(msg):
                return True

    def _handle_stream_message(self, msg):
        if not msg:
            return False
        for topic, msgs in msg:
            callbacks = self._stream_topics_cb[topic.decode()]
            for index, record in msgs:
                msg_dict = {
                    k.decode(): MsgpackSerialization.loads(msg) for k, msg in record.items()
                }
                for info in callbacks:
                    info.id = index
                    cb = info.cb()
                    if cb:
                        try:
                            cb(msg_dict, **info.kwargs)
                        # pylint: disable=broad-except
                        except Exception:
                            sys.excepthook(*sys.exc_info())
        return True

    def shutdown(self):
        """
        Shutdown the connector
        """
        super().shutdown()
        if self._stream_events_listener_thread:
            self._stop_stream_events_listener_thread.set()
            self._stream_events_listener_thread.join()
            self._stream_events_listener_thread = None
        if self._stream_events_dispatcher_thread:
            self._stream_messages_queue.put(StopIteration)
            self._stream_events_dispatcher_thread.join()
            self._stream_events_dispatcher_thread = None


class RedisConnector(StreamRegisterMixin, ConnectorBase):
    """
    Redis connector class. This class is a wrapper around the redis library providing
    a simple interface to send and receive messages from a redis server.
    """

    def __init__(self, bootstrap: list, redis_cls=None):
        """
        Initialize the connector

        Args:
            bootstrap (list): list of strings in the form "host:port"
            redis_cls (redis.client, optional): redis client class. Defaults to None.
        """
        super().__init__(bootstrap)
        self.host, self.port = (
            bootstrap[0].split(":") if isinstance(bootstrap, list) else bootstrap.split(":")
        )

        if redis_cls:
            self._redis_conn = redis_cls(host=self.host, port=self.port)
        else:
            self._redis_conn = redis.Redis(host=self.host, port=self.port)

        # main pubsub connection
        self._pubsub_conn = self._redis_conn.pubsub()
        self._pubsub_conn.ignore_subscribe_messages = True
        # keep track of topics and callbacks
        self._topics_cb = collections.defaultdict(list)

        self._events_listener_thread = None
        self._events_dispatcher_thread = None
        self._messages_queue = queue.Queue()
        self._stop_events_listener_thread = threading.Event()
        self.stream_keys = {}

    def shutdown(self):
        """
        Shutdown the connector
        """
        super().shutdown()
        if self._events_listener_thread:
            self._stop_events_listener_thread.set()
            self._events_listener_thread.join()
            self._events_listener_thread = None
        if self._events_dispatcher_thread:
            self._messages_queue.put(StopIteration)
            self._events_dispatcher_thread.join()
            self._events_dispatcher_thread = None

        # release all connections
        self._pubsub_conn.close()
        self._redis_conn.close()

    def log_warning(self, msg):
        """
        send a warning

        Args:
            msg (str): warning message
        """
        self.set_and_publish(MessageEndpoints.log(), LogMessage(log_type="warning", log_msg=msg))

    def log_message(self, msg):
        """
        send a message as log

        Args:
            msg (str): message
        """
        self.set_and_publish(MessageEndpoints.log(), LogMessage(log_type="log", log_msg=msg))

    def log_error(self, msg):
        """
        send an error as log

        Args:
            msg (str): error message
        """
        self.set_and_publish(MessageEndpoints.log(), LogMessage(log_type="error", log_msg=msg))

    def raise_alarm(self, severity: Alarms, alarm_type: str, source: str, msg: str, metadata: dict):
        """
        Raise an alarm

        Args:
            severity (Alarms): alarm severity
            alarm_type (str): alarm type
            source (str): source
            msg (str): message
            metadata (dict): metadata
        """
        alarm_msg = AlarmMessage(
            severity=severity, alarm_type=alarm_type, source=source, msg=msg, metadata=metadata
        )
        self.set_and_publish(MessageEndpoints.alarm(), alarm_msg)

    def pipeline(self) -> redis.client.Pipeline:
        """Create a new pipeline"""
        return self._redis_conn.pipeline()

    def execute_pipeline(self, pipeline) -> list:
        """
        Execute a pipeline and return the results

        Args:
            pipeline (Pipeline): redis pipeline

        Returns:
            list: list of results
        """
        if not isinstance(pipeline, redis.client.Pipeline):
            raise TypeError(f"Expected a redis Pipeline, got {type(pipeline)}")
        ret = []
        results = pipeline.execute()
        for res in results:
            try:
                ret.append(MsgpackSerialization.loads(res))
            except RuntimeError:
                ret.append(res)
        return ret

    def raw_send(self, topic: str, msg: bytes, pipe=None):
        """
        Send a message to a topic. This is the raw version of send, it does not
        check the message type. Use this method if you want to send a message
        that is not a BECMessage.

        Args:
            topic (str): topic
            msg (bytes): message
            pipe (Pipeline, optional): redis pipe. Defaults to None.
        """
        client = pipe if pipe is not None else self._redis_conn
        client.publish(topic, msg)

    @validate_endpoint("topic")
    def send(self, topic: EndpointInfo, msg: BECMessage, pipe=None) -> None:
        """
        Send a message to a topic

        Args:
            topic (str): topic
            msg (BECMessage): message
            pipe (Pipeline, optional): redis pipe. Defaults to None.
        """
        if not isinstance(msg, BECMessage):
            raise TypeError(f"Message {msg} is not a BECMessage")
        self.raw_send(topic, MsgpackSerialization.dumps(msg), pipe)

    def register(
        self,
        topics: str | list[str] | EndpointInfo | list[EndpointInfo] = None,
        patterns: str | list[str] | EndpointInfo | list[EndpointInfo] = None,
        cb: callable = None,
        start_thread: bool = True,
        **kwargs,
    ):
        """
        Register a callback for a topic or a pattern

        Args:
            topics (str, list, EndpointInfo, list[EndpointInfo], optional): topic or list of topics. Defaults to None. The topic should be a valid message endpoint in BEC and can be a string or an EndpointInfo object.
            patterns (str, list, optional): pattern or list of patterns. Defaults to None. In contrast to topics, patterns may contain "*" wildcards. The evaluated patterns should be a valid message endpoint in BEC and can be a string or an EndpointInfo object.
            cb (callable, optional): callback. Defaults to None.
            start_thread (bool, optional): start the dispatcher thread. Defaults to True.
            **kwargs: additional keyword arguments to be transmitted to the callback

        Examples:
            >>> def my_callback(msg, **kwargs):
            ...     print(msg)
            ...
            >>> connector.register("test", my_callback)
            >>> connector.register(topics="test", cb=my_callback)
            >>> connector.register(patterns="test:*", cb=my_callback)
            >>> connector.register(patterns="test:*", cb=my_callback, start_thread=False)
            >>> connector.register(patterns="test:*", cb=my_callback, start_thread=False, my_arg="test")
        """
        if self._events_listener_thread is None:
            # create the thread that will get all messages for this connector;
            self._events_listener_thread = threading.Thread(
                target=self._get_messages_loop, args=(self._pubsub_conn,), daemon=True
            )
            self._events_listener_thread.start()

        if cb is None:
            raise ValueError("Callback cb cannot be None")
        # make a weakref from the callable, using louie;
        # it can create safe refs for simple functions as well as methods
        cb_ref = louie.saferef.safe_ref(cb)

        if topics is None and patterns is None:
            raise ValueError("topics and patterns cannot be both None")

        if patterns is not None:
            patterns = self._convert_endpointinfo_to_str(patterns)
            if not isinstance(patterns, list):
                patterns = [patterns]

            self._pubsub_conn.psubscribe(patterns)
            for pattern in patterns:
                self._topics_cb[pattern].append((cb_ref, kwargs))
        else:
            topics = self._convert_endpointinfo_to_str(topics)
            if not isinstance(topics, list):
                topics = [topics]

            self._pubsub_conn.subscribe(topics)
            for topic in topics:
                self._topics_cb[topic].append((cb_ref, kwargs))

        if start_thread and self._events_dispatcher_thread is None:
            # start dispatcher thread
            self._events_dispatcher_thread = threading.Thread(
                target=self._dispatch_events, daemon=True
            )
            self._events_dispatcher_thread.start()

    def _convert_endpointinfo_to_str(self, endpoint):
        if isinstance(endpoint, EndpointInfo):
            return endpoint.endpoint
        if isinstance(endpoint, str):
            return endpoint
        if isinstance(endpoint, list):
            return [self._convert_endpointinfo_to_str(e) for e in endpoint]
        raise ValueError(f"Invalid endpoint {endpoint}")

    def _get_messages_loop(self, pubsub: redis.client.PubSub) -> None:
        """
        Get messages loop. This method is run in a separate thread and listens
        for messages from the redis server.

        Args:
            pubsub (redis.client.PubSub): pubsub object
        """
        error = False
        while not self._stop_events_listener_thread.is_set():
            try:
                msg = pubsub.get_message(timeout=1)
            except redis.exceptions.ConnectionError:
                if not error:
                    error = True
                    bec_logger.logger.error("Failed to connect to redis. Is the server running?")
                time.sleep(1)
            # pylint: disable=broad-except
            except Exception:
                sys.excepthook(*sys.exc_info())
            else:
                error = False
                if msg is not None:
                    self._messages_queue.put(msg)

    def _handle_message(self, msg):
        if msg["type"].endswith("subscribe"):
            # ignore subscribe messages
            return False
        channel = msg["channel"].decode()
        if msg["pattern"] is not None:
            callbacks = self._topics_cb[msg["pattern"].decode()]
        else:
            callbacks = self._topics_cb[channel]
        msg = MessageObject(topic=channel, value=MsgpackSerialization.loads(msg["data"]))
        for cb_ref, kwargs in callbacks:
            cb = cb_ref()
            if cb:
                try:
                    cb(msg, **kwargs)
                # pylint: disable=broad-except
                except Exception:
                    sys.excepthook(*sys.exc_info())
        return True

    def poll_messages(self, timeout=None) -> None:
        while True:
            try:
                msg = self._messages_queue.get(timeout=timeout)
            except queue.Empty as exc:
                raise TimeoutError(
                    f"{self}: poll_messages: did not receive a message within {timeout} seconds"
                ) from exc
            if msg is StopIteration:
                return False
            if self._handle_message(msg):
                return True

    def _dispatch_events(self):
        while self.poll_messages():
            ...

    @validate_endpoint("topic")
    def lpush(
        self, topic: EndpointInfo, msg: str, pipe=None, max_size: int = None, expire: int = None
    ) -> None:
        """Time complexity: O(1) for each element added, so O(N) to
        add N elements when the command is called with multiple arguments.
        Insert all the specified values at the head of the list stored at key.
        If key does not exist, it is created as empty list before
        performing the push operations. When key holds a value that
        is not a list, an error is returned."""
        client = pipe if pipe is not None else self.pipeline()
        if isinstance(msg, BECMessage):
            msg = MsgpackSerialization.dumps(msg)
        client.lpush(topic, msg)
        if max_size:
            client.ltrim(topic, 0, max_size)
        if expire:
            client.expire(topic, expire)
        if not pipe:
            client.execute()

    @validate_endpoint("topic")
    def lset(self, topic: EndpointInfo, index: int, msg: str, pipe=None) -> None:
        client = pipe if pipe is not None else self._redis_conn
        if isinstance(msg, BECMessage):
            msg = MsgpackSerialization.dumps(msg)
        return client.lset(topic, index, msg)

    @validate_endpoint("topic")
    def rpush(self, topic: EndpointInfo, msg: str, pipe=None) -> int:
        """O(1) for each element added, so O(N) to add N elements when the
        command is called with multiple arguments. Insert all the specified
        values at the tail of the list stored at key. If key does not exist,
        it is created as empty list before performing the push operation. When
        key holds a value that is not a list, an error is returned."""
        client = pipe if pipe is not None else self._redis_conn
        if isinstance(msg, BECMessage):
            msg = MsgpackSerialization.dumps(msg)
        return client.rpush(topic, msg)

    @validate_endpoint("topic")
    def lrange(self, topic: EndpointInfo, start: int, end: int, pipe=None):
        """O(S+N) where S is the distance of start offset from HEAD for small
        lists, from nearest end (HEAD or TAIL) for large lists; and N is the
        number of elements in the specified range. Returns the specified elements
        of the list stored at key. The offsets start and stop are zero-based indexes,
        with 0 being the first element of the list (the head of the list), 1 being
        the next element and so on."""
        client = pipe if pipe is not None else self._redis_conn
        cmd_result = client.lrange(topic, start, end)
        if pipe:
            return cmd_result

        # in case of command executed in a pipe, use 'execute_pipeline' method
        ret = []
        for msg in cmd_result:
            try:
                ret.append(MsgpackSerialization.loads(msg))
            except RuntimeError:
                ret.append(msg)
        return ret

    @validate_endpoint("topic")
    def set_and_publish(self, topic: EndpointInfo, msg, pipe=None, expire: int = None) -> None:
        """piped combination of self.publish and self.set"""
        client = pipe if pipe is not None else self.pipeline()
        if not isinstance(msg, BECMessage):
            raise TypeError(f"Message {msg} is not a BECMessage")
        msg = MsgpackSerialization.dumps(msg)
        self.set(topic, msg, pipe=client, expire=expire)
        self.raw_send(topic, msg, pipe=client)
        if not pipe:
            client.execute()

    @validate_endpoint("topic")
    def set(self, topic: EndpointInfo, msg, pipe=None, expire: int = None) -> None:
        """set redis value"""
        client = pipe if pipe is not None else self._redis_conn
        if isinstance(msg, BECMessage):
            msg = MsgpackSerialization.dumps(msg)
        client.set(topic, msg, ex=expire)

    @validate_endpoint("pattern")
    def keys(self, pattern: EndpointInfo) -> list:
        """returns all keys matching a pattern"""
        return self._redis_conn.keys(pattern)

    @validate_endpoint("topic")
    def delete(self, topic: EndpointInfo, pipe=None):
        """delete topic"""
        client = pipe if pipe is not None else self._redis_conn
        client.delete(topic)

    @validate_endpoint("topic")
    def get(self, topic: EndpointInfo, pipe=None):
        """retrieve entry, either via hgetall or get"""
        client = pipe if pipe is not None else self._redis_conn
        data = client.get(topic)
        if pipe:
            return data
        else:
            try:
                return MsgpackSerialization.loads(data)
            except RuntimeError:
                return data

    @validate_endpoint("topic")
    def xadd(
        self, topic: EndpointInfo, msg_dict: dict, max_size=None, pipe=None, expire: int = None
    ):
        """
        add to stream

        Args:
            topic (str): redis topic
            msg_dict (dict): message to add
            max_size (int, optional): max size of stream. Defaults to None.
            pipe (Pipeline, optional): redis pipe. Defaults to None.
            expire (int, optional): expire time. Defaults to None.

        Examples:
            >>> redis.xadd("test", {"test": "test"})
            >>> redis.xadd("test", {"test": "test"}, max_size=10)
        """
        if pipe:
            client = pipe
        elif expire:
            client = self.pipeline()
        else:
            client = self._redis_conn

        msg_dict = {key: MsgpackSerialization.dumps(val) for key, val in msg_dict.items()}

        if max_size:
            client.xadd(topic, msg_dict, maxlen=max_size)
        else:
            client.xadd(topic, msg_dict)
        if expire:
            client.expire(topic, expire)
        if not pipe and expire:
            client.execute()

    @validate_endpoint("topic")
    def get_last(self, topic: EndpointInfo, key=None, count=1):
        """
        Get last message from stream. Repeated calls will return
        the same message until a new message is added to the stream.

        Args:
            topic (str): redis topic
            key (str, optional): key to retrieve. Defaults to None. If None, the whole message is returned.
            count (int, optional): number of last elements to retrieve
        """
        if count <= 0:
            return None
        ret = []
        client = self._redis_conn
        try:
            res = client.xrevrange(topic, "+", "-", count=count)
            if not res:
                return None
            for _, msg_dict in reversed(res):
                ret.append(
                    {k.decode(): MsgpackSerialization.loads(msg) for k, msg in msg_dict.items()}
                    if key is None
                    else MsgpackSerialization.loads(msg_dict[key.encode()])
                )
        except TypeError:
            return None

        if count > 1:
            return ret
        else:
            return ret[0]

    @validate_endpoint("topic")
    def xread(
        self,
        topic: EndpointInfo,
        id: str = None,
        count: int = None,
        block: int = None,
        from_start=False,
    ) -> list:
        """
        read from stream

        Args:
            topic (str): redis topic
            id (str, optional): id to read from. Defaults to None.
            count (int, optional): number of messages to read. Defaults to None, which means all.
            block (int, optional): block for x milliseconds. Defaults to None.
            from_start (bool, optional): read from start. Defaults to False.

        Returns:
            [list]: list of messages

        Examples:
            >>> redis.xread("test", "0-0")
            >>> redis.xread("test", "0-0", count=1)

            # read one message at a time
            >>> key = 0
            >>> msg = redis.xread("test", key, count=1)
            >>> key = msg[0][1][0][0]
            >>> next_msg = redis.xread("test", key, count=1)
        """
        client = self._redis_conn
        if from_start:
            self.stream_keys[topic] = "0-0"
        if topic not in self.stream_keys:
            if id is None:
                try:
                    msg = client.xrevrange(topic, "+", "-", count=1)
                    if msg:
                        self.stream_keys[topic] = msg[0][0].decode()
                        out = {}
                        for key, val in msg[0][1].items():
                            out[key.decode()] = MsgpackSerialization.loads(val)
                        return [out]
                    self.stream_keys[topic] = "0-0"
                except redis.exceptions.ResponseError:
                    self.stream_keys[topic] = "0-0"
        if id is None:
            id = self.stream_keys[topic]

        msg = client.xread({topic: id}, count=count, block=block)
        return self._decode_stream_messages_xread(msg)

    def _decode_stream_messages_xread(self, msg):
        out = []
        for topic, msgs in msg:
            for index, record in msgs:
                out.append(
                    {k.decode(): MsgpackSerialization.loads(msg) for k, msg in record.items()}
                )
                self.stream_keys[topic.decode()] = index
        return out if out else None

    @validate_endpoint("topic")
    def xrange(self, topic: EndpointInfo, min: str, max: str, count: int = None):
        """
        read a range from stream

        Args:
            topic (str): redis topic
            min (str): min id. Use "-" to read from start
            max (str): max id. Use "+" to read to end
            count (int, optional): number of messages to read. Defaults to None.

        Returns:
            [list]: list of messages or None
        """
        client = self._redis_conn
        msgs = []
        for reading in client.xrange(topic, min, max, count=count):
            _, msg_dict = reading
            msgs.append(
                {k.decode(): MsgpackSerialization.loads(msg) for k, msg in msg_dict.items()}
            )
        return msgs if msgs else None

    def producer(self):
        """Return itself as a producer, to be compatible with old code"""
        warnings.warn(
            "RedisConnector.producer() is deprecated and should not be used anymore. A Connector is a producer now, just use the connector object.",
            FutureWarning,
        )
        return self

    def consumer(
        self,
        topics=None,
        patterns=None,
        group_id=None,
        event=None,
        cb=None,
        threaded=True,
        name=None,
        **kwargs,
    ):
        """Return a fake thread object to be compatible with old code

        In order to keep this fail-safe and simple it uses 'mock'...
        """
        from unittest.mock import (  # import is done here, to not pollute the file with something normally in tests
            Mock,
        )

        warnings.warn(
            "RedisConnector.consumer() is deprecated and should not be used anymore. Use RedisConnector.register() with 'topics', 'patterns', 'cb' or 'start_thread' instead. Additional keyword args are transmitted to the callback. For the caller, the main difference with RedisConnector.register() is that it does not return a new thread.",
            FutureWarning,
        )
        dummy_thread = Mock(spec=threading.Thread)
        dummy_thread.start.side_effet = lambda: self.register(
            topics, patterns, cb, threaded, **kwargs
        )
        return dummy_thread
