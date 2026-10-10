import subprocess

from .node import Node


def check_node(node: Node) -> dict:
    command = [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=5",
        f"{node.user}@{node.address}",
        "hostname"
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )

    except subprocess.TimeoutExpired:
        return {
            "status": "TIMEOUT",
            "reason": "SSH process exceeded 10 seconds"
        }
    except FileNotFoundError:
        return {
            "status": "ERROR",
            "reason": "OpenSSH client executable not found"
        }
    if result.returncode == 0:
        return {
            "status": "REACHABLE",
            "reason": "SSH command succeeded"
        }
    error = result.stderr.strip()

    if "Permission denied" in error:
        return {
            "status": "AUTH_FAILED",
            "reason": "SSH authentication failed"
        }
    return {
        "status": "ERROR",
        "reason": error or f"SSH exited with code {result.returncode}"
    }