# Novi Lab Specs

This folder turns the bootstrap summary into reviewable working specs. The goal is to make product and architecture decisions explicit before code is scaffolded.

The specs are written for editing, not as final documentation. Prefer changing the proposal directly when a direction is clear, and moving unresolved tradeoffs into `open-questions.md`.

## Current Specs

Read in this order:

1. `v0-scope.md`: narrows the first useful build.
2. `architecture.md`: defines the core product shape and system boundaries.
3. `tooling-and-modules.md`: discusses candidate tools and module boundaries.
4. `features.md`: summarizes product features and priorities.
5. `roadmap.md`: outlines directional roadmap phases.
6. `data-model.md`: defines durable objects and records.
7. `cli.md`: defines the first user-facing command surface.
8. `open-questions.md`: lists decisions that still need confirmation.

## Source Background

The source background is `../../novi_lab_repo_bootstrap_summary.md`. It contains the full vision and roadmap. These specs intentionally narrow that document into a practical first build.

## Working Thesis

Novi Lab is a skill-first, session-aware control plane for autonomous research, coding, training, and physical-AI experiments. It organizes work around skills, sessions, runs, tools, memory, artifacts, and policies while keeping external systems as pluggable modules.

## V0 Design Bias

V0 should validate the core loop:

```text
novi init
novi skill list
novi session create
novi run start research "..."
novi run inspect <run_id>
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

The core v0 direction is accepted enough to plan Phase 1. No implementation has been started.

The spec set is frozen. Do not edit files in this folder unless the user explicitly approves a spec change. Development process and implementation notes belong under `../impl/`.
