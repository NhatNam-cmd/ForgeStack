
import re
import shlex
from dataclasses import dataclass
from typing import Literal

from .node import Node
from .ssh import SSHResult, run_ssh


ServiceStatus = Literal[
    "RUNNING",
    "ACTIVE",
    "STOPPED",
    "FAILED",
    "NOT_FOUND",
    "UNKNOWN",
    "TIMEOUT",
    "ERROR"
]


@dataclass(frozen=True)
class ServiceState:
    service: str
    status: ServiceStatus
    reason: str
    load_state: str | None = None
    active_state: str | None = None
    sub_state: str | None = None
    returncode: int | None = None


def parse_properties(output: str) -> dict[str, str]:
    properties = {}

    for line in output.splitlines():
        key, separator, value = line.partition("=")

        if separator:
            properties[key.strip()] = value.strip()

    return properties


def normalize_service_state(
        service: str,
        result: SSHResult
) -> ServiceState:
    if result.failure is not None:
        return ServiceState(
            service=service,
            status=result.failure,
            reason=result.reason
        )

    properties = parse_properties(result.stdout)

    load_state = properties.get("LoadState")
    active_state = properties.get("ActiveState")
    sub_state = properties.get("SubState")

    status: ServiceStatus
    reason: str

    if result.returncode == 255:
        status = "ERROR"
        reason = result.stderr.strip() or "SSH execution failed"

    elif load_state == "not-found":
        status = "NOT_FOUND"
        reason = "Service unit does not exist"

    elif result.returncode != 0:
        status = "ERROR"
        reason = (
                result.stderr.strip()
                or f"Remote command exited with code {result.returncode}"
        )

    elif not all((load_state, active_state, sub_state)):
        status = "UNKNOWN"
        reason = "Incomplete systemd state information"

    elif load_state != "loaded":
        status = "UNKNOWN"
        reason = f"Unexpected load state: {load_state}"

    elif active_state == "active" and sub_state == "running":
        status = "RUNNING"
        reason = "Service is active and running"

    elif active_state == "active":
        status = "ACTIVE"
        reason = f"Service is active with substate: {sub_state}"

    elif active_state == "inactive":
        status = "STOPPED"
        reason = "Service is inactive"

    elif active_state == "failed":
        status = "FAILED"
        reason = "Service is in failed state"

    else:
        status = "UNKNOWN"
        reason = f"Current state: {active_state}/{sub_state}"

    return ServiceState(
        service=service,
        status=status,
        reason=reason,
        load_state=load_state,
        active_state=active_state,
        sub_state=sub_state,
        returncode=result.returncode
    )


def check_service(node: Node, service: str) -> ServiceState:
    if not re.fullmatch(r"[A-Za-z0-9_.@:-]+\.service", service):
        raise ValueError("Expected a valid systemd service unit name")

    remote_command = (
        "systemctl show --no-pager "
        "--property=LoadState,ActiveState,SubState "
        f"-- {shlex.quote(service)}"
    )

    result = run_ssh(node, remote_command)

    return normalize_service_state(service, result)
