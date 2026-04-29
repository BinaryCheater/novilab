# 2026-04-29 Phase 1 First Code

## Goal

Create the first executable local core loop for Novi without depending on a real LLM, network search, ROS, MCP, browser automation, or a web dashboard.

## Changed

- Added a uv-managed Python package with the `novi` CLI entrypoint.
- Added filesystem-backed `.novi/` initialization with readable YAML/JSONL records.
- Added built-in skill discovery for `research.review`, `run.audit`, and `memory.curate`.
- Added session creation/list/open/inspect basics.
- Added deterministic `run start` for `research`, `analysis`, and `audit` run types.
- Added append-only run events, separate tool call logs, context pack records, artifact records with SHA-256 hashes, and memory candidates.
- Added `run inspect`, `memory review`, `memory accept`, and `memory reject`.
- Added CLI end-to-end tests for the local core loop.

## Verified

- `uv sync --extra dev`
- `uv run pytest -v`
- Temporary-directory smoke test with `UV_CACHE_DIR=/private/tmp/novilab-uv-cache`:
  - `uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli init`
  - `uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli skill list`
  - `uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli session create "physical-ai literature scan"`
  - `uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli run start research "summarize recent work on physical AI skill learning"`
  - `uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli run inspect <run_id>`
  - `uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli memory review`
  - `uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli memory accept <candidate_id>`
  - `uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli memory review`

## Follow-Up

- Add tool registry commands and approval queue commands.
- Add stronger schema validation for durable records.
- Add `memory reject` smoke coverage outside the automated tests if needed.
- Keep real LLMs, real network search, MCP, browser automation, ROS, TUI/Web, and cowork/team features deferred.
