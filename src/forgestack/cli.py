import argparse

from .inventory import load_nodes
from .reachability import check_node

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

    args = parser.parse_args()

    try:
        nodes = load_nodes(args.inventory)

        if args.command == "nodes":
            print_nodes(nodes)

        elif args.command == "status":
            print_status(nodes)

    except FileNotFoundError:
        print(
            f"Error: inventory file not found: "
            f"{args.inventory}"
        )

    except ValueError as error:
        print(f"Error: {error}")
