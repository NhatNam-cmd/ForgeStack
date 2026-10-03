import argparse

from .inventory import load_nodes


def print_nodes(nodes):
    print(f"{'NAME':<12} {'ADDRESS'}")

    for node in nodes:
        print(f"{node.name:<12} {node.address}")

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

    args = parser.parse_args()

    if args.command == "nodes":
        try:
            nodes = load_nodes(args.inventory)
            print_nodes(nodes)

        except FileNotFoundError:
            print(
                f"Error: inventory file not found: "
                f"{args.inventory}"
            )

        except ValueError as error:
            print(f"Error: {error}")