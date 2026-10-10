# ForgeStack

ForgeStack is a small infrastructure platform for deploying and operating workloads across multiple Linux nodes.

## Project Status

**Module 1 — Node Management** is in progress. M1-S1 (inventory and CLI) and M1-S2 (SSH access checks) are complete; M1-S3 (identity, failure handling, and acceptance tests) is next.

The current lab uses two Ubuntu Server VMs on VirtualBox.

## Current Capabilities

- Install ForgeStack as a local Python package with the `forgestack` CLI.
- Load node name, address, and SSH username from a YAML inventory.
- List configured nodes using the `nodes` command.
- Check SSH access using the `status` command and report a status with a reason.
- Report missing inventory files or required node fields.

**SSH status meanings:** `REACHABLE` (remote command succeeded), `AUTH_FAILED` (authentication rejected), `TIMEOUT` (process time limit exceeded), and `ERROR` (other check failures).

## Run Locally

Requires Python 3.13 and an available OpenSSH client. Configure key-based SSH access to the lab nodes before using `status`; verify each server's host key rather than bypassing verification.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

Update `config/nodes.yaml` with your current node IP addresses and SSH usernames, then run:

```powershell
forgestack --inventory config/nodes.yaml nodes
forgestack --inventory config/nodes.yaml status
```

Example output (addresses depend on DHCP):

```text
NAME         ADDRESS          STATUS         REASON
node-a       192.168.1.10     REACHABLE      SSH command succeeded
node-b       192.168.1.32     REACHABLE      SSH command succeeded
```

## Current Limitations

- Inventory addresses are maintained manually; DHCP changes may make them stale.
- `status` verifies SSH command execution, not overall node or application health.
- SSH error classification is basic; timeout and missing-client handling have not yet been exercised in dedicated tests.
- An invalid inventory entry stops the inventory loader. Independent handling of invalid entries is planned for M1-S3.

## Documentation

- [Build Specification](docs/BUILD_SPECIFICATION.md)
- [M1 — Node Management](docs/modules/M1_NODE_MANAGEMENT.md)
