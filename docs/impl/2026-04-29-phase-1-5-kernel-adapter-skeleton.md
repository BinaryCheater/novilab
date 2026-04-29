# 2026-04-29 Phase 1.5 Kernel Adapter Skeleton

## Goal

Prepare Novi to reuse DeepAgents for real multi-turn agent execution without replacing Novi Core.

## Changed

- Raised Novi's Python requirement to `>=3.11`.
- Added optional dependency group:
  - `deepagents>=0.5,<0.6`;
  - `langchain-openai>=0.3`.
- Added `src/novi_lab/kernels.py`.
- Added `novi run start ... --kernel simple|deepagents`.
- Recorded selected kernel in `run.yaml` and `model_request.yaml`.
- Kept the current deterministic runner as the `simple` kernel.
- Added a `deepagents` kernel skeleton that fails clearly when the optional dependency is missing.
- Added cache-friendly prompt parts under each run:

```text
prompt_parts/
  00-system.md
  20-agent.md
  30-skills.md
  40-tools.md
  80-current-task.md
  manifest.yaml
```

- Added `response.md` placeholder.
- Added `model_calls.jsonl` placeholder with `status: not_connected`.

## Current Boundary

The `simple` kernel remains for deterministic tests, archive validation, and policy smoke tests. It is not intended to become a full LLM runtime.

The `deepagents` kernel is the future real execution path. It should provide:

- model loop;
- tool call loop;
- multi-turn execution;
- planning/todo;
- subagents;
- context summarization;
- human-in-the-loop hooks.

Novi still owns:

- run ledger;
- prompt/archive format;
- policy;
- tool scope;
- artifacts;
- memory candidates.

## Next Implementation Step

Implement the DeepAgents adapter behind `--kernel deepagents`:

1. create a DeepAgents agent from Novi prompt parts;
2. expose only Novi-wrapped tools first;
3. map DeepAgents tool events into `tool_calls.jsonl`;
4. write final output to `response.md`;
5. write model metadata to `model_calls.jsonl`;
6. preserve generated files as Novi artifacts.

## Verified

- Red/green test for Python `>=3.11` and optional DeepAgents metadata.
- Red/green test for `--kernel simple`.
- Red/green test for `--kernel deepagents` missing dependency message.
- Red/green test for prompt parts, response placeholder, and model call placeholder.
