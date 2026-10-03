

**Module:** M1  
**Status:** IN PROGRESS  
**Purpose:** Establish the first real ForgeStack-owned product capability.

## 1. Module Outcome

ForgeStack knows which Linux nodes it manages and can report their basic availability reliably.

At the end of M1, ForgeStack should no longer depend on the operator remembering:

```text
Node A IP is ...
Node B IP is ...
which host is which?
is it online?
how do I check it manually?
```

Instead, ForgeStack has its own small node model and can present managed infrastructure consistently.

## 2. Current Starting Point

### Node A

```text
hostname: forgestack-node-a
OS: Ubuntu Server
network: VirtualBox Bridged
addressing: DHCP / environment-dependent
SSH: available
nginx: available
```

### Node B

```text
hostname: forgestack-node-b
OS: Ubuntu Server
network: VirtualBox Bridged
addressing: DHCP / environment-dependent
SSH: available
```

Both nodes:

- run simultaneously;
- have independent hostname, MAC address, IP address, machine-id, and SSH identity;
- are reachable from Windows under the current LAN;
- can reach each other.

F08 established the environment. M1 begins the product.

## 3. User-Visible Capability

The exact CLI syntax is provisional.

The operator should eventually be able to perform an action conceptually similar to:

```text
fs nodes
```

and receive a useful view such as:

```text
NAME                 ADDRESS          STATUS
forgestack-node-a    <current addr>   reachable
forgestack-node-b    <current addr>   reachable
```

The value is not the table itself. The value is that ForgeStack:

1. has a persistent representation of managed nodes;
2. can distinguish them;
3. can inspect basic availability;
4. handles unavailable/invalid nodes predictably.

## 4. M1 Definition of Done

M1 is DONE when:

- [ ] ForgeStack has a clear internal representation of a node.
- [ ] At least Node A and Node B can be configured/registered.
- [ ] Node identity is not based only on a temporary DHCP address.
- [ ] ForgeStack can list managed nodes.
- [ ] ForgeStack can perform a basic availability/reachability check.
- [ ] ForgeStack reports reachable vs unreachable state clearly.
- [ ] One invalid/misconfigured node does not break reporting for all other nodes.
- [ ] One intentionally offline node is handled correctly.
- [ ] Output is useful enough for a human operator.
- [ ] The project owner can explain the complete node-status flow.
- [ ] ForgeStack result can be verified manually using Linux/network tools.
- [ ] At least one automated or repeatable acceptance check exists.
- [ ] README/module documentation explains how to reproduce the basic M1 behavior.

## 5. M1 Acceptance Scenarios

### Scenario A — Two healthy nodes

**Given**
- Node A is online.
- Node B is online.
- Both are configured as managed nodes.

**When**
ForgeStack lists/checks managed nodes.

**Then**
- both nodes are shown independently;
- identity is correct;
- both are reported as reachable/available;
- one node is not confused with the other.

### Scenario B — One node offline

**Given**
- Node A remains online.
- Node B is powered off or intentionally unreachable.

**When**
ForgeStack checks managed nodes.

**Then**
- Node A still reports correctly;
- Node B reports unreachable/unavailable;
- ForgeStack does not crash;
- the output does not falsely report Node B as healthy.

### Scenario C — Invalid node configuration

**Given**
- Node A and Node B are valid.
- An intentionally invalid node entry exists.

**When**
ForgeStack loads/checks the node inventory.

**Then**
- the invalid entry produces a clear error/status;
- valid nodes remain usable;
- one bad entry does not destroy the entire operation.

## 6. Sprint Plan

M1 will be built incrementally. Sprint boundaries may change if real implementation pain points appear.

### M1-S1 — Node Inventory / First Runnable ForgeStack Capability

**Status:** CURRENT

**Outcome**

ForgeStack has a minimal repository and can load/display Node A and Node B from a managed node inventory.

**Expected product increment**

Conceptually:

```text
fs nodes
```

or an equivalent runnable command/script.

**Scope**
- initialize/clean ForgeStack repository structure;
- define the smallest useful Node representation;
- define a minimal inventory/config representation;
- add Node A and Node B;
- load the inventory;
- display managed nodes consistently;
- handle at least one simple invalid input;
- document how to run the capability.

**Not required yet**
- live reachability;
- SSH execution abstraction;
- service state;
- deployment;
- monitoring;
- database;
- agent;
- containers;
- GUI.

**Exit / USABLE Gate**
- [ ] repository contains runnable ForgeStack code;
- [ ] Node A and Node B are represented as managed nodes;
- [ ] a command/script loads them from configuration;
- [ ] output is deterministic and understandable;
- [ ] at least one malformed/invalid inventory case is handled;
- [ ] the project owner can explain every important code path;
- [ ] changes are committed as a real product artifact.

### M1-S2 — Reachability & Normalized Node Status

**Status:** PLANNED

**Outcome**

ForgeStack can determine and present basic current availability for each managed node.

**Likely questions to solve**
- What evidence counts as "reachable"?
- ICMP, TCP/SSH, or another method?
- How should timeout be represented?
- What happens when a node address changes?
- Should reachability and SSH availability be separate states?

**Expected product increment**

Conceptually:

```text
NODE                 STATUS
forgestack-node-a    reachable
forgestack-node-b    unreachable
```

**Exit / USABLE Gate**
- [ ] live node check exists;
- [ ] result is normalized into a ForgeStack state;
- [ ] timeout/failure is handled;
- [ ] one failed node does not block other node checks;
- [ ] result can be manually verified.

### M1-S3 — Identity, Failure Handling & Module Acceptance

**Status:** PLANNED

**Outcome**

M1 becomes robust enough to call DONE.

**Likely scope**
- confirm stable node identity strategy;
- improve invalid/missing configuration handling;
- test one node offline;
- test invalid node entry;
- add repeatable acceptance checks;
- tighten CLI/operator output;
- update module documentation;
- run all M1 acceptance scenarios.

**Exit / DONE Gate**

All M1 DoD items and acceptance scenarios pass.

## 7. Open Design Questions

These are intentionally not locked yet.

### Node inventory format
Possible options:
- YAML;
- JSON;
- TOML;
- Python/native config;
- another simple format.

Decision should favor readability and simplicity.

### Node identity
Current IP addresses are DHCP-assigned and environment-dependent.

Possible identity inputs may include:
- logical ForgeStack node name;
- hostname;
- SSH host identity;
- machine-id;
- another stable identifier.

Do not assume current IPv4 address is permanent identity.

### Reachability mechanism
Possible signals include:
- ICMP;
- TCP/22;
- SSH handshake;
- another explicit probe.

M1-S2 should choose behavior based on what "reachable" needs to mean for ForgeStack.

### Remote execution
Possible implementation choices include:
- system SSH client via subprocess;
- Python SSH library;
- later another transport.

Do not decide until the first product increment reveals what is actually needed.

## 8. Current Non-Goals

M1 does not include:
- workload deployment;
- service health;
- containers;
- placement;
- recovery;
- monitoring stack;
- persistent database;
- agent daemon;
- cloud integration;
- GUI.

If one of these becomes necessary to complete M1 correctly, document the reason before expanding scope.

## 9. Evidence Expected from M1

By the end of M1, the repository should show:

```text
input/configured nodes
        ↓
ForgeStack node model
        ↓
node listing/status logic
        ↓
operator-visible result
        ↓
offline/invalid node handling
```

Useful evidence may include:
- source code;
- example inventory;
- terminal output;
- acceptance test output;
- failure screenshots/logs where useful;
- README/module instructions.

## 10. Learning / Ownership Check

Before M1 is called DONE, the project owner should be able to answer without relying on AI:

1. What makes a ForgeStack node a node?
2. Which values are identity, and which are temporary runtime state?
3. How does ForgeStack load a node?
4. How does ForgeStack decide basic availability?
5. What happens if one node is invalid or offline?
6. Which part is provided by Linux/SSH/networking, and which logic belongs to ForgeStack?
7. How can ForgeStack's result be checked manually?

If these cannot be explained, the module may work technically but is not yet fully owned.

## 11. Current Sprint

**Active Sprint:** M1-S1 — Node Inventory / First Runnable ForgeStack Capability

This sprint is the first build session where ForgeStack should begin accumulating persistent product code rather than only infrastructure-learning artifacts.

The immediate objective is deliberately small:

> Create the first runnable ForgeStack capability that knows Node A and Node B as managed infrastructure.

No additional technology should be introduced unless this objective genuinely requires it.
