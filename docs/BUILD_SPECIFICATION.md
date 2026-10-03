# ForgeStack Build Specification

**Status:** Source of truth for product outcomes  
**Purpose:** Define what ForgeStack must eventually be able to do without locking the implementation too early.

> **Lock outcomes, not implementation.**

## 1. Product Contract

ForgeStack is a lightweight multi-node infrastructure platform for **deploying, operating, observing, placing, and recovering workloads across Linux machines**.

ForgeStack does not exist merely to run an application. Linux, systemd, containers, SSH, and other infrastructure primitives already do that.

ForgeStack exists to provide a management layer above those primitives so that an operator can answer:

- Which nodes exist and are currently usable?
- Which workloads are running, and where?
- Is a workload actually healthy?
- How can a workload be deployed and operated consistently?
- Which node should receive a workload?
- What failed: the workload, local runtime/service, node, or network path?
- What recovery action should be attempted?
- Was recovery successful?

## 2. Stable Product Outcome

ForgeStack Core is complete when it can demonstrate this end-to-end flow:

```text
multiple Linux nodes
        ↓
ForgeStack loads their managed identities
        ↓
operator submits a workload
        ↓
ForgeStack selects or accepts an eligible target node
        ↓
workload is deployed and started
        ↓
ForgeStack verifies workload health
        ↓
operator can inspect and control workload state
        ↓
service/process failure is introduced
        ↓
ForgeStack detects and handles/reports it
        ↓
whole-node failure is introduced
        ↓
ForgeStack detects node failure
        ↓
workload is recovered/redeployed where possible
        ↓
health is verified again
```

The exact implementation may change.

## 3. Core Modules

### M1 — Node Management
ForgeStack knows which Linux nodes it manages and can identify and report their basic availability reliably.

### M2 — Node & Service State
ForgeStack can collect and normalize useful state from managed nodes and distinguish node reachability, runtime/service state, listener state, and application health where applicable.

### M3 — Workload Deployment
ForgeStack can take a valid workload definition/artifact, deploy it to an eligible Linux node, start it, verify it, and report success or failure truthfully.

### M4 — Workload Lifecycle
ForgeStack can track and operate deployed workloads through actions such as start, stop, restart, inspect, and remove, while preserving a clear model of desired state versus actual state.

### M5 — Placement
ForgeStack can make a basic, explainable decision about which eligible node should run a workload using available node/workload information.

### M6 — Failure Detection & Recovery
ForgeStack can distinguish important failure classes, attempt an appropriate recovery action, and verify whether recovery succeeded.

### M7 — Remote / Hybrid Infrastructure
**Stretch module.** Validate that ForgeStack abstractions can extend beyond one local LAN to a remote/cloud-like node while preserving safe and understandable operation.

M7 is not required for ForgeStack Core completion.

## 4. Module Completion States

### NOT STARTED
The capability does not yet exist.

### USABLE
The primary happy path works well enough for another module to depend on it.

### DONE
The module has passed its Definition of Done, at least one meaningful failure path, acceptance scenarios, and evidence/documentation requirements.

Modules do **not** need to become perfect before dependent work begins.

## 5. Common Completion Gates

Every core module must eventually pass all five gates:

### 1. Behavior
A user/operator can perform a useful, observable action.

### 2. Ownership
ForgeStack owns meaningful control logic or system behavior. The module is not only a collection of manually executed third-party commands.

### 3. Understanding
The project owner can explain:

```text
input
→ ForgeStack logic
→ infrastructure interaction
→ output/state
→ likely failure points
```

### 4. Failure
At least one relevant failure path has been tested deliberately.

### 5. Evidence
There is runnable code/configuration plus reproducible output, test, or documentation showing that the capability works.

## 6. Module-Level Definition of Done

### M1 — Node Management

M1 is DONE when:

- ForgeStack has a clear representation of a managed node.
- At least two Linux nodes can be registered/configured.
- ForgeStack distinguishes Node A and Node B reliably.
- Basic availability/reachability can be checked.
- An unavailable or invalid node does not crash the entire operation.
- User-visible output clearly reports managed node state.
- Node identity is not based only on one fragile runtime value.
- The operator can verify ForgeStack's result manually.
- Acceptance scenarios pass with evidence.

### M2 — Node & Service State

M2 is DONE when:

- ForgeStack can collect useful state from a remote node.
- Node reachability and workload/service state are not treated as the same thing.
- ForgeStack can represent at least node reachable/unreachable, runtime/service running/stopped when relevant, and application-level health when a health contract exists.
- Timeout/error conditions are represented clearly.
- At least one intentional state mismatch is detected correctly.
- Operator-visible output is understandable and manually verifiable.

### M3 — Workload Deployment

M3 is DONE when:

- A real demo workload exists.
- ForgeStack can deliver/provision that workload to a target node.
- The workload can be started successfully.
- A client can use or observe the workload after deployment.
- ForgeStack knows where the workload was deployed.
- Deployment success is verified rather than assumed.
- A failed deployment is not falsely reported as successful.
- Another person can reproduce the basic deployment from project documentation.

### M4 — Workload Lifecycle

M4 is DONE when:

- ForgeStack tracks deployed workloads.
- Core lifecycle operations have defined behavior.
- Desired state and actual state are represented separately enough to reason about drift/failure.
- Operations are verified after execution.
- Invalid operations fail safely and clearly.
- Restart/reboot scenarios do not cause ForgeStack to silently lose track of managed workloads.

### M5 — Placement

M5 is DONE when:

- At least two eligible nodes exist.
- ForgeStack gathers enough state to make a placement decision.
- A placement policy exists in ForgeStack-owned logic.
- The decision is explainable.
- Ineligible nodes are not selected.
- At least one controlled scenario proves that a different input can lead to a different placement result.
- Placement behavior can be tested without relying on hidden AI reasoning.

### M6 — Failure Detection & Recovery

M6 is DONE when:

- ForgeStack can detect a workload/service failure.
- ForgeStack can detect a whole-node failure.
- Those failure classes are not handled identically by default.
- At least one recovery action exists.
- Recovery is verified after execution.
- Failed recovery is reported truthfully.
- A controlled service/process failure test has been completed.
- A controlled whole-node failure test has been completed.
- Before/after incident evidence exists.

### M7 — Remote / Hybrid Infrastructure

M7 is intentionally open-ended and will receive a dedicated DoD only if activated.

Possible goals include:

- adding a remote node;
- secure remote connectivity;
- observing latency/reachability differences;
- validating workload placement/recovery across local and remote infrastructure;
- documenting operational and cost/complexity trade-offs.

## 7. Core Acceptance Demo

ForgeStack Core should eventually support a demonstration broadly equivalent to:

```text
1. Start with at least two Linux nodes.
2. ForgeStack reports both nodes independently.
3. Submit/deploy a demo workload.
4. ForgeStack reports which node hosts it.
5. Client verifies the workload is usable.
6. ForgeStack reports workload health/state.
7. Stop or kill the workload process/service.
8. ForgeStack detects the failure.
9. Recover and verify the workload.
10. Power off or disconnect the hosting node.
11. ForgeStack detects the node failure.
12. Recover/redeploy the workload to another eligible node when possible.
13. Verify that the workload is usable again.
14. Show evidence explaining what happened.
```

Exact CLI syntax is not part of this contract.

## 8. Design Principles

- **Behavior before technology:** choose technology because a capability requires it, not because the tool is fashionable.
- **Existing primitives are allowed:** ForgeStack may use SSH, systemd, containers, Linux tools, libraries, metrics systems, and other infrastructure primitives.
- **ForgeStack owns control logic:** node/workload models, normalized state, placement, deployment workflow, failure handling, and recovery should contain meaningful project-owned behavior.
- **Build before over-design:** do not design the entire future architecture before current pain points exist.
- **Reproducibility matters:** a capability should eventually be repeatable from the repository and documentation.
- **Evidence over claims:** "works" means there is reproducible evidence.
- **Least privilege and safe change:** prefer narrow permissions, validation, rollback, and controlled failure tests.

## 9. Explicit Non-Goals

ForgeStack Core does not aim to:

- replace Kubernetes, Nomad, Docker, systemd, SSH, or Linux;
- support enterprise-scale clusters;
- provide a production-grade distributed consensus/control plane;
- provide a GUI;
- implement every infrastructure primitive itself;
- maximize feature count;
- hide infrastructure behavior from the project owner;
- use AI as a substitute for deterministic core control logic.

A feature outside the Product Contract should normally go to the backlog until a real problem justifies it.

## 10. Planning Model

```text
Vision
  ↓
Module
  ↓
Sprint
  ↓
Daily Build Task
```

A module may require multiple sprints.  
A sprint should normally create one usable product increment in roughly one or two Build Days.  
A daily task is only an execution step inside the active sprint.

## 11. Change Policy

### Stable
These should change rarely:

- Product Contract
- Core Acceptance Demo
- M1–M6 capability outcomes
- Common Completion Gates

### Flexible
These may evolve when evidence justifies it:

- programming language;
- CLI structure;
- config format;
- SSH library/transport mechanism;
- agent vs agentless model;
- systemd vs container runtime;
- state persistence;
- repository structure;
- monitoring stack;
- placement algorithm details.

When a major implementation choice has meaningful trade-offs, record it in a Decision Note.

## 12. Current High-Level Status

```text
Foundation Phase (F01–F08)         DONE ENOUGH

M1 — Node Management               IN PROGRESS
M2 — Node & Service State          NOT STARTED
M3 — Workload Deployment           NOT STARTED
M4 — Workload Lifecycle            NOT STARTED
M5 — Placement                     NOT STARTED
M6 — Failure Detection & Recovery  NOT STARTED
M7 — Remote / Hybrid               STRETCH / NOT STARTED
```

Current real infrastructure:

```text
Windows admin/client machine

forgestack-node-a
- Ubuntu Server
- SSH
- nginx
- Bridged networking

forgestack-node-b
- Ubuntu Server
- SSH
- Bridged networking

Node A ↔ Node B connectivity verified.
```

## 13. ForgeStack Core Completion Statement

ForgeStack Core is complete when:

> A user can manage multiple Linux nodes, deploy and operate a real workload, observe where and how it is running, make or inspect a basic placement decision, detect meaningful service/node failures, recover the workload when possible, and verify the final state with reproducible evidence.

The implementation may evolve. This outcome is the contract.
