# Phase 1 Preparation

## Current Direction

Phase 1 should implement the local core loop from the accepted v0 specs:

- filesystem-first `.novi/` workspace;
- explicit CLI commands;
- deterministic mock/local runner;
- independent run records under `.novi/runs/`;
- append-only event and tool call logs;
- artifact registration;
- memory candidate review;
- simple policy/approval boundary.

## Process Constraint

`docs/spec/development-process.md` is frozen. Any future process notes should be recorded in `docs/impl/` unless the user explicitly approves changing that spec.

## Next Step

Write the Phase 1 implementation plan under `docs/plans/phase-1-local-core-loop.md` before scaffolding code.
