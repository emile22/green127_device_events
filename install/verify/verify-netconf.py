import socket
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from ncclient import manager


YANG_LIBRARY_NS = "urn:ietf:params:xml:ns:yang:ietf-yang-library"
HARDWARE_NS = "urn:ietf:params:xml:ns:yang:ietf-hardware"
GREEN_NS = "urn:ietf:params:xml:ns:yang:ietf-power-and-energy"
BASE_CAPABILITIES = (
    "urn:ietf:params:netconf:base:1.0",
    "urn:ietf:params:netconf:base:1.1",
)
EXPECTED_MODULES = {
    "ietf-hardware": "2018-03-13",
    "ietf-power-and-energy": "2026-07-02",
}


def read_config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if separator:
            values[key] = value
    return values


def choose_host(config: dict[str, str]) -> tuple[str, int]:
    port = int(config.get("NETCONF_PORT", "830"))
    candidates = ["localhost"]
    fallback = config.get("NETCONF_HOST")
    if fallback and fallback not in candidates:
        candidates.append(fallback)
    failures: list[str] = []
    for host in candidates:
        try:
            with socket.create_connection((host, port), timeout=3):
                return host, port
        except OSError as error:
            failures.append(f"{host}:{port}: {error}")
    raise RuntimeError("NETCONF is unreachable: " + "; ".join(failures))


def main(config_path: str) -> int:
    config = read_config(Path(config_path))
    username = config.get("NETCONF_USERNAME")
    password = config.get("NETCONF_PASSWORD")
    if not username or not password:
        raise RuntimeError("NETCONF connection config is missing credentials")
    host, port = choose_host(config)
    print(f"[PASS] TCP connection: {host}:{port}")

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
    try:
        capabilities = [str(item) for item in session.server_capabilities]
        if not any(item.startswith(BASE_CAPABILITIES) for item in capabilities):
            raise RuntimeError("server does not advertise NETCONF base 1.0/1.1")
        print("[PASS] NETCONF base capability")

        library_filter = (
            f'<yang-library xmlns="{YANG_LIBRARY_NS}"/>'
        )
        library_reply = ET.fromstring(
            session.get(filter=("subtree", library_filter)).data_xml
        )
        installed_modules: dict[str, set[str]] = {}
        for module in library_reply.findall(f".//{{{YANG_LIBRARY_NS}}}module"):
            name = module.find(f"{{{YANG_LIBRARY_NS}}}name")
            revision = module.find(f"{{{YANG_LIBRARY_NS}}}revision")
            if name is not None and name.text:
                installed_modules.setdefault(name.text, set()).add(
                    revision.text if revision is not None and revision.text else ""
                )
        for module_name, expected_revision in EXPECTED_MODULES.items():
            if expected_revision not in installed_modules.get(module_name, set()):
                raise RuntimeError(
                    f"YANG Library does not report {module_name}@{expected_revision}"
                )
            print(f"[PASS] YANG module capability: {module_name}@{expected_revision}")

        data_reply = ET.fromstring(session.get().data_xml)
        if data_reply.find(f".//{{{HARDWARE_NS}}}component") is None:
            raise RuntimeError("<get> reply does not contain ietf-hardware components")
        print("[PASS] RFC 8348 hardware operational data")
        if data_reply.find(f".//{{{GREEN_NS}}}energy-object") is None:
            raise RuntimeError("<get> reply does not contain GREEN Energy Objects")
        print("[PASS] GREEN Energy Object operational data")
        print("[PASS] NETCONF XML parsed successfully")
    finally:
        session.close_session()
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify-netconf.py <connection.env>")
    try:
        raise SystemExit(main(sys.argv[1]))
    except Exception as error:
        print(f"[FAIL] NETCONF end-to-end: {error}", file=sys.stderr)
        raise SystemExit(1)
