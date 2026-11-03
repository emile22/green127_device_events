from __future__ import annotations

import os
from pathlib import Path
from typing import Any


class NetconfUnavailable(RuntimeError):
    pass


def _connection_config_paths() -> tuple[Path, ...]:
    repository_root = Path(__file__).resolve().parents[3]
    return (
        repository_root / "install" / "runtime" / "netconf" / "connection.env",
        repository_root / "allrun5" / "runtime" / "netconf" / "connection.env",
    )


def _read_local_connection_config() -> dict[str, str]:
    for path in _connection_config_paths():
        if not path.is_file():
            continue
        values: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            key, separator, value = line.partition("=")
            if separator and key in {
                "NETCONF_HOST",
                "NETCONF_PORT",
                "NETCONF_USERNAME",
                "NETCONF_PASSWORD",
                "NETCONF_DEVICE_ID",
            }:
                values[key] = value
        if values:
            return values
    return {}


class NetconfClient:
    def __init__(self, session: Any, *, device: str) -> None:
        self.session = session
        self.device = device

    @classmethod
    def connect_from_environment(cls) -> "NetconfClient":
        config = _read_local_connection_config()
        host = os.environ.get("NETCONF_HOST") or config.get("NETCONF_HOST", "localhost")
        port_text = os.environ.get("NETCONF_PORT") or config.get("NETCONF_PORT", "830")
        username = os.environ.get("NETCONF_USERNAME") or config.get("NETCONF_USERNAME")
        password = os.environ.get("NETCONF_PASSWORD") or config.get("NETCONF_PASSWORD")
        device = os.environ.get("NETCONF_DEVICE_ID") or config.get("NETCONF_DEVICE_ID", host)
        if not username or not password:
            raise NetconfUnavailable(
                "NETCONF credentials were not found in install/runtime/netconf/connection.env, "
                "allrun5/runtime/netconf/connection.env, or NETCONF_USERNAME/NETCONF_PASSWORD"
            )
        try:
            port = int(port_text)
        except ValueError as error:
            raise NetconfUnavailable(f"NETCONF_PORT must be an integer, found {port_text!r}") from error
        if not 1 <= port <= 65535:
            raise NetconfUnavailable(f"NETCONF_PORT is outside 1..65535: {port}")

        try:
            from ncclient import manager

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
            raise NetconfUnavailable(f"NETCONF connection to {host}:{port} failed: {error}") from error
        return cls(session, device=device)

    def get(self) -> str:
        try:
            return self.session.get().data_xml
        except Exception as error:
            raise NetconfUnavailable(f"NETCONF <get> failed: {error}") from error

    def close(self) -> None:
        self.session.close_session()

    def __enter__(self) -> "NetconfClient":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()
