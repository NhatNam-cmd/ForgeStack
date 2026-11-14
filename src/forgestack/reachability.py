
from .node import Node
from .ssh import run_ssh


def check_node(node: Node) -> dict:
    result = run_ssh(node, "hostname")

    if result.failure is not None:
        return {
            "status": result.failure,
            "reason": result.reason
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
