# Novi Lab Agent Guide

This repository is moving from specification mode into Phase 1 planning.

## Start Here

- Read `docs/spec/README.md` before proposing code or scaffolding.
- Treat `novi_lab_repo_bootstrap_summary.md` as source background, not as an implementation checklist.
- Treat `docs/spec/` as the frozen accepted spec set unless the user explicitly approves a spec change.
- Put development process notes and implementation records under `docs/impl/`.

## Product Principles

- Novi Lab is a skill-first, session-aware control plane.
- Skills, sessions, runs, tools, memory, artifacts, and policies are the core concepts.
- External systems such as ROS, simulators, model trainers, Codex, Claude Code, MCP servers, and chat channels are adapters or modules.
- Runs are the primary unit of execution, audit, replay, and evidence.
- Long-term memory must be evidence-based and reviewable.
- Tool use must pass through validation, policy, logging, and artifact capture.

## Scope Discipline

- Do not treat Novi as primarily a multi-agent framework.
- Do not make ROS, MCP, web dashboards, or plugin distribution foundational for v0.
- Prefer a local-first CLI and filesystem-readable records before broader infrastructure.
- Keep specs small, explicit, and easy to revise.

## Project-Level Constraints

- Actively use git to save progress at functional change points.
- Use `uv` to manage the Python environment and dependencies; prefer `uv run` for project commands and tests.
- Prefer creating a separate development branch for each focused task.
- Do not push directly to GitHub remote `main`; changes intended for `main` must go through a pull request and be merged through GitHub.
- Files under `docs/spec/` are frozen. Ask the user before editing, moving, deleting, or adding spec files.
- Development process docs and implementation process notes belong under `docs/impl/`.

## Collaboration Rules

- When adding implementation detail, prefer `docs/impl/` or `docs/plans/` unless the user explicitly approves a spec update.
- Put unresolved implementation choices in `docs/impl/` unless they require an approved spec change.
- Avoid implementation work until the specs are accepted or the user explicitly asks for scaffolding.
