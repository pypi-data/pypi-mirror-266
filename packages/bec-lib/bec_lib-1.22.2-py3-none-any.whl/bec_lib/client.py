"""
BECClient class. This class is the main entry point for the BEC client and all 
derived classes. It is used to initialize the client and start the client.
"""

from __future__ import annotations, print_function

import builtins
import getpass
import importlib
import inspect
from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

from bec_lib import messages
from bec_lib.alarm_handler import AlarmHandler, Alarms
from bec_lib.bec_service import BECService
from bec_lib.bl_checks import BeamlineChecks
from bec_lib.callback_handler import CallbackHandler
from bec_lib.dap_plugins import DAPPlugins
from bec_lib.devicemanager import DeviceManagerBase
from bec_lib.endpoints import MessageEndpoints
from bec_lib.logger import bec_logger
from bec_lib.redis_connector import RedisConnector
from bec_lib.scan_manager import ScanManager
from bec_lib.scans import Scans
from bec_lib.service_config import ServiceConfig
from bec_lib.user_scripts_mixin import UserScriptsMixin

if TYPE_CHECKING:
    from bec_lib.connector import ConnectorBase

logger = bec_logger.logger


class BECClient(BECService, UserScriptsMixin):
    """
    The BECClient class is the main entry point for the BEC client and all derived classes.
    """

    _client = None
    _initialized = False
    started = False

    def __init__(
        self,
        config: ServiceConfig = None,
        connector_cls: ConnectorBase = None,
        wait_for_server=False,
        forced=False,
        parent=None,
    ) -> None:
        """
        Initialize the BECClient

        Args:
            config (ServiceConfig, optional): The configuration for the client. Defaults to None.
            connector_cls (ConnectorBase, optional): The connector class to use. Defaults to None.
            wait_for_server (bool, optional): Whether to wait for the server to be available before starting. Defaults to False.
            forced (bool, optional): Whether to force the initialization of a new client. Defaults to False.
        """
        if self._initialized:
            return
        self.__init_params = {
            "config": config if config is not None else ServiceConfig(),
            "connector_cls": connector_cls if connector_cls is not None else RedisConnector,
            "wait_for_server": wait_for_server,
        }
        self.device_manager = None
        self.queue = None
        self.alarm_handler = None
        self.config = None
        self.history = None
        self.live_updates = None
        self.dap = None
        self.bl_checks = None
        self._hli_funcs = {}
        self.metadata = {}
        self.callbacks = None
        self._parent = parent if parent is not None else self
        self._initialized = True

    def __new__(cls, *args, forced=False, **kwargs):
        if forced or cls._client is None:
            cls._client = super(BECClient, cls).__new__(cls)
            cls._initialized = False
        return cls._client

    def __str__(self) -> str:
        return "BECClient\n\nTo get a list of available commands, type `bec.show_all_commands()`"

    @classmethod
    def _reset_singleton(cls):
        cls._client = None
        cls._initialized = False
        cls.started = False

    @property
    def username(self) -> str:
        """get the current username"""
        return self._username

    @property
    def active_account(self) -> str:
        """get the currently active target (e)account"""
        msg = self.connector.get(MessageEndpoints.account())
        if msg:
            return msg.value
        return ""

    def start(self):
        """start the client"""
        if self.started:
            return
        self.started = True
        config = self.__init_params["config"]
        connector_cls = self.__init_params["connector_cls"]
        wait_for_server = self.__init_params["wait_for_server"]
        super().__init__(config, connector_cls, wait_for_server=wait_for_server)
        builtins.bec = self._parent
        self._start_services()
        logger.info("Starting new client")

    def _start_services(self):
        self._configure_logger()
        self._load_scans()
        # self.logbook = LogbookConnector(self.connector)
        self._update_username()
        self.callbacks = CallbackHandler()
        self._start_device_manager()
        self._start_scan_queue()
        self._start_alarm_handler()
        self.load_all_user_scripts()
        self.config = self.device_manager.config_helper
        self.history = self.queue.queue_storage.storage
        self.dap = DAPPlugins(self)
        self.bl_checks = BeamlineChecks(self)
        self.bl_checks.start()

    def alarms(self, severity=Alarms.WARNING):
        """get the next alarm with at least the specified severity"""
        if self.alarm_handler is None:
            yield []
        yield from self.alarm_handler.get_alarm(severity=severity)

    def show_all_alarms(self, severity=Alarms.WARNING):
        """print all unhandled alarms"""
        alarms = self.alarm_handler.get_unhandled_alarms(severity=severity)
        for alarm in alarms:
            print(alarm)

    def clear_all_alarms(self):
        """remove all alarms from stack"""
        self.alarm_handler.clear()

    @property
    def pre_scan_macros(self):
        """currently stored pre-scan macros"""
        return self.connector.lrange(MessageEndpoints.pre_scan_macros(), 0, -1)

    @pre_scan_macros.setter
    def pre_scan_macros(self, hooks: list[str]):
        self.connector.delete(MessageEndpoints.pre_scan_macros())
        for hook in hooks:
            msg = messages.VariableMessage(value=hook)
            self.connector.lpush(MessageEndpoints.pre_scan_macros(), msg)

    def _load_scans(self):
        self.scans = Scans(self._parent)
        builtins.scans = self.scans

    def load_high_level_interface(self, module_name):
        mod = importlib.import_module(f"bec_client.high_level_interfaces.{module_name}")
        members = inspect.getmembers(mod)
        funcs = {name: func for name, func in members if not name.startswith("__")}
        self._hli_funcs = funcs
        builtins.__dict__.update(funcs)

    def _update_username(self):
        self._username = getpass.getuser()

    def _start_scan_queue(self):
        self.queue = ScanManager(self.connector)

    def _configure_logger(self):
        bec_logger.logger.remove()
        bec_logger.add_file_log(bec_logger.LOGLEVEL.DEBUG)
        bec_logger.add_sys_stderr(bec_logger.LOGLEVEL.SUCCESS)
        bec_logger.add_console_log()

    def _start_device_manager(self):
        logger.info("Starting device manager")
        self.device_manager = DeviceManagerBase(self)
        self.device_manager.initialize(self.bootstrap_server)
        builtins.dev = self.device_manager.devices

    def _start_alarm_handler(self):
        logger.info("Starting alarm listener")
        self.alarm_handler = AlarmHandler(self.connector)
        self.alarm_handler.start()

    def shutdown(self):
        """shutdown the client and all its components"""
        if self.started:
            super().shutdown()
        if self.device_manager:
            self.device_manager.shutdown()
        if self.queue:
            self.queue.shutdown()
        if self.alarm_handler:
            self.alarm_handler.shutdown()
        if self.bl_checks:
            self.bl_checks.stop()
        bec_logger.logger.remove()
        self.started = False

    def _print_available_commands(self, title: str, data: tuple) -> None:
        console = Console()
        table = Table(title=title)
        table.add_column("Name", justify="center")
        table.add_column("Description", justify="center")
        for name, descr in data:
            table.add_row(name, descr)
        console.print(table)

    def _print_user_script_commands(self) -> None:
        data = self._get_user_script_commands()
        self._print_available_commands("User scripts", data)

    def _get_user_script_commands(self) -> list:
        avail_commands = []
        for name, val in self._scripts.items():
            descr = self._get_description_from_doc_string(val["cls"].__doc__)
            avail_commands.append((name, descr))
        return avail_commands

    def _get_scan_commands(self) -> list:
        avail_commands = []
        for name, scan in self.scans._available_scans.items():
            descr = self._get_description_from_doc_string(scan.scan_info["doc"])
            avail_commands.append((name, descr))
        return avail_commands

    def _print_scan_commands(self) -> None:
        data = self._get_scan_commands()
        self._print_available_commands("Scans", data)

    def show_all_commands(self):
        self._print_user_script_commands()
        self._print_scan_commands()

    @staticmethod
    def _get_description_from_doc_string(doc_string: str) -> str:
        if not doc_string:
            return ""
        return doc_string.strip().split("\n")[0]
