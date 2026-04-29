# Development Process

Status: Draft, v0 direction accepted

This document defines how Novi development should be recorded while the project moves from specs into implementation.

## Goal

Development should create inspectable progress records without turning the repo into process overhead. Each functional change should leave enough context to understand what changed, why it changed, how it was verified, and what remains open.

## Development Unit

Use one small functional change as the normal development unit. A functional change should usually map to one of:

- a spec convergence update;
- an implementation plan;
- a CLI command or command group;
- a durable record type;
- a tool/runtime/policy behavior;
- a verification improvement.

Each functional change should be committed when it reaches a coherent checkpoint.

## Required Records

Keep these records during early development:

- frozen specs in `docs/spec/`;
- implementation plans in `docs/plans/`;
- implementation notes and checkpoints in `docs/impl/`;
- durable design decisions inside the relevant spec only after explicit user approval;
- unresolved choices in `docs/spec/open-questions.md` only after explicit user approval.

Implementation entries should be lightweight. They are for recording checkpoints, not duplicating commit history.

## Development Log Shape

Use this shape for implementation checkpoints:

```markdown
# YYYY-MM-DD <short-topic>

## Goal

One or two sentences.

## Changed

- Concrete change.
- Concrete change.

## Verified

- Command or inspection performed.

## Follow-Up

- Remaining issue or `None`.
```

## Phase 1 Start Gate

Phase 1 implementation can start when:

- v0 product scope decisions are marked in `open-questions.md`;
- `v0-scope.md`, `data-model.md`, `cli.md`, and `roadmap.md` agree on the local core loop;
- the first implementation plan exists under `docs/plans/`;
- the plan starts with the filesystem-only, deterministic-runner path;
- no plan task depends on real LLMs, ROS, MCP, browser automation, web dashboard, or team collaboration.

## Verification Discipline

Every implementation checkpoint should include at least one verification command. Early examples:

- schema/unit tests for record creation;
- CLI smoke tests for `novi init`, `novi session create`, and `novi run start`;
- inspection of generated `.novi/` files;
- validation that blocked/failed tool calls are recorded.

## Git Discipline

Use git actively at functional change points. Commit specs, plans, and implementation separately when practical so a future reviewer can distinguish product decisions from code changes.
