# ForgeStack

ForgeStack is a small infrastructure platform for deploying and operating workloads across multiple Linux nodes.

## Project Status

**Module 1 — Node Management:** USABLE.

**Module 2 — Node & Service State:** IN PROGRESS.

M2-S1 is complete. ForgeStack can inspect systemd service
state across managed nodes using reusable SSH execution,
normalize the results, and report inspection failures
without losing other node results.

M2-S2 will introduce listener inspection and application
health validation..

## Current Capabilities

- Install ForgeStack as a local Python package with the `forgestack` CLI.
- Load node name, address, and SSH username from a YAML inventory.
- List configured nodes using the `nodes` command.
- Check SSH access using the `status` command and report a status with a reason.
- Report missing inventory files or required node fields.
- Skip invalid inventory records while reporting warnings and returning a non-zero exit code.
- Execute reusable remote commands through a shared SSH layer.
- Inspect systemd service state across managed nodes.
- Preserve raw systemd properties alongside normalized states.
- Distinguish service inspection failures from stopped services.
- Continue inspecting other nodes when a remote inspection fails.
- Run automated regression tests using Python unittest.

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
Inspect a systemd service across managed nodes:

```powershell
forgestack --inventory config/nodes.yaml services nginx.service
```

Example:

```text
Service: nginx.service

NAME     STATUS       SYSTEMD
node-a   RUNNING      loaded/active/running
node-b   NOT_FOUND    not-found/inactive/dead
```

The service inspection command returns:

- `0`: inspection completed with determined states.
- `1`: one or more inspections failed or returned unknown state.
- `2`: invalid inventory or input.

## Tests

Run the automated regression suite:

```powershell
python -m unittest discover -s tests -v
```

The tests cover SSH execution error handling, service state
normalization, CLI exit codes, and inspection failure isolation.

## Current Limitations

- Inventory addresses are maintained manually; DHCP changes may make them stale.
- `status` verifies SSH command execution, not overall node or application health.
- SSH timeout and missing-client handling have mocked test
  coverage; dedicated LIVE tests remain pending.
- Service inspection currently supports systemd `.service` units.
- Listener and application health inspection are not implemented yet.
- Invalid node records are skipped with warnings; malformed inventory files return exit code `2`.

## Documentation

- [Build Specification](docs/BUILD_SPECIFICATION.md)
- [M1 — Node Management](docs/modules/M1_NODE_MANAGEMENT.md)
- [M2 — Node & Service State](docs/modules/M2_NODE_SERVICE_STATE.md)