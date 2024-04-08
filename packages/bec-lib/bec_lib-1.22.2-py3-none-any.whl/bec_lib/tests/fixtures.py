from __future__ import annotations

import copy
import threading
from unittest import mock

import pytest

from bec_lib.service_config import ServiceConfig
from bec_lib.tests.utils import ClientMock, ConnectorMock, DMClientMock, load_test_config


@pytest.fixture()
def threads_check():
    threads_at_start = set(th for th in threading.enumerate() if th is not threading.main_thread())
    yield
    threads_after = set(th for th in threading.enumerate() if th is not threading.main_thread())
    additional_threads = threads_after - threads_at_start
    assert (
        len(additional_threads) == 0
    ), f"Test creates {len(additional_threads)} threads that are not cleaned: {additional_threads}"


@pytest.fixture
def dm():
    service_mock = mock.MagicMock()
    service_mock.connector = ConnectorMock("")
    dev_manager = DMClientMock(service_mock)
    yield dev_manager


@pytest.fixture
def dm_with_devices(dm):
    dm._session = copy.deepcopy(load_test_config())
    dm._load_session()
    yield dm


@pytest.fixture()
def bec_client_mock(dm_with_devices):
    client = ClientMock(
        ServiceConfig(redis={"host": "host", "port": 123}, scibec={"host": "host", "port": 123}),
        ConnectorMock,
        wait_for_server=False,
    )
    client.start()
    device_manager = dm_with_devices
    for name, dev in device_manager.devices.items():
        dev._info["hints"] = {"fields": [name]}
    client.device_manager = device_manager
    try:
        yield client
    finally:
        client.shutdown()
        client._reset_singleton()
        device_manager.devices.flush()
