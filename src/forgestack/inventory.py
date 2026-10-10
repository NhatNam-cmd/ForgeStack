import yaml

from .node import Node

def load_nodes(path: str) -> list[Node]:
    with open(path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    nodes = []

    for item in data["nodes"]:
        if "name" not in item:
            raise ValueError("Node is missing 'name'")

        if "address" not in item:
            node_name = item.get("name", "<unknown>")
            raise ValueError(
                f"Node '{node_name}' is missing 'address'"
            )

        if "user" not in item:
            node_name = item.get("name", "<unknown")
            raise ValueError(
                f"Node '{node_name}' is missing 'user'"
            )
        node = Node(
            name=item["name"],
            address=item["address"],
            user=item["user"]
        )
        nodes.append(node)

    return nodes