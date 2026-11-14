
import subprocess
from dataclasses import dataclass
from typing import Literal

from .node import Node


@dataclass(frozen=True)
class SSHResult:
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    failure: Literal["TIMEOUT", "ERROR"] | None = None
    reason: str = ""


def run_ssh(node: Node, remote_command: str) -> SSHResult:
    command = [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=5",
        f"{node.user}@{node.address}",
        remote_command
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )

        return SSHResult(
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr
        )

    except subprocess.TimeoutExpired:
        return SSHResult(
            failure="TIMEOUT",
            reason="SSH process exceeded 10 seconds"
        )

    except FileNotFoundError:
        return SSHResult(
            failure="ERROR",
            reason="OpenSSH client executable not found"
        )
