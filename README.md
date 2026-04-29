# Novi Lab

Novi Lab is a skill-first, session-aware control plane for autonomous research, coding, training, and physical-AI experiments.

The repository has started Phase 1 local-core implementation. The accepted working specs live under `docs/spec/`.

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
- Use Superpowers skills for development work when available, especially planning, test-driven development, debugging, and verification-before-completion workflows.
- Use `uv` to manage the Python environment and dependencies. Prefer commands such as `uv sync --extra dev` and `uv run pytest -v`.

## GitHub Workflow

- Do not push directly to the remote `main` branch.
- All GitHub changes intended for `main` must go through a pull request and be merged through GitHub.
- Use development branches such as `dev` or `codex/<topic>` for pushed work.
- Prefer creating a separate branch for each focused development task so review and rollback stay clear.
