# ForgeStack

**Discover what is running on your Linux servers.**

ForgeStack is a lightweight, SSH-first command-line tool for discovering existing Linux infrastructure. It helps operators inspect known nodes and running systemd services without installing agents or changing workloads.

> Connect your servers. Discover what is running. Understand what changed. Export the context.

The full vision includes infrastructure context, snapshots, change comparison, and export. **Those capabilities are planned, not implemented yet.** See [Product Direction](docs/PRODUCT_DIRECTION.md) and [Build Specification](docs/BUILD_SPECIFICATION.md).

## Current capabilities

- Read Linux node names, addresses, and SSH usernames from a YAML inventory.
- List inventory entries with `nodes`.
- Check basic SSH command execution with `status`.
- Inspect the systemd state of a **named** `.service` unit across nodes with `services`.
- Discover each node's hostname, kernel release, and currently running systemd service units with `discover` — no service name required.
- Keep results from reachable nodes when another node fails, and report incomplete collection rather than interpreting it as an empty result.

**Scope:** M1 node access and inventory are the foundation; M2 Linux infrastructure discovery is in progress. The `discover` command is the initial discovery increment, not a complete infrastructure inventory.

## Requirements

- Python **3.13 or later** and an OpenSSH client available as `ssh` on the local machine.
- One or more Linux targets accessible using authorized SSH, with a working `hostname` and `uname` command.
- `systemd` on targets where service inspection/discovery is required.
- Existing SSH authentication (for example, a configured SSH key). ForgeStack uses non-interactive SSH and does not manage credentials.

Verify SSH host keys before connecting; do not disable host-key verification to get the tool working.

## Install

From the repository root (PowerShell example):

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## Configure targets

Create or edit `config/nodes.yaml`:

```yaml
nodes:
  - name: node-a
    address: 192.0.2.10
    user: operator
  - name: node-b
    address: 192.0.2.11
    user: operator
```

The addresses above are documentation examples; replace them with the addresses of your own servers. Keep private inventory files and credentials out of public commits.

## Usage

List configured nodes:

```powershell
forgestack --inventory config/nodes.yaml nodes
```

Check whether a remote command can run via SSH:

```powershell
forgestack --inventory config/nodes.yaml status
```

Inspect a specific systemd service, including inactive or failed states where available:

```powershell
forgestack --inventory config/nodes.yaml services ssh.service
```

Discover basic facts and **currently running** systemd services on every valid inventory node:

```powershell
forgestack --inventory config/nodes.yaml discover
```

A successful node section looks like:

```text
Node: node-a (192.0.2.10)
  Collection: COMPLETE
  Hostname: linux-a
  Kernel: 6.x.y-generic
  Running systemd services: 2 observed
    - cron.service: Regular background program processing daemon
    - ssh.service: OpenBSD Secure Shell server
```

This is an illustrative excerpt, not an actual LIVE result.

### How to interpret results

- `COMPLETE` means the three F15 collection fields (hostname, kernel release, and running systemd service list) were obtained without reported errors. It **does not** mean the node or its applications are healthy.
- `INCOMPLETE` means at least one collection field failed or was not collected. Other successfully collected fields remain visible.
- `Running systemd services: 0 observed` means a successful service query returned no running units. `UNKNOWN (not collected)` means there is no valid service-list observation.
- `status` proves only that a simple SSH command executed; `active/running` reports systemd runtime state, **not** TCP listener status or application health.
- `discover` lists running `.service` units only. A service absent from that list may be stopped, failed, not loaded, or otherwise outside the query; absence is **not proof of removal**.

### Exit codes

For `discover` and `services`:

| Code | Meaning |
| --- | --- |
| `0` | Collection/inspection completed without reported errors for valid inventory nodes. |
| `1` | One or more node inspections were incomplete or failed. |
| `2` | Inventory/input error (including invalid inventory records). |

The existing `nodes` and `status` commands retain their original behavior. In particular, `status` prints per-node SSH results but does not currently return exit code `1` solely because a node is unreachable.

## Tests

Run the complete automated test suite:

```powershell
python -m unittest discover -s tests -v
```

Tests cover SSH result handling, service-state normalization, running-service parsing, partial collection, and CLI failure isolation. Automated tests use mocks for SSH behavior; validate actual SSH discovery separately on targets you control.

## Current limitations

- SSH inventory is maintained manually; target addresses may change.
- `discover` runs bounded, read-only commands but does not collect container workloads, listeners, process relationships, or application health checks.
- Running-service discovery is based on `systemctl list-units --type=service --state=running`, not an exhaustive list of installed or stopped services.
- No snapshots, change comparison, JSON export, dashboard, background agent, or orchestration actions are implemented.
- Collection errors and unknowns are surfaced, but the current discovery model is not yet a persisted, timestamped evidence store.
- Linux/systemd outputs and permissions may vary by distribution and target configuration; broader compatibility is not yet established.

## Project documentation

- [Product Direction](docs/PRODUCT_DIRECTION.md)
- [Build Specification](docs/BUILD_SPECIFICATION.md)

ForgeStack's current focus is **read-only discovery and reliable infrastructure context**, not workload deployment, service control, placement, or autonomous recovery.
