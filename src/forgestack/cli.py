
import argparse

import yaml

from .inventory import load_nodes
from .reachability import check_node
from .service_state import check_service


def print_nodes(nodes):
    print(f"{'NAME':<12} {'ADDRESS'}")

    for node in nodes:
        print(f"{node.name:<12} {node.address}")


def print_status(nodes):
    print(f"{'NAME':<12} {'ADDRESS':<16} {'STATUS':<14} REASON")

    for node in nodes:
        result = check_node(node)

        print(
            f"{node.name:<12} "
            f"{node.address:<16} "
            f"{result['status']:<14} "
            f"{result['reason']}"
        )


def print_services(nodes, service: str) -> int:
    results = [
        (node, check_service(node, service))
        for node in nodes
    ]

    print(f"Service: {service}")
    print()

    print(
        f"{'NAME':<12} "
        f"{'ADDRESS':<16} "
        f"{'STATUS':<12} "
        f"{'SYSTEMD':<28} "
        f"REASON"
    )

    inspection_failed = False

    for node, state in results:
        if state.status in {"ERROR", "TIMEOUT", "UNKNOWN"}:
            inspection_failed = True

        raw_state = "/".join([
            state.load_state or "-",
            state.active_state or "-",
            state.sub_state or "-"
        ])

        print(
            f"{node.name:<12} "
            f"{node.address:<16} "
            f"{state.status:<12} "
            f"{raw_state:<28} "
            f"{state.reason}"
        )

    return 1 if inspection_failed else 0


def main():
    parser = argparse.ArgumentParser(prog="forgestack")

    parser.add_argument(
        "--inventory",
        required=True,
        help="Path to the node inventory file"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    subparsers.add_parser(
        "nodes",
        help="List managed nodes"
    )

    subparsers.add_parser(
        "status",
        help="Check SSH access to managed nodes"
    )

    services_parser = subparsers.add_parser(
        "services",
        help="Inspect a systemd service on managed nodes"
    )

    services_parser.add_argument(
        "service",
        help="Systemd service unit name, e.g. nginx.service"
    )

    args = parser.parse_args()

    try:
        nodes, errors = load_nodes(args.inventory)

        for error in errors:
            print(f"WARNING: {error}")

        if not nodes:
            print("Error: no valid nodes found in inventory")
            return 2

        command_exit = 0

        if args.command == "nodes":
            print_nodes(nodes)

        elif args.command == "status":
            print_status(nodes)

        elif args.command == "services":
            command_exit = print_services(nodes, args.service)

        if errors:
            return 2

        return command_exit

    except FileNotFoundError:
        print(f"Error: inventory file not found: {args.inventory}")
        return 2

    except ValueError as error:
        print(f"Error: {error}")
        return 2

    except yaml.YAMLError as error:
        print(f"Error: invalid YAML: {error}")
        return 2
