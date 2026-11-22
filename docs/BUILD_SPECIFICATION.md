# ForgeStack Build Specification

**Status:** Proposed specification for the discovery-first direction (F14). Review against the repository before adopting as the implementation source of truth.

**Purpose:** Define verifiable product outcomes and boundaries without prematurely fixing implementation details.

> Lock outcomes, not implementation. Preserve working capabilities and evidence as the product evolves.

**Product direction:** [PRODUCT_DIRECTION.md](PRODUCT_DIRECTION.md)

## 1. Product Contract

ForgeStack is a lightweight, SSH-first tool for discovering, understanding, and tracking changes in **existing Linux infrastructure**. Its primary audience is people operating their own servers, homelabs, and self-hosted services.

Without deploying or orchestrating workloads, ForgeStack should help an operator answer:

- Which Linux nodes are known, reachable, and discoverable?
- What workloads and services are observable on each node, and what state are they in?
- What network endpoints, runtime details, and relationships can be established from evidence?
- Which observations are facts, which derive from configuration or inference, and what remains unknown?
- What changed between two useful observations, and where is data merely missing or collection incomplete?
- What context can be exported safely to investigate a problem or communicate with another person or external AI assistant?
- After the operator makes a change, what newly collected evidence verifies the outcome?

ForgeStack must distinguish **availability**, **service/runtime state**, **listener state**, and **application health**; no one signal proves the others.

## 2. Intended Core Experience

The target end-to-end experience is:

```text
Existing Linux node(s), accessible via authorized SSH
                ↓
Connect and identify targets with minimal configuration
                ↓
Collect node, systemd/service, and relevant endpoint evidence
                ↓
Normalize findings into understandable infrastructure context
                ↓
Record a useful, timestamped observation/snapshot
                ↓
Repeat collection and compare meaningful changes
                ↓
Export readable, provenance-aware troubleshooting context
                ↓
Operator investigates or fixes the problem outside ForgeStack
                ↓
Recollect and verify the observed state
```

This is a product target, not a claim that the complete flow currently exists. Relationships must not be invented to complete a diagram. Start with systemd and Linux nodes; expand to containers only when evidence and demand justify it.

## 3. Modules and Capability Outcomes

Module identifiers M1 and M2 retain continuity with existing work. The old deployment/placement/recovery roadmap is superseded; historical commits and evidence remain valid.

### M1 — Node Access & Inventory

ForgeStack can identify configured Linux targets, connect using authorized existing SSH access, distinguish targets reliably, report reachability and connection failures honestly, and preserve compatibility with the existing node inventory and CLI.

**Existing foundation:** Previous M1 work is complete according to recorded project evidence. Do not reimplement it merely because product direction changed.

### M2 — Linux Infrastructure Discovery

ForgeStack can collect and normalize useful information about an existing Linux node and its services. The initial scope uses systemd and node-level information; endpoint and workload details are added incrementally where supported by reliable evidence.

- Report node reachability separately from service state.
- Distinguish service active/inactive/failed/unknown where the underlying evidence supports it.
- Keep listener and application-health observations separate from service status.
- Record explicit collection failure, timeout, unsupported capability, and permission-limited results.
- Prefer targeted, bounded, read-only commands; avoid broad secret/configuration collection.

**Existing foundation:** M2-S1 systemd service-state inspection was implemented, tested, documented, and merged. M2 as defined here is not yet complete.

### M3 — Infrastructure Context Model

ForgeStack can represent discovered entities and evidence-supported relationships coherently across a node or small set of nodes.

- Record where an observation came from, when it was collected, and how complete it is.
- Distinguish **observed**, **configured**, **inferred**, and **unknown** information.
- Support missing relationships without fabricating connectivity or causal dependencies.
- Preserve stable identity where possible, while allowing IPs, service state, and other attributes to change.

This module does not require an automatic dependency graph or visualization at first. A simple structured model is acceptable.

### M4 — Snapshots & Change Comparison

ForgeStack can preserve useful observation sets and compare them in a way that is truthful about collection quality.

- Keep snapshot time, source/target, discovery scope, and collection outcome.
- Identify meaningful changes in comparable observed fields.
- Treat timeout, permission denial, incomplete discovery, or unsupported collection as **unknown/incomplete**, not automatically as disappearance, shutdown, or deletion.
- Explain changed, unchanged, newly observed, and not-comparable findings clearly.
- Permit controlled repeatable tests against known service-state changes.

No always-on daemon, metrics backend, or automated periodic scheduler is required for the initial version.

### M5 — Context Export & Reverification

ForgeStack can produce readable context for an operator, collaborator, or external AI assistant without requiring an AI provider.

- Export a human-readable summary and/or structured representation, with observations, provenance, timestamps, and gaps.
- Avoid exposing credentials, private keys, tokens, or sensitive configuration values by default.
- Make clear when exported material is incomplete or stale.
- Allow recollection after an operator-initiated fix so before/after evidence can be compared.
- Do not claim that a problem is fixed solely from a successful SSH connection or service-active flag.

## 4. Module Status Definitions

- **NOT STARTED:** No usable implementation exists.
- **IN PROGRESS:** Partial implementation exists; the defined outcome is not yet met.
- **USABLE:** A meaningful happy path works and can support a dependent increment; completion gates remain open.
- **DONE:** Acceptance, failure-path tests, reproducible evidence, and documentation meet the defined scope.
- **DEFERRED:** A possible extension, not a current completion requirement.

Module status is based on implementation and evidence, not merely the existence of a document or passing isolated unit tests.

## 5. Common Completion Gates

A module is DONE only when the following are satisfied within its explicitly agreed scope:

1. **Useful behavior:** An operator can obtain an observable, relevant result.
2. **Truthful evidence:** Facts, interpretations, unknowns, and collection errors are distinguishable.
3. **Failure handling:** At least one meaningful failure or incomplete-collection path is deliberately tested.
4. **Safety and compatibility:** Read-only behavior and least privilege are respected; existing supported functionality is not silently broken.
5. **Verification and documentation:** Reproducible tests or LIVE evidence demonstrate the behavior; the owner can explain inputs, collection logic, normalization, output, and likely failure points.

LIVE observations from Node A/B and synthetic/unit-test evidence must be labeled distinctly. No status is automatically upgraded based on a planned task.

## 6. Definition of Done by Module

### M1 — Node Access & Inventory

- At least two Linux nodes can be represented and distinguished.
- Authorized SSH access and basic reachability can be assessed.
- Invalid or offline nodes do not crash unrelated operations.
- Existing inventory/CLI behavior remains usable.
- Manual checks and recorded evidence support results.

### M2 — Linux Infrastructure Discovery

- Discovery works against at least one reachable Linux target using authorized SSH.
- Basic node attributes and at least one systemd service have clear, structured results.
- Service state is not confused with node reachability or application health.
- Permission/timeout/unsupported cases are represented explicitly.
- Two-node LIVE checks plus automated regression tests demonstrate repeatability at the agreed initial scope.

Further endpoint/listener discovery may be delivered as a later M2 increment; it is not automatically required for F15.

### M3 — Infrastructure Context Model

- Discovered entities can be related using evidence-supported links or references.
- Each relationship has a clear origin or is explicitly qualified as inferred/unknown.
- Data from two nodes can coexist without identity collision.
- Incomplete inputs do not silently produce fabricated relationships.

### M4 — Snapshots & Change Comparison

- Two observations can be saved and compared.
- A controlled change appears accurately in the comparison.
- A deliberate collection failure does not appear as a confirmed workload removal.
- Timestamp, scope, and collection-status limitations are visible.

### M5 — Context Export & Reverification

- A readable export shows observed state and relevant uncertainty.
- Secrets and unneeded sensitive data are omitted or masked by default.
- Exported context remains useful without AI integration.
- A controlled operator-initiated change can be checked with new evidence.

## 7. Core Acceptance Demonstration

A complete core demonstration should eventually be able to show:

1. Start with two Linux nodes already accessible using authorized SSH.
2. Identify both nodes; show one node or connection failure without crashing the entire run.
3. Discover basic node attributes and relevant systemd service state.
4. Show available endpoint evidence and supported relationships without inventing missing links.
5. Save a timestamped observation with explicit collection completeness.
6. Change a demo service's state manually in the isolated lab (outside ForgeStack).
7. Recollect and show a correct, explainable difference.
8. Simulate an unavailable target; report missing evidence as incomplete/unknown, not proof of deletion.
9. Export a readable, appropriately sanitized troubleshooting context.
10. After an operator manually resolves the demo issue, recollect to verify the observed result.

The demo proves **discovery and trustworthy context**, not workload deployment, service control, node placement, failover, or autonomous recovery.

## 8. Design Principles and Boundaries

- **Low friction:** Use existing SSH credentials/configuration and avoid avoidable setup.
- **Read-only by default:** Discovery never requires write access or service restart.
- **Evidence first:** Preserve provenance, freshness, missing observations, and uncertainty.
- **Truthful health model:** SSH reachable, systemd active, TCP listening, and application healthy are different claims.
- **Small footprint:** Avoid new long-running agents/services unless justified by real usage.
- **AI independent:** Do not require AI APIs to complete the core workflow.
- **Practical value:** Prefer reduced investigation effort over dashboards and feature count.
- **Incremental changes:** Preserve working code and compatibility; refactor only for an identified requirement.

## 9. Explicit Non-Goals for the Current Core

- Automated workload deployment, start/stop/restart orchestration, or removal.
- Workload placement, desired-state reconciliation, failover, or autonomous remediation.
- Replacement of Kubernetes, Ansible, Prometheus, full observability, or configuration management.
- Production-grade multi-cluster control plane or complex scheduling.
- Mandatory dashboard, container support, eBPF, graph database, or cloud integration.
- Secret collection or autonomous production changes.

Possible later extensions include container discovery, periodic collection, deeper telemetry, visual interfaces, remote/hybrid environments, and AI-assisted analysis of exported evidence. These are hypotheses to validate, not commitments.

## 10. Planning and Change Policy

```text
Product Direction
       ↓
Capability / Module outcome
       ↓
Small, testable increment
       ↓
LIVE validation + regression checks
       ↓
Decision to continue, adjust, or stop
```

Keep user-facing outcomes stable enough to guide implementation, but allow CLI syntax, YAML shape, code organization, storage format, and collection mechanism to evolve **with explicit compatibility decisions**. Record nontrivial tradeoffs in a short decision note.

The older spec remains accessible through Git history. Superseded placement and recovery outcomes are not unfinished debts.

## 11. Current State — F14 Review Baseline

Evidence available from the project history and provided Git log:

- Foundation: two Ubuntu Server nodes with SSH; Node A and Node B previously verified reachable.
- **M1:** Previously closed as DONE, pending regression verification after the direction update.
- **M2:** IN PROGRESS; M2-S1 systemd state collection/CLI/tests/docs merged to `main` at `e403a71` (merge), based on the supplied Git history.
- **M3–M5:** NOT STARTED under this new capability model; no implementation claims.
- Existing working-tree changes to YAML inventory/test files remain untouched; do not stage them accidentally.

The full codebase has not yet been inspected for F14. Actual command names, data structures, and the precise refactor/no-refactor decision must be validated against the repository.

## 12. Next Increment — F15 Discovery Foundation (Proposed)

**Goal:** Make one small improvement in generic SSH-first discovery, grounded in the current M1/M2 code and preserving existing behavior.

**Candidate scope, to finalize after code inspection:**

- Connect to a selected existing inventory target, or add minimal ad hoc SSH target support only if needed.
- Collect a small, useful set of node facts and relevant systemd service details.
- Produce one structured, human-readable result with explicit status/provenance.
- Handle a deliberately offline/invalid target without breaking discovery of reachable targets.
- Preserve existing CLI, inventory configuration, and M2-S1 regression tests.
- Verify on real Node A and B, record evidence, and commit only the relevant reviewed files.

**Explicitly excluded from F15:** snapshot diff, persistence migration, relationship inference, container discovery, GUI, scheduling, eBPF, remediation, and new deployment/control operations.

**Acceptance:** happy path on both reachable nodes; one controlled failure path; truthful output; no destructive actions; automated regression checks pass; minimal usage documentation and reproducible evidence.

F15 is not DONE until those tests are observed. The exact code surface and CLI contract remain open until a targeted repository review.

## 13. Core Completion Statement

ForgeStack Core is complete when a person operating existing Linux servers can connect with minimal setup, discover meaningful infrastructure facts, understand supported relationships and uncertainty, preserve and compare observations, export useful context, and recollect evidence after investigating or resolving a problem — **without requiring ForgeStack to deploy, modify, or recover workloads**.

This completion outcome is a hypothesis to validate against real troubleshooting workflows, not a guaranteed product-market fit claim.
