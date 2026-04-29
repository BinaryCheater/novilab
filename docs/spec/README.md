# Novi Lab Specs

This folder turns the bootstrap summary into reviewable working specs. The goal is to make product and architecture decisions explicit before code is scaffolded.

The specs are written for editing, not as final documentation. Prefer changing the proposal directly when a direction is clear, and moving unresolved tradeoffs into `open-questions.md`.

## Current Specs

Read in this order:

1. `v0-scope.md`: narrows the first useful build.
2. `architecture.md`: defines the core product shape and system boundaries.
3. `tooling-and-modules.md`: discusses candidate tools and module boundaries.
4. `exploration.md`: records the integrated design exploration for configurable agents, workflow iteration, collaboration, and scientific memory.
5. `features.md`: summarizes product features and priorities.
6. `roadmap.md`: outlines directional roadmap phases.
7. `data-model.md`: defines durable objects and records.
8. `cli.md`: defines the first user-facing command surface.
9. `open-questions.md`: lists decisions that still need confirmation.

## Source Background

The source background is `../../novi_lab_repo_bootstrap_summary.md`. It contains the full vision and roadmap. These specs intentionally narrow that document into a practical first build.

## Working Thesis

Novi Lab is a skill-first, session-aware control plane for autonomous research, coding, training, and physical-AI experiments. It organizes work around skills, sessions, runs, tools, memory, artifacts, and policies while keeping external systems as pluggable modules.

## V0 Design Bias

V0 should validate the core loop:

```text
novi init
novi configure model siliconflow --model "..."
novi skill list
novi session create
novi ask "..."
novi run start research "..."
novi run inspect <run_id>
novi run output latest
novi run trace latest
novi memory review
```

The first version should be local-first, inspectable, and easy to revise. It should support agent roles and per-agent scopes, but should not depend on ROS, MCP, a web dashboard, a plugin marketplace, or complex multi-agent orchestration.

## Review Conventions

Use these labels when editing:

- `Proposal`: a recommended direction.
- `Decision`: a direction that is considered accepted.
- `Open`: a question that needs confirmation.
- `Deferred`: a real need that should not block v0.

When reviewing, focus on:

- whether the v0 loop is useful enough;
- whether anything important is missing from the durable records;
- whether any item is too broad for the first implementation;
- whether a term is overloaded or unclear.

## Current Status

The core v0 direction is accepted and Phase 1 implementation is underway.

The current prototype can create a local `.novi/` workspace, list skills, create and open sessions, create runs, archive prompt/context records, store project-local model configuration, execute through the deterministic local kernel or optional DeepAgents kernel, call OpenAI-compatible chat-completions providers, and inspect run output/traces. `novi ask` records multi-turn user/assistant messages and creates auditable runs. Read-only model-triggered tool calls can pass through Novi Tool Runtime and are logged with source attribution.

The spec set is frozen. Do not edit files in this folder unless the user explicitly approves a spec change. Development process and implementation notes belong under `../impl/`.
