# ForgeStack — Product Direction

## Vision

ForgeStack is a lightweight tool for discovering, understanding, and tracking changes in existing Linux infrastructure.

It aims to help people who manage their own servers understand what is running, where it runs, how components interact, and what has changed — without having to manually reconstruct their infrastructure every time they need to investigate a problem.

**Connect your servers. Discover what is running. Understand what changed. Export the context.**

## Problem and Audience

ForgeStack is intended primarily for individuals who operate Linux servers, homelabs, or self-hosted applications and already have basic Linux and SSH knowledge.

As infrastructure grows, information about workloads, network endpoints, runtime state, and changes becomes scattered across machines and tools. Collecting and organizing this information can be repetitive, especially during troubleshooting.

ForgeStack seeks to reduce that effort without introducing another complex infrastructure stack to maintain.

## Product Direction

The core experience centers on an adaptable workflow:

- **Discover:** Connect to existing infrastructure and automatically identify nodes, workloads, and relevant runtime information with minimal configuration.
- **Understand:** Organize observations into a meaningful infrastructure model, including relationships between components where evidence supports them.
- **Remember and compare:** Preserve useful observations over time and highlight meaningful changes, distinguishing actual changes from incomplete or failed collection.
- **Export and verify:** Provide readable, shareable context for troubleshooting, whether performed by the operator, another person, or an external AI assistant. Recollect evidence to verify the result of a change or fix.

Visual interfaces, periodic discovery, and deeper runtime observation may enhance this workflow when they provide clear user value.

## Design Principles

- **Low-friction adoption:** Reuse existing access and configuration where possible. Deliver useful results before requiring detailed setup.
- **Evidence-first:** Distinguish observed facts, configured relationships, inferred relationships, and unknowns. Make collection limitations visible.
- **Safe by default:** Prefer read-only collection, respect existing permissions, and minimize sensitive data exposure. Additional access or operations require explicit authorization.
- **Small operational footprint:** Avoid unnecessary dependencies, services, agents, and maintenance overhead.
- **AI-independent:** Context should be useful to humans and compatible with external AI tools without requiring an AI provider or API key.
- **Practical usefulness:** Prioritize reduced manual effort and clearer understanding over feature count or visual complexity.

## Development Boundaries

The initial direction is SSH-first discovery of Linux workloads, with systemd as the existing foundation and containerized workloads as an important area to explore. Snapshot comparison and context export are early priorities.

ForgeStack does not currently aim to replace full observability platforms, configuration management systems, or workload orchestrators. Automated deployment, placement, failover, and autonomous remediation are outside the current product focus.

These boundaries guide prioritization rather than permanently restricting the project. Implementation choices, supported environments, interfaces, and future capabilities should evolve according to technical evidence and real usage.

## Validation

ForgeStack's product value is a working hypothesis, not an established claim. Its direction should be tested against practical workflows and existing alternatives.

Success means a user can obtain useful infrastructure context with little setup, understand meaningful changes, and spend less effort investigating problems — without taking on disproportionate maintenance or security costs.

The project should remain open to narrowing its scope, integrating existing tools, or changing its approach when evidence suggests a better solution.
