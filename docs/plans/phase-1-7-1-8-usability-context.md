# Phase 1.7 and 1.8 Usability and Context Plan

> For agentic workers: Use superpowers:test-driven-development for each implementation task. Keep each change independently testable and commit at functional boundaries.

## Goal

Make real API runs observable from the CLI, distinguish Novi preflight tool records from model-initiated tool calls, and add a minimal session-aware `ask` command.

## Architecture

DeepAgents remains the execution kernel. Novi adds thin adapters around model construction, tool calls, trace archival, CLI presentation, and session message storage. Durable Novi records remain filesystem-readable YAML, JSONL, and Markdown.

## Tasks

### Task 1: DeepAgents Trace and Tool Source

Files:

- Modify `src/novi_lab/kernels.py`
- Modify `src/novi_lab/runner.py`
- Modify `src/novi_lab/tools.py`
- Modify `tests/test_cli_core_loop.py`

Steps:

1. Add a failing test proving DeepAgents result messages are archived in `deepagents_messages.jsonl`.
2. Add a failing test proving model-triggered Novi tool calls have `source: deepagents_model`.
3. Add source labels for runner preflight and DeepAgents wrapper calls.
4. Serialize DeepAgents messages conservatively without depending on provider-specific classes.
5. Run focused tests and commit.

### Task 2: CLI Output and Diagnostics

Files:

- Modify `src/novi_lab/cli.py`
- Modify `tests/test_cli_core_loop.py`

Steps:

1. Add a failing test proving `run start` prints the model response for DeepAgents runs.
2. Add `run output <run_id|latest>`.
3. Add `run trace <run_id|latest>` summarizing model calls, DeepAgents messages, and tool calls.
4. Add `doctor model` that reports model provider, model, and base URL without printing secrets.
5. Run focused tests and commit.

### Task 3: Minimal Multi-turn `ask`

Files:

- Modify `src/novi_lab/store.py`
- Modify `src/novi_lab/prompts.py`
- Modify `src/novi_lab/cli.py`
- Modify `tests/test_cli_core_loop.py`

Steps:

1. Add a failing test proving `novi ask "..."` records user and assistant messages in the active session.
2. Add recent session messages to prompt parts as `70-recent-messages.jsonl`.
3. Add `ask` as a convenience command using `research` and `--kernel deepagents` by default when requested.
4. Run focused tests and commit.
