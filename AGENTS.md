# Novi Lab Agent Guide

This repository is currently in specification mode.

## Start Here

- Read `docs/spec/README.md` before proposing code or scaffolding.
- Treat `novi_lab_repo_bootstrap_summary.md` as source background, not as an implementation checklist.
- Keep new specs under `docs/spec/` until the project scope is confirmed.

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

## Collaboration Rules

- When adding detail, update the relevant spec and keep cross-links current.
- Put unresolved choices in `docs/spec/open-questions.md`.
- Avoid implementation work until the specs are accepted or the user explicitly asks for scaffolding.
