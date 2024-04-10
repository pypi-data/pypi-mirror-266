"""
This module contains the BECLogger class, which is a wrapper around the loguru logger. It is used to
configure and manage the logging of the BEC.
"""

from __future__ import annotations

import enum
import json
import os
import sys
from typing import TYPE_CHECKING

from loguru import logger as loguru_logger

# TODO: Importing bec_lib, instead of `from bec_lib.messages import LogMessage`, avoids potential
# logger <-> messages circular import. But there could be a better solution.
import bec_lib
from bec_lib.endpoints import MessageEndpoints
from bec_lib.file_utils import LogWriter

if TYPE_CHECKING:
    from bec_lib.connector import ConnectorBase


class LogLevel(int, enum.Enum):
    """Mapping of Loguru log levels to BEC log levels."""

    TRACE = 5
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    CONSOLE_LOG = 21


class BECLogger:
    """Logger for BEC."""

    DEBUG_FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> |"
        " <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> -"
        " <level>{message}</level>"
    )
    LOG_FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>[{level}]</level> |"
        " <level>{message}</level>"
    )
    LOGLEVEL = LogLevel

    def __init__(self) -> None:
        if hasattr(self, "_configured"):
            return
        self.bootstrap_server = None
        self.connector = None
        self.service_name = None
        self.writer_mixin = None
        self._base_path = None
        self.logger = loguru_logger
        self._log_level = LogLevel.INFO
        self.level = self._log_level
        self._configured = False
        self.logger.level("CONSOLE_LOG", no=21, color="<yellow>", icon="📣")

    def __new__(cls):
        if not hasattr(cls, "_logger"):
            cls._logger = super(BECLogger, cls).__new__(cls)
            cls._initialized = False
        return cls._logger

    def configure(
        self,
        bootstrap_server: list,
        connector_cls: ConnectorBase,
        service_name: str,
        service_config: dict = None,
    ) -> None:
        """
        Configure the logger.

        Args:
            bootstrap_server (list): List of bootstrap servers.
            connector_cls (ConnectorBase): Connector class.
            service_name (str): Name of the service to which the logger belongs.
        """
        if not self._base_path:
            self._update_base_path(service_config)
        if os.path.exists(self._base_path) is False:
            self.writer_mixin.create_directory(self._base_path)
        self.bootstrap_server = bootstrap_server
        self.connector = connector_cls(bootstrap_server)
        self.service_name = service_name
        self._configured = True
        self._update_sinks()

    def _update_base_path(self, service_config: dict = None):
        """
        Compile the log base path.
        """
        # pylint: disable=import-outside-toplevel
        if service_config:
            service_cfg = service_config["log_writer"]
        else:
            service_cfg = {"base_path": "./"}
        self.writer_mixin = LogWriter(service_cfg)
        self._base_path = self.writer_mixin.directory
        self.writer_mixin.create_directory(self._base_path)

    def _logger_callback(self, msg):
        if not self._configured:
            return
        msg = json.loads(msg)
        msg["service_name"] = self.service_name
        try:
            self.connector.send(
                topic=MessageEndpoints.log(),
                msg=bec_lib.messages.LogMessage(
                    log_type=msg["record"]["level"]["name"], log_msg=msg
                ),
            )
        except Exception:
            # connector disconnected?
            # just ignore the error here...
            # Exception is not explicitely specified,
            # because it depends on the connector
            pass

    def format(self, level: LogLevel = None) -> str:
        """
        Get the format for a specific log level.

        Args:
            level (LogLevel, optional): Log level. Defaults to None. If None, the current log level will be used.

        Returns:
            str: Log format.
        """
        if level is None:
            level = self.level
        if level > self.LOGLEVEL.DEBUG:
            return self.LOG_FORMAT

        return self.DEBUG_FORMAT

    def _update_sinks(self):
        self.logger.remove()
        self.add_console_log()
        self.add_redis_log(self._log_level)
        self.add_sys_stderr(self._log_level)
        self.add_file_log(self._log_level)

    def add_sys_stderr(self, level: LogLevel):
        """
        Add a sink to stderr.

        Args:
            level (LogLevel): Log level.
        """
        self.logger.add(sys.stderr, level=level, format=self.format(level), enqueue=True)

    def add_file_log(self, level: LogLevel):
        """
        Add a sink to the service log file.

        Args:
            level (LogLevel): Log level.
        """
        if not self.service_name:
            return
        filename = os.path.join(self._base_path, f"{self.service_name}.log")
        self.logger.add(filename, level=level, format=self.format(level), enqueue=True)

    def add_console_log(self):
        """
        Add a sink to the console log.
        """
        if not self.service_name:
            return
        filename = os.path.join(self._base_path, f"{self.service_name}_CONSOLE.log")
        self.logger.add(
            filename,
            level=LogLevel.CONSOLE_LOG,
            format=self.format(LogLevel.CONSOLE_LOG),
            filter=lambda record: record["level"].no == LogLevel.CONSOLE_LOG,
            enqueue=True,
        )

    def add_redis_log(self, level: LogLevel):
        """
        Add a sink to the redis log.

        Args:
            level (LogLevel): Log level.
        """
        self.logger.add(self._logger_callback, serialize=True, level=level)

    @property
    def level(self):
        """
        Get the current log level.
        """
        return self._log_level

    @level.setter
    def level(self, val: LogLevel):
        self._log_level = val
        self._update_sinks()


bec_logger = BECLogger()
