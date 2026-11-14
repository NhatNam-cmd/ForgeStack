
# M2 — Node & Service State

**Module status:** IN PROGRESS  
**Completed:** M2-S1 — Remote State Collection  
**Next:** M2-S2 — Listener & Health Validation

## Goal

Collect and normalize useful state from managed Linux nodes.

ForgeStack must distinguish node reachability, service state,
listener state, and application health instead of treating
them as a single healthy/unhealthy condition.

## Current Design

M2-S1 extends the existing node management capability with
reusable SSH execution and systemd service inspection.

```text
Node inventory
      |
      v
Shared SSH execution (ssh.py)
      |
      v
Remote systemctl show
      |
      v
Property parsing and state normalization
      |
      v
ServiceState model
      |
      v
CLI output and inspection exit code
```

### Component Responsibilities

| Component | Responsibility |
|---|---|
| `ssh.py` | Execute remote commands and return execution evidence |
| `reachability.py` | Interpret SSH access status |
| `service_state.py` | Parse and normalize systemd service state |
| `cli.py` | Present results and determine command exit codes |

The SSH execution layer does not decide whether a service
is running or healthy. Domain-specific modules interpret
the collected evidence.

## M2-S1 — Remote State Collection

**Status:** DONE  
**Build day:** F13 — 2026-11-14

### Delivered Capabilities

- [x] Extract reusable SSH command execution from M1.
- [x] Preserve existing node reachability behavior.
- [x] Collect systemd service properties remotely.
- [x] Parse and normalize service state.
- [x] Preserve raw systemd properties and execution reasons.
- [x] Expose service inspection through the CLI.
- [x] Report inspection errors without losing other node results.
- [x] Add automated regression tests.
- [x] Verify service state changes on real Linux nodes.
- [x] Verify remote inspection failure isolation.

### Usage

```powershell
forgestack --inventory config/nodes.yaml nodes

forgestack --inventory config/nodes.yaml status

forgestack --inventory config/nodes.yaml services nginx.service

forgestack --inventory config/nodes.yaml services ssh.service
```

The `services` command inspects the specified systemd service
on every valid node in the inventory.

Service names must include the `.service` suffix.

### Service State Model

ForgeStack collects:

- `LoadState`: unit loading state.
- `ActiveState`: high-level activation state.
- `SubState`: detailed unit state.

These properties are normalized into ForgeStack states.

| Status | Meaning |
|---|---|
| RUNNING | Loaded, active, and running |
| ACTIVE | Active with a different substate |
| STOPPED | Loaded but inactive |
| FAILED | Loaded and in a failed state |
| NOT_FOUND | Service unit does not exist |
| UNKNOWN | Insufficient or unsupported state information |
| TIMEOUT | SSH subprocess exceeded its execution limit |
| ERROR | SSH or remote command execution failed |

A successful SSH command does not imply that a service is
running. A running service does not imply application health.

### CLI Exit Codes

| Code | Meaning |
|---|---|
| 0 | Inspection completed with determined service states |
| 1 | At least one inspection returned ERROR, TIMEOUT, or UNKNOWN |
| 2 | Invalid inventory or command input |

STOPPED, FAILED, and NOT_FOUND are valid inspection results.
They do not by themselves cause inspection failure.

Inventory errors take priority over inspection errors.

### SSH Execution Semantics

SSH uses non-interactive authentication with:

- `BatchMode=yes`
- `ConnectTimeout=5`
- Python subprocess timeout of 10 seconds

A connection timeout reported by OpenSSH may produce ERROR
with the original stderr message.

A Python subprocess timeout produces TIMEOUT.

These conditions are not equivalent and do not prove that
a managed node is powered off.

## Verification

### Automated Tests

```powershell
python -m unittest discover -s tests -v
```

Result on 2026-11-14:

```text
Ran 12 tests in 0.012s

OK
```

Coverage includes:

- systemd property parsing;
- service state normalization;
- missing and incomplete state information;
- invalid service names;
- SSH timeout and missing executable handling;
- CLI exit codes;
- inspection failure isolation;
- inventory error priority.

Timeout and missing executable handling are tested using
mocks, not actual missing-client or subprocess-timeout events.

### LIVE Environment

- Windows controller running the ForgeStack CLI.
- Node A: Ubuntu Server, SSH, Nginx.
- Node B: Ubuntu Server, SSH, Nginx not installed.
- Key-based SSH access.
- DHCP-assigned node addresses.

Addresses during acceptance:

```text
node-a: 192.168.1.126
node-b: 192.168.1.125
```

### Acceptance 1 — Independent Node and Service State

```text
NODE     SSH          NGINX
node-a   REACHABLE    RUNNING
node-b   REACHABLE    NOT_FOUND
```

Both inspections returned service states successfully.

The missing Nginx unit on Node B returned:

```text
LoadState=not-found
ActiveState=inactive
SubState=dead
returncode=0
```

This demonstrates why service state cannot be inferred from
the command exit code alone.

Result: PASS.

### Acceptance 2 — Controlled Service State Change

Stop Nginx on Node A:

```bash
sudo systemctl stop nginx
```

Inspect from the controller:

```powershell
forgestack --inventory config/nodes.yaml status

forgestack --inventory config/nodes.yaml services nginx.service
```

Observed:

```text
node-a   REACHABLE
node-b   REACHABLE

node-a   STOPPED     loaded/inactive/dead
node-b   NOT_FOUND   not-found/inactive/dead
```

Service inspection exit code: `0`.

Restore Nginx on Node A:

```bash
sudo systemctl start nginx
```

Repeat service inspection:

```text
node-a   RUNNING     loaded/active/running
node-b   NOT_FOUND   not-found/inactive/dead
```

Service inspection exit code: `0`.

Verify the restored HTTP endpoint manually:

```powershell
curl.exe -I --max-time 5 http://192.168.1.126/
```

Observed:

```text
HTTP/1.1 200 OK
```

Result: PASS.

Recovery was performed manually by the operator.
ForgeStack detected the resulting service state changes.

The HTTP request was a manual post-recovery verification,
not a ForgeStack-owned application health check.

### Acceptance 3 — Remote Inspection Failure Isolation

Use a temporary inventory containing an unavailable test
address and the valid Node B record.

```yaml
nodes:
  - name: node-offline
    address: 192.0.2.10
    user: nam

  - name: node-b
    address: 192.168.1.125
    user: namb
```

Run service inspection against this inventory.

Observed:

```text
node-offline ERROR     -/-/-
node-b       NOT_FOUND not-found/inactive/dead
```

SSH error:

```text
ssh: connect to host 192.0.2.10 port 22: Connection timed out
```

CLI exit code: `1`.

Node B was inspected despite the first node's failure.
The temporary inventory was removed after verification.

Result: PASS.

This scenario verifies remote inspection failure isolation.
It does not simulate a confirmed physical node shutdown.

## M2-S2 — Listener & Health Validation

**Status:** PLANNED

- [ ] Collect listener state from managed nodes.
- [ ] Define an application health contract.
- [ ] Validate HTTP response status and expected content.
- [ ] Represent listener and application health independently.
- [ ] Detect a running service with an unhealthy endpoint.

## M2-S3 — State Mismatch & Acceptance

**Status:** PLANNED

- [ ] Combine relevant state dimensions in operator output.
- [ ] Verify intentional state mismatch scenarios.
- [ ] Review timeout and error representation.
- [ ] Complete module-level acceptance and documentation.

## Known Limitations

- Inspection currently supports systemd `.service` units.
- Managed nodes are inspected sequentially.
- Node reachability and service inspection use separate CLI commands.
- Inventory addresses require manual updates after DHCP changes.
- Listener inspection is not implemented yet.
- Application health inspection is not implemented yet.
- No continuous monitoring or historical state storage.
- No automatic service recovery or workload deployment.

## Module Completion Criteria

- [x] Collect useful state from remote nodes.
- [x] Distinguish SSH reachability from systemd service state.
- [x] Represent running, stopped, missing, and failed service states.
- [x] Represent remote inspection errors and timeouts.
- [x] Provide understandable and manually verifiable CLI output.
- [x] Verify independent node and service state behavior.
- [ ] Collect and represent listener state.
- [ ] Validate application health using a health contract.
- [ ] Verify running-service/unhealthy-application mismatch.
- [ ] Complete final module acceptance.

M2-S1 is complete. Module 2 remains in progress until
listener and application health capabilities are implemented
and the remaining module-level acceptance criteria pass.
