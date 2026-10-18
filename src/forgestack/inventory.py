import yaml

from .node import Node


def load_nodes(path: str) -> tuple[list[Node], list[str]]:
    with open(path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict) or not isinstance(data.get("nodes"), list):
        raise ValueError("Inventory must contain a 'nodes' list")

    nodes = []
    errors = []
    seen_names = set()

    for index, item in enumerate(data["nodes"], start=1):
        if not isinstance(item, dict):
            errors.append(f"Record {index}: expected a node object")
            continue

        missing_fields = [
            field for field in ("name", "address", "user")
            if not isinstance(item.get(field), str) or not item[field].strip()
        ]

        if missing_fields:
            errors.append(
                f"Record {index}: missing or invalid "
                f"{', '.join(missing_fields)}"
            )
            continue

        name = item["name"].strip()

        if name in seen_names:
            errors.append(f"Record {index}: duplicate node name '{name}'")
            continue

        seen_names.add(name)

        nodes.append(
            Node(
                name=name,
                address=item["address"].strip(),
                user=item["user"].strip()
            )
        )

    return nodes, errors
