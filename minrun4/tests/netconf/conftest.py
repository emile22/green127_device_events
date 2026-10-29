import os
import socket
from pathlib import Path

import pytest
from ncclient import manager


def _load_local_connection_config() -> None:
    config_path = Path(__file__).parents[2] / "state" / "netconf" / "connection.env"
    if not config_path.exists():
        return
    for line in config_path.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if separator and key and key not in os.environ:
            os.environ[key] = value


@pytest.fixture(scope="module")
def netconf_manager():
    _load_local_connection_config()
    host = os.environ.get("NETCONF_HOST")
    username = os.environ.get("NETCONF_USERNAME")
    password = os.environ.get("NETCONF_PASSWORD")
    if not host or not username or not password:
        pytest.skip(
            "NETCONF smoke tests need NETCONF_HOST, NETCONF_USERNAME, and NETCONF_PASSWORD; "
            "start the local WSL stack first"
        )
    port = int(os.environ.get("NETCONF_PORT", "830"))

    try:
        with socket.create_connection((host, port), timeout=3):
            pass
    except OSError as error:
        pytest.fail(f"NETCONF infrastructure is unavailable at {host}:{port}: {error}")

    try:
        session = manager.connect_ssh(
            host=host,
            port=port,
            username=username,
            password=password,
            hostkey_verify=False,
            allow_agent=False,
            look_for_keys=False,
            timeout=8,
            device_params={"name": "default"},
        )
    except Exception as error:
        pytest.fail(f"NETCONF SSH authentication/connection failed: {error}")

    try:
        yield session
    finally:
        session.close_session()