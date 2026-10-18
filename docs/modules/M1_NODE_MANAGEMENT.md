# M1 — Node Management

**Module status:** IN PROGRESS
**Completed:** M1-S1, M1-S2 (core scope)
**Current:** M1-S3 — Final Review & Acceptance

## Goal and Environment

Provide a consistent inventory of managed Linux nodes and a basic, evidence-based SSH access status for each node.

The lab consists of two Ubuntu Server VMs (`forgestack-node-a` and `forgestack-node-b`) on VirtualBox bridged networking. Their IP addresses are assigned by DHCP and may change.

## Current Design

```text
YAML inventory (name, address, user)
          ↓
       Node model
          ↓
OpenSSH via Python subprocess
          ↓
 returncode / stderr / timeout
          ↓
    status + reason
          ↓
      CLI output
```

Commands:

```powershell
forgestack --inventory config/nodes.yaml nodes
forgestack --inventory config/nodes.yaml status
```

An SSH check runs the remote `hostname` command using key-based authentication and non-interactive mode. Its results describe **SSH access from the ForgeStack machine**, not overall node or application health.

| Status | Meaning |
|---|---|
| `REACHABLE` | Remote SSH command completed with exit code `0`. |
| `AUTH_FAILED` | SSH authentication was rejected. |
| `TIMEOUT` | Python's total subprocess timeout was exceeded. |
| `ERROR` | Another SSH or local execution error occurred; inspect `reason`. |

`ConnectTimeout=5` limits SSH connection setup; the Python `timeout=10` limits the overall SSH subprocess. SSH errors are classified conservatively; they do not prove a node is powered off.

## Sprint Progress

### M1-S1 — Inventory & CLI — DONE

- [x] Define a minimal node model and YAML inventory.
- [x] Load and list Node A and Node B using the CLI.
- [x] Report missing inventory files and missing required fields.
- [x] Commit the runnable project capability.

### M1-S2 — SSH Reachability & Status — DONE (core scope)

- [x] Add per-node SSH usernames to the inventory.
- [x] Configure and verify key-based SSH access to both VMs.
- [x] Execute an SSH command through Python `subprocess`.
- [x] Return normalized `status` and `reason` values.
- [x] Verify two reachable nodes and an authentication failure.
- [x] Confirm a connection-refused error is surfaced without marking the host offline.
- [x] Continue checking Node B when Node A authentication fails.
- [x] Implement process timeout and missing-SSH-client handling.
- [ ] Test process timeout and missing-client handling directly.

### M1-S3 — Identity, Failure Handling & Acceptance — PLANNED

### M1-S3 — Identity, Failure Handling & Acceptance — IN PROGRESS

- [x] Define logical node identity independently of DHCP addresses.
- [x] Preserve SSH host key verification; do not auto-trust changed keys.
- [x] Skip invalid inventory records while retaining valid nodes.
- [x] Detect missing fields and duplicate node names.
- [x] Return CLI exit code `0` for success and `2` for inventory errors.
- [x] Verify node failure isolation using an unreachable test address.
- [x] Pass six manual acceptance checks.
- [ ] Complete final review and commit.

## M1 Acceptance Criteria

M1 is complete only when:

- [x] Both nodes can be configured, listed, and checked using a consistent node model.
- [x] A failed SSH authentication check does not prevent reporting other nodes.
- [x] Basic SSH results can be compared with manual SSH and TCP tests.
- [ ] Offline-node and malformed-inventory scenarios are handled as specified.
- [ ] Stable identity behavior is defined and verified.
- [ ] Repeatable acceptance checks exist and pass.
- [ ] The operator can explain and reproduce the full node-status flow.

## Known Limitations and Scope

- Node addresses are updated manually if DHCP assignments change.
- SSH key access must be prepared on the controller and target nodes.
- The inventory path is supplied with `--inventory`.
- Invalid node records are skipped with warnings; malformed inventory
  structures are rejected.
- Stable node identity is defined, but DHCP changes still require manual
  address updates and SSH trust verification.
- Intermittent SSH timeouts remain uninvestigated.
- A successful SSH command does not imply healthy services, workloads, CPU, memory, or disk.
- M1 does **not** include deployment, monitoring, recovery, containers, agents, a database, or a GUI.
