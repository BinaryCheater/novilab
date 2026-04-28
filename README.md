# Novi Lab

Novi Lab is a skill-first, session-aware control plane for autonomous research, coding, training, and physical-AI experiments.

The repository is currently in specification mode. The working specs live under `docs/spec/`; no implementation has started.

## Start Here

Read the specs in this order:

1. `docs/spec/README.md`
2. `docs/spec/v0-scope.md`
3. `docs/spec/architecture.md`
4. `docs/spec/tooling-and-modules.md`
5. `docs/spec/data-model.md`
6. `docs/spec/cli.md`
7. `docs/spec/open-questions.md`

Chinese draft specs are available under `docs/spec_zh/`.

## Current Direction

V0 should validate a local-first loop:

```text
novi init
novi skill list
novi session create
novi run start research "..."
novi run inspect <run_id>
novi memory review
```

Core concepts are skills, sessions, runs, tools, memory, artifacts, policies, and explicit context packs.

## Repository Notes

- Treat `novi_lab_repo_bootstrap_summary.md` as background material.
- Keep new specs under `docs/spec/` until project scope is confirmed.
- Avoid implementation scaffolding until the specs are accepted or explicitly requested.
