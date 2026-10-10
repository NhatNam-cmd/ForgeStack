# M1 — Node Management

**Module status:** IN PROGRESS  
**Completed:** M1-S1, M1-S2 (core scope)  
**Next:** M1-S3 — Identity, Failure Handling & Acceptance

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

- [ ] Confirm node identity beyond the current DHCP address; avoid treating an IP as permanent identity.
- [ ] Test an intentionally offline node while another node remains available.
- [ ] Improve malformed-inventory handling so one bad entry does not hide valid nodes.
- [ ] Add repeatable acceptance tests for normal and failure cases.
- [ ] Review CLI behavior and complete M1 acceptance checks.

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
- Invalid inventory records currently stop loading; per-node SSH failures do not.
- A successful SSH command does not imply healthy services, workloads, CPU, memory, or disk.
- M1 does **not** include deployment, monitoring, recovery, containers, agents, a database, or a GUI.
