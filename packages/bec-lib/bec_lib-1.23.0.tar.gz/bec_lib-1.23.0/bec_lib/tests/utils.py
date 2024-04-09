from __future__ import annotations

import builtins
import functools
import os
import time
import uuid
from typing import TYPE_CHECKING

import yaml

import bec_lib
from bec_lib import BECClient, messages
from bec_lib.connector import ConnectorBase
from bec_lib.devicemanager import DeviceManagerBase
from bec_lib.endpoints import EndpointInfo, MessageEndpoints
from bec_lib.logger import bec_logger
from bec_lib.scans import Scans

if TYPE_CHECKING:
    from bec_lib.alarm_handler import Alarms

dir_path = os.path.dirname(bec_lib.__file__)

logger = bec_logger.logger

# pylint: disable=no-member
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access


def queue_is_empty(queue) -> bool:  # pragma: no cover
    if not queue:
        return True
    if not queue["primary"].get("info"):
        return True
    return False


def get_queue(bec):  # pragma: no cover
    return bec.queue.connector.get(MessageEndpoints.scan_queue_status())


def wait_for_empty_queue(bec):  # pragma: no cover
    while not get_queue(bec):
        time.sleep(1)
    while not queue_is_empty(get_queue(bec).content["queue"]):
        time.sleep(1)
        logger.info(bec.queue)
    while get_queue(bec).content["queue"]["primary"]["status"] != "RUNNING":
        time.sleep(1)
        logger.info(bec.queue)


class ScansMock(Scans):
    def _import_scans(self):
        pass

    def open_scan_def(self):
        pass

    def close_scan_def(self):
        pass

    def close_scan_group(self):
        pass

    def umv(self):
        pass


class ClientMock(BECClient):
    def _load_scans(self):
        self.scans = ScansMock(self)
        builtins.scans = self.scans

    # def _start_services(self):
    #     pass

    def _start_metrics_emitter(self):
        pass

    def _start_update_service_info(self):
        pass


def get_device_info_mock(device_name, device_class) -> messages.DeviceInfoMessage:
    device_info = {
        "samx": messages.DeviceInfoMessage(
            device="samx",
            info={
                "device_info": {
                    "device_base_class": "positioner",
                    "signals": [
                        {
                            "component_name": "readback",
                            "obj_name": device_name,
                            "kind_int": 5,
                            "kind_str": "Kind.hinted",
                        },
                        {
                            "component_name": "setpoint",
                            "obj_name": f"{device_name}_setpoint",
                            "kind_int": 1,
                            "kind_str": "Kind.normal",
                        },
                        {
                            "component_name": "motor_is_moving",
                            "obj_name": f"{device_name}_motor_is_moving",
                            "kind_int": 1,
                            "kind_str": "Kind.normal",
                        },
                        {
                            "component_name": "readback",
                            "obj_name": device_name,
                            "kind_int": 5,
                            "kind_str": "Kind.hinted",
                        },
                        {
                            "component_name": "velocity",
                            "obj_name": f"{device_name}_velocity",
                            "kind_int": 2,
                            "kind_str": "Kind.config",
                        },
                        {
                            "component_name": "acceleration",
                            "obj_name": f"{device_name}_acceleration",
                            "kind_int": 2,
                            "kind_str": "Kind.config",
                        },
                        {
                            "component_name": "high_limit_travel",
                            "obj_name": f"{device_name}_high_limit_travel",
                            "kind_int": 2,
                            "kind_str": "Kind.config",
                        },
                        {
                            "component_name": "low_limit_travel",
                            "obj_name": f"{device_name}_low_limit_travel",
                            "kind_int": 2,
                            "kind_str": "Kind.config",
                        },
                        {
                            "component_name": "unused",
                            "obj_name": f"{device_name}_unused",
                            "kind_int": 0,
                            "kind_str": "Kind.omitted",
                        },
                    ],
                    "hints": {"fields": ["samx"]},
                    "describe": {
                        "samx": {
                            "source": "SIM:samx",
                            "dtype": "integer",
                            "shape": [],
                            "precision": 3,
                        },
                        "samx_setpoint": {
                            "source": "SIM:samx_setpoint",
                            "dtype": "integer",
                            "shape": [],
                            "precision": 3,
                        },
                        "samx_motor_is_moving": {
                            "source": "SIM:samx_motor_is_moving",
                            "dtype": "integer",
                            "shape": [],
                            "precision": 3,
                        },
                    },
                    "describe_configuration": {
                        "samx_velocity": {
                            "source": "SIM:samx_velocity",
                            "dtype": "integer",
                            "shape": [],
                        },
                        "samx_acceleration": {
                            "source": "SIM:samx_acceleration",
                            "dtype": "integer",
                            "shape": [],
                        },
                    },
                    "sub_devices": [],
                    "custom_user_access": {
                        "dummy_controller": {
                            "_func_with_args": {"type": "func", "doc": None},
                            "_func_with_args_and_kwargs": {"type": "func", "doc": None},
                            "_func_with_kwargs": {"type": "func", "doc": None},
                            "_func_without_args_kwargs": {"type": "func", "doc": None},
                            "controller_show_all": {
                                "type": "func",
                                "doc": (
                                    "dummy controller show all\n\n        Raises:\n           "
                                    " in: _description_\n            LimitError:"
                                    " _description_\n\n        Returns:\n            _type_:"
                                    " _description_\n        "
                                ),
                            },
                            "some_var": {"type": "int"},
                        },
                        "sim_state": {"type": "dict"},
                        "speed": {"type": "int"},
                    },
                }
            },
        ),
        "dyn_signals": messages.DeviceInfoMessage(
            device="dyn_signals",
            info={
                "device_info": {
                    "device_dotted_name": "dyn_signals",
                    "device_attr_name": "dyn_signals",
                    "device_base_class": "device",
                    "signals": [],
                    "hints": {"fields": []},
                    "describe": {
                        "dyn_signals_messages_message1": {
                            "source": "SIM:dyn_signals_messages_message1",
                            "dtype": "integer",
                            "shape": [],
                            "precision": 3,
                        },
                        "dyn_signals_messages_message2": {
                            "source": "SIM:dyn_signals_messages_message2",
                            "dtype": "integer",
                            "shape": [],
                            "precision": 3,
                        },
                        "dyn_signals_messages_message3": {
                            "source": "SIM:dyn_signals_messages_message3",
                            "dtype": "integer",
                            "shape": [],
                            "precision": 3,
                        },
                        "dyn_signals_messages_message4": {
                            "source": "SIM:dyn_signals_messages_message4",
                            "dtype": "integer",
                            "shape": [],
                            "precision": 3,
                        },
                        "dyn_signals_messages_message5": {
                            "source": "SIM:dyn_signals_messages_message5",
                            "dtype": "integer",
                            "shape": [],
                            "precision": 3,
                        },
                    },
                    "describe_configuration": {},
                    "sub_devices": [
                        {
                            "device_name": "dyn_signals_messages",
                            "device_info": {
                                "device_attr_name": "messages",
                                "device_dotted_name": "messages",
                                "device_base_class": "device",
                                "signals": [
                                    {
                                        "component_name": "message1",
                                        "obj_name": "dyn_signals_messages_message1",
                                        "kind_int": 1,
                                        "kind_str": "Kind.normal",
                                    },
                                    {
                                        "component_name": "message2",
                                        "obj_name": "dyn_signals_messages_message2",
                                        "kind_int": 1,
                                        "kind_str": "Kind.normal",
                                    },
                                    {
                                        "component_name": "message3",
                                        "obj_name": "dyn_signals_messages_message3",
                                        "kind_int": 1,
                                        "kind_str": "Kind.normal",
                                    },
                                    {
                                        "component_name": "message4",
                                        "obj_name": "dyn_signals_messages_message4",
                                        "kind_int": 1,
                                        "kind_str": "Kind.normal",
                                    },
                                    {
                                        "component_name": "message5",
                                        "obj_name": "dyn_signals_messages_message5",
                                        "kind_int": 1,
                                        "kind_str": "Kind.normal",
                                    },
                                ],
                                "hints": {"fields": []},
                                "describe": {
                                    "dyn_signals_messages_message1": {
                                        "source": "SIM:dyn_signals_messages_message1",
                                        "dtype": "integer",
                                        "shape": [],
                                        "precision": 3,
                                    },
                                    "dyn_signals_messages_message2": {
                                        "source": "SIM:dyn_signals_messages_message2",
                                        "dtype": "integer",
                                        "shape": [],
                                        "precision": 3,
                                    },
                                    "dyn_signals_messages_message3": {
                                        "source": "SIM:dyn_signals_messages_message3",
                                        "dtype": "integer",
                                        "shape": [],
                                        "precision": 3,
                                    },
                                    "dyn_signals_messages_message4": {
                                        "source": "SIM:dyn_signals_messages_message4",
                                        "dtype": "integer",
                                        "shape": [],
                                        "precision": 3,
                                    },
                                    "dyn_signals_messages_message5": {
                                        "source": "SIM:dyn_signals_messages_message5",
                                        "dtype": "integer",
                                        "shape": [],
                                        "precision": 3,
                                    },
                                },
                                "describe_configuration": {},
                                "sub_devices": [],
                                "custom_user_access": {},
                            },
                        }
                    ],
                    "custom_user_access": {},
                }
            },
        ),
    }
    if device_name in device_info:
        return device_info[device_name]

    device_base_class = "positioner" if device_class == "SimPositioner" else "signal"
    if device_base_class == "positioner":
        signals = [
            {
                "component_name": "readback",
                "obj_name": device_name,
                "kind_int": 5,
                "kind_str": "Kind.hinted",
            },
            {
                "component_name": "setpoint",
                "obj_name": f"{device_name}_setpoint",
                "kind_int": 1,
                "kind_str": "Kind.normal",
            },
            {
                "component_name": "motor_is_moving",
                "obj_name": f"{device_name}_motor_is_moving",
                "kind_int": 1,
                "kind_str": "Kind.normal",
            },
            {
                "component_name": "readback",
                "obj_name": device_name,
                "kind_int": 5,
                "kind_str": "Kind.hinted",
            },
            {
                "component_name": "velocity",
                "obj_name": f"{device_name}_velocity",
                "kind_int": 2,
                "kind_str": "Kind.config",
            },
            {
                "component_name": "acceleration",
                "obj_name": f"{device_name}_acceleration",
                "kind_int": 2,
                "kind_str": "Kind.config",
            },
            {
                "component_name": "high_limit_travel",
                "obj_name": f"{device_name}_high_limit_travel",
                "kind_int": 2,
                "kind_str": "Kind.config",
            },
            {
                "component_name": "low_limit_travel",
                "obj_name": f"{device_name}_low_limit_travel",
                "kind_int": 2,
                "kind_str": "Kind.config",
            },
            {
                "component_name": "unused",
                "obj_name": f"{device_name}_unused",
                "kind_int": 0,
                "kind_str": "Kind.omitted",
            },
        ]
    elif device_base_class == "signal":
        signals = [
            {
                "component_name": "readback",
                "obj_name": device_name,
                "kind_int": 5,
                "kind_str": "Kind.hinted",
            },
            {
                "component_name": "velocity",
                "obj_name": f"{device_name}_velocity",
                "kind_int": 2,
                "kind_str": "Kind.config",
            },
            {
                "component_name": "acceleration",
                "obj_name": f"{device_name}_acceleration",
                "kind_int": 2,
                "kind_str": "Kind.config",
            },
            {
                "component_name": "high_limit_travel",
                "obj_name": f"{device_name}_high_limit_travel",
                "kind_int": 2,
                "kind_str": "Kind.config",
            },
            {
                "component_name": "low_limit_travel",
                "obj_name": f"{device_name}_low_limit_travel",
                "kind_int": 2,
                "kind_str": "Kind.config",
            },
            {
                "component_name": "unused",
                "obj_name": f"{device_name}_unused",
                "kind_int": 0,
                "kind_str": "Kind.omitted",
            },
        ]
    dev_info = {
        "device_name": device_name,
        "device_info": {
            "device_dotted_name": device_name,
            "device_attr_name": device_name,
            "device_base_class": device_base_class,
            "signals": signals,
        },
        "custom_user_acces": {},
    }

    return messages.DeviceInfoMessage(device=device_name, info=dev_info, metadata={})


class DMClientMock(DeviceManagerBase):
    def _get_device_info(self, device_name) -> messages.DeviceInfoMessage:
        return get_device_info_mock(device_name, self.get_device(device_name)["deviceClass"])

    def get_device(self, device_name):
        for dev in self._session["devices"]:
            if dev["name"] == device_name:
                return dev


class PipelineMock:  # pragma: no cover
    _pipe_buffer = []
    _connector = None

    def __init__(self, connector) -> None:
        self._connector = connector

    def execute(self):
        if not self._connector.store_data:
            self._pipe_buffer = []
            return []
        res = [
            getattr(self._connector, method)(*args, **kwargs)
            for method, args, kwargs in self._pipe_buffer
        ]
        self._pipe_buffer = []
        return res


class SignalMock:  # pragma: no cover
    def __init__(self) -> None:
        self.is_set = False

    def set(self):
        self.is_set = True


class ConnectorMock(ConnectorBase):  # pragma: no cover
    def __init__(self, bootstrap_server="localhost:0000", store_data=True):
        super().__init__(bootstrap_server)
        self.message_sent = []
        self._get_buffer = {}
        self.store_data = store_data

    def raise_alarm(
        self, severity: Alarms, alarm_type: str, source: str, msg: dict, metadata: dict
    ):
        pass

    def log_error(self, *args, **kwargs):
        pass

    def shutdown(self):
        pass

    def register(self, *args, **kwargs):
        pass

    def keys(self, *args, **kwargs):
        return []

    def set(self, topic, msg, pipe=None, expire: int = None):
        if pipe:
            pipe._pipe_buffer.append(("set", (topic.endpoint, msg), {"expire": expire}))
            return
        self.message_sent.append({"queue": topic, "msg": msg, "expire": expire})

    def raw_send(self, topic, msg, pipe=None):
        if pipe:
            pipe._pipe_buffer.append(("send", (topic.endpoint, msg), {}))
            return
        self.message_sent.append({"queue": topic, "msg": msg})

    def send(self, topic, msg, pipe=None):
        if not isinstance(msg, messages.BECMessage):
            raise TypeError("Message must be a BECMessage")
        return self.raw_send(topic, msg, pipe)

    def set_and_publish(self, topic, msg, pipe=None, expire: int = None):
        if pipe:
            pipe._pipe_buffer.append(("set_and_publish", (topic.endpoint, msg), {"expire": expire}))
            return
        self.message_sent.append({"queue": topic, "msg": msg, "expire": expire})

    def lpush(self, topic, msg, pipe=None, max_size=None):
        if pipe:
            pipe._pipe_buffer.append(("lpush", (topic, msg), {}))
            return

    def rpush(self, topic, msg, pipe=None):
        if pipe:
            pipe._pipe_buffer.append(("rpush", (topic, msg), {}))
            return
        pass

    def lrange(self, topic, start, stop, pipe=None):
        if pipe:
            pipe._pipe_buffer.append(("lrange", (topic, start, stop), {}))
            return
        return []

    def get(self, topic, pipe=None):
        if isinstance(topic, EndpointInfo):
            topic = topic.endpoint
        if pipe:
            pipe._pipe_buffer.append(("get", (topic,), {}))
            return
        val = self._get_buffer.get(topic)
        if isinstance(val, list):
            return val.pop(0)
        self._get_buffer.pop(topic, None)
        return val

    def pipeline(self):
        return PipelineMock(self)

    def delete(self, topic, pipe=None):
        if pipe:
            pipe._pipe_buffer.append(("delete", (topic,), {}))
            return

    def lset(self, topic: str, index: int, msgs: str, pipe=None) -> None:
        if pipe:
            pipe._pipe_buffer.append(("lrange", (topic, index, msgs), {}))
            return

    def producer(self):
        return self

    def execute_pipeline(self, pipeline):
        pipeline.execute()

    def xadd(self, topic, msg_dict, max_size=None, pipe=None, expire: int = None):
        if pipe:
            pipe._pipe_buffer.append(("xadd", (topic, msg_dict), {"expire": expire}))
            return
        pass

    def xread(self, topic, id=None, count=None, block=None, pipe=None, from_start=False):
        if pipe:
            pipe._pipe_buffer.append(
                ("xread", (topic, id, count, block), {"from_start": from_start})
            )
            return
        return []

    def xrange(self, topic, min="-", max="+", pipe=None):
        if pipe:
            pipe._pipe_buffer.append(("xrange", (topic, min, max), {}))
            return
        return []


def create_session_from_config(config: dict) -> dict:
    device_configs = []
    session_id = str(uuid.uuid4())
    for name, conf in config.items():
        dev_conf = {
            "id": str(uuid.uuid4()),
            "accessGroups": "customer",
            "name": name,
            "sessionId": session_id,
            "enabled": conf["enabled"],
            "read_only": conf["readOnly"],
        }
        dev_conf.update(conf)
        device_configs.append(dev_conf)
    session = {"accessGroups": "customer", "devices": device_configs}
    return session


@functools.lru_cache
def load_test_config():
    with open(f"{dir_path}/tests/test_config.yaml", "r", encoding="utf-8") as f:
        return create_session_from_config(yaml.safe_load(f))
