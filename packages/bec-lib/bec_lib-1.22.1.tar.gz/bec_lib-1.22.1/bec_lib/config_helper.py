"""
This module provides a helper class for updating and saving the BEC device configuration.
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import time
import uuid
from typing import TYPE_CHECKING

import yaml

import bec_lib
from bec_lib import messages
from bec_lib.bec_errors import DeviceConfigError
from bec_lib.endpoints import MessageEndpoints
from bec_lib.logger import bec_logger
from bec_lib.messages import DeviceConfigMessage, RequestResponseMessage

if TYPE_CHECKING:
    from bec_lib.redis_connector import RedisConnector

logger = bec_logger.logger


class ConfigHelper:
    def __init__(self, connector: RedisConnector, service_name: str = None) -> None:
        self.connector = connector
        self._service_name = service_name

    def update_session_with_file(self, file_path: str, save_recovery: bool = True) -> None:
        """Update the current session with a yaml file from disk.

        Args:
            file_path (str): Full path to the yaml file.
            save_recovery (bool, optional): Save the current session before updating. Defaults to True.
        """
        if save_recovery:
            time_stamp = f"{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}"
            fname = f"recovery_config_{time_stamp}.yaml"
            success = self._save_config_to_file(fname, raise_on_error=False)
            if success:
                print(f"A recovery config was written to {fname}.")
        config = self._load_config_from_file(file_path)
        self.send_config_request(action="set", config=config)

    def _load_config_from_file(self, file_path: str) -> dict:
        data = {}
        if pathlib.Path(file_path).suffix not in (".yaml", ".yml"):
            raise NotImplementedError

        with open(file_path, "r", encoding="utf-8") as stream:
            try:
                data = yaml.safe_load(stream)
                logger.trace(
                    f"Loaded new config from disk: {json.dumps(data, sort_keys=True, indent=4)}"
                )
            except yaml.YAMLError as err:
                logger.error(f"Error while loading config from disk: {repr(err)}")

        return data

    def save_current_session(self, file_path: str):
        """Save the current session as a yaml file to disk.

        Args:
            file_path (str): Full path to the yaml file.
        """
        self._save_config_to_file(file_path)
        print(f"Config was written to {file_path}.")

    def _save_config_to_file(self, file_path: str, raise_on_error: bool = True) -> bool:
        config = self.connector.get(MessageEndpoints.device_config())
        if not config:
            if raise_on_error:
                raise DeviceConfigError("No config found in the session.")
            return False
        config = config.content["resource"]
        out = {}
        for dev in config:
            dev.pop("id", None)
            dev.pop("createdAt", None)
            dev.pop("createdBy", None)
            dev.pop("sessionId", None)
            name = dev.pop("name")
            out[name] = dev

        with open(file_path, "w") as file:
            file.write(yaml.dump(out))
        return True

    def send_config_request(self, action: str = "update", config=None) -> None:
        """
        send request to update config
        Returns:

        """
        if action in ["update", "add", "set"] and not config:
            raise DeviceConfigError(f"Config cannot be empty for an {action} request.")
        RID = str(uuid.uuid4())
        self.connector.send(
            MessageEndpoints.device_config_request(),
            DeviceConfigMessage(action=action, config=config, metadata={"RID": RID}),
        )

        reply = self.wait_for_config_reply(RID)

        if not reply.content["accepted"] and not reply.metadata.get("updated_config"):
            raise DeviceConfigError(
                f"Failed to update the config: {reply.content['message']}. No devices were updated."
            )
        try:
            if not reply.content["accepted"] and reply.metadata.get("updated_config"):
                raise DeviceConfigError(
                    f"Failed to update the config: {reply.content['message']}. The old config will be kept in the device config history."
                )

            if "failed_devices" in reply.metadata:
                print("Failed to update the config for some devices.")
                for dev in reply.metadata["failed_devices"]:
                    print(
                        f"Device {dev} failed to update:\n {reply.metadata['failed_devices'][dev]}."
                    )
                devices = [dev for dev in reply.metadata["failed_devices"]]

                raise DeviceConfigError(
                    f"Failed to update the config for some devices. The following devices were disabled: {devices}."
                )
        finally:
            # wait for the device server and scan server to acknowledge the config change
            self.wait_for_service_response(RID)

    def wait_for_service_response(self, RID: str, timeout=10) -> messages.ServiceResponseMessage:
        """
        wait for service response

        Args:
            RID (str): request id
            timeout (int, optional): timeout in seconds. Defaults to 10.

        Returns:
            ServiceResponseMessage: reply message
        """
        elapsed_time = 0
        max_time = timeout
        while True:
            service_messages = self.connector.lrange(MessageEndpoints.service_response(RID), 0, -1)
            if not service_messages:
                time.sleep(0.005)
                elapsed_time += 0.005
            else:
                ack_services = [
                    msg.content["response"]["service"]
                    for msg in service_messages
                    if msg is not None
                ]
                checked_services = set(["DeviceServer", "ScanServer"])
                if self._service_name:
                    checked_services.add(self._service_name)
                if checked_services.issubset(set(ack_services)):
                    break
            if elapsed_time > max_time:
                if service_messages:
                    raise DeviceConfigError(
                        "Timeout reached whilst waiting for config change to be acknowledged."
                        f" Received {service_messages}."
                    )

                raise DeviceConfigError(
                    "Timeout reached whilst waiting for config change to be acknowledged. No"
                    " messages received."
                )

    def wait_for_config_reply(self, RID: str, timeout=10) -> RequestResponseMessage:
        """
        wait for config reply

        Args:
            RID (str): request id
            timeout (int, optional): timeout in seconds. Defaults to 10.

        Returns:
            RequestResponseMessage: reply message
        """
        start = 0
        while True:
            msg = self.connector.get(MessageEndpoints.device_config_request_response(RID))
            if msg is None:
                time.sleep(0.01)
                start += 0.01

                if start > timeout:
                    raise DeviceConfigError("Timeout reached whilst waiting for config reply.")
                continue
            return msg

    def load_demo_config(self):
        """Load BEC device demo_config.yaml for simulation."""
        dir_path = os.path.abspath(os.path.join(os.path.dirname(bec_lib.__file__), "./configs/"))
        fpath = os.path.join(dir_path, "demo_config.yaml")
        self.update_session_with_file(fpath)
