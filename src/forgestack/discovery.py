
from dataclasses import dataclass, field

from .node import Node
from .ssh import run_ssh


@dataclass(frozen=True)
class RunningService:
    name: str
    load_state: str
    active_state: str
    sub_state: str
    description: str


def parse_running_services(output: str) -> list[RunningService]:
    services: list[RunningService] = []

    for line_number, line in enumerate(output.splitlines(), start=1):
        if not line.strip():
            continue

        fields = line.split(maxsplit=4)

        if len(fields) != 5:
            raise ValueError(
                f"Line {line_number}: invalid systemd service row: {line!r}"
            )

        name, load_state, active_state, sub_state, description = fields

        if not name.endswith(".service"):
            raise ValueError(
                f"Line {line_number}: invalid service unit: {name!r}"
            )

        if (load_state, active_state, sub_state) != (
                "loaded", "active", "running"
        ):
            raise ValueError(
                f"Line {line_number}: unexpected state for {name}: "
                f"{load_state}/{active_state}/{sub_state}"
            )

        services.append(
            RunningService(
                name=name,
                load_state=load_state,
                active_state=active_state,
                sub_state=sub_state,
                description=description,
            )
        )

    return services


@dataclass(frozen=True)
class TextCollection:
    text: str | None = None
    error: str | None = None
    abort_followups: bool = False


def collect_text(
        node: Node, command: str, *, allow_empty: bool = False
) -> TextCollection:
    result = run_ssh(node, command)

    if result.failure is not None:
        return TextCollection(
            error=f"{result.failure}: {result.reason}",
            abort_followups=True,
        )

    if result.returncode is None:
        return TextCollection(error="SSH result has no exit status")


    if result.returncode != 0:
        reason = result.stderr.strip() or "Remote command failed"

        connection_failed = (
                result.returncode == 255
                and reason.startswith("ssh: connect to host ")
        )

        return TextCollection(
            error=f"Exit {result.returncode}: {reason}",
            abort_followups=connection_failed,
        )


    output = result.stdout.strip()

    if not output and not allow_empty:
        return TextCollection(error="Empty command output")

    return TextCollection(text=output)


@dataclass
class NodeDiscovery:
    node: Node
    hostname: str | None = None
    kernel: str | None = None
    running_services: list[RunningService] | None = None
    errors: dict[str, str] = field(default_factory=dict)


def discover_node(node: Node) -> NodeDiscovery:
    discovery = NodeDiscovery(node=node)

    hostname = collect_text(node, "hostname")

    if hostname.error is None:
        discovery.hostname = hostname.text
    else:
        discovery.errors["hostname"] = hostname.error

    if hostname.abort_followups:
        discovery.errors["kernel"] = (
            "NOT_COLLECTED: SSH execution timed out or was unavailable"
        )
        discovery.errors["services"] = (
            "NOT_COLLECTED: SSH execution timed out or was unavailable"
        )
        return discovery

    kernel = collect_text(node, "uname -r")

    if kernel.error is None:
        discovery.kernel = kernel.text
    else:
        discovery.errors["kernel"] = kernel.error

    if kernel.abort_followups:
        discovery.errors["services"] = (
            "NOT_COLLECTED: SSH execution timed out or was unavailable"
        )
        return discovery

    command = (
        "LC_ALL=C systemctl list-units "
        "--type=service --state=running "
        "--no-pager --no-legend --plain"
    )

    services = collect_text(node, command, allow_empty=True)

    if services.error is not None:
        discovery.errors["services"] = services.error
    else:
        try:
            discovery.running_services = parse_running_services(
                services.text or ""
            )
        except ValueError as exc:
            discovery.errors["services"] = str(exc)

    return discovery
