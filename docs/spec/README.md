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

The core v0 direction is accepted. Phase 1 local-core implementation is usable, and Phase 1.5 is converging on an integrated research loop.

The current prototype can create a local `.novi/` workspace, list skills, create and open sessions, create runs, archive prompt/context records, store project-local model configuration, execute through the deterministic local kernel or optional DeepAgents kernel, call OpenAI-compatible chat-completions providers, and inspect run output/traces. `novi ask` records multi-turn user/assistant messages and creates auditable runs. `novi task` creates resumable workflow-backed tasks, advances workflow steps, archives model responses and DeepAgents working files as artifacts, and stops at review gates when pending contributions exist. `novi ingest` preserves imported documents as artifacts and can turn agent proposals into reviewable document patch contributions.

Phase 1.5 now has a real minimal research-iteration loop. The `research-iteration` workflow uses `topic.research`, `document.evidence`, `experiment.iterate`, and `physics.prior.extract` skills to turn a topic or loose materials into topic briefs, evidence maps, hypotheses, experiment plans, iteration logs, physical-prior candidates, and proposals. A SiliconCloud/OpenAI-compatible run with `MiniMaxAI/MiniMax-M2.5` has verified that DeepAgents can call Novi-wrapped tools and export working files into Novi artifacts. Provider compatibility remains model-specific; models that return malformed chat-completions tool-call roles should be switched rather than treated as Novi tool-runtime failures.

Source intake remains intentionally lightweight. PDFs, papers, web pages, experiment logs, datasets, plots, and videos should first enter as source/result artifacts. Skills and DeepAgents may call external commands or future browser/search tools to extract usable Markdown. Novi should not introduce a heavy scientific schema before repeated real tasks prove that natural-language result packets and Markdown review are too loose.

The spec set is frozen unless the user explicitly approves a spec change. When an approved spec change is made, keep `../spec_zh/` aligned with this folder. Development process and implementation notes belong under `../impl/`; user-facing explanatory docs belong under `../guide/`.
