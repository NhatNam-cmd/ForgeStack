# ForgeStack

ForgeStack is a small infrastructure platform for deploying and operating workloads across multiple Linux nodes.

## Project Status

The project is currently in **Module 1 — Node Management**.

The lab environment currently contains two Ubuntu Server nodes running on VirtualBox. The active sprint focuses on building the first ForgeStack node inventory and CLI capability.

## Current Capabilities

ForgeStack can currently:

- Be installed locally as a Python package and provide the `forgestack` command.
- Load managed nodes from a YAML inventory.
- Display each node's `NAME` and `ADDRESS`.
- Report a clear error when the inventory path does not exist.
- Report a clear error when a node is missing a required field such as `address`.

## Run Locally

Python 3.13 is required.

Create and activate a virtual environment:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1

Install ForgeStack in editable mode:

```bash
pip install -e .
````

Run the node inventory command:

Bash

```
forgestack --inventory config/nodes.yaml nodes
```

Example output:

Plaintext

```
NAME         ADDRESS
node-a       192.168.1.83
node-b       192.168.1.60
```

## Current Limitations

- The node inventory is currently maintained manually by the operator.

- ForgeStack does not yet perform live node reachability checks.

- If one node entry is invalid, the current inventory loader stops loading instead of continuing with the remaining valid nodes.


## Documentation

- `docs/BUILD_SPECIFICATION.md`

- `docs/modules/M1_NODE_MANAGEMENT.md`