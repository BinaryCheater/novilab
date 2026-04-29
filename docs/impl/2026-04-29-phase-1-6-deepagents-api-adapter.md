# 2026-04-29 Phase 1.6 DeepAgents API Adapter

## Goal

Make `novi run start ... --kernel deepagents` execute through DeepAgents when the optional dependency and API credentials are available.

## Current Use

Install optional dependencies:

```bash
uv sync --extra dev --extra deepagents
```

Set a provider key and optional model:

```bash
export OPENAI_API_KEY=...
export NOVI_MODEL=openai:gpt-4.1-mini
```

Run:

```bash
novi init
novi session create "api run"
novi run start research "summarize this project" --kernel deepagents
```

If the selected agent has `model_profile: deterministic-local`, the DeepAgents adapter uses `NOVI_MODEL` or falls back to `openai:gpt-4.1-mini`.

## Implemented

- `--kernel deepagents` imports `deepagents.create_deep_agent`.
- The adapter passes Novi's `prompt.md` as the DeepAgents `system_prompt`.
- The adapter invokes DeepAgents with the run objective as the user message.
- Final output is written to `response.md`.
- Model call status is appended to `model_calls.jsonl`.
- DeepAgents receives Novi-wrapped tools instead of unrestricted native tools.
- Tool wrappers call `execute_tool()` and append records to `tool_calls.jsonl`.

## Exposed Novi-Wrapped Tools

The adapter currently exposes only tools already granted to the selected Novi agent:

- `search_stub.query` as `search_stub_query(query: str)`;
- `filesystem.read` as `filesystem_read(path: str)`;
- `git.status` as `git_status()`.

These wrappers preserve Novi's policy checks and scope enforcement.

## Not Yet Implemented

- Streaming DeepAgents events into `events.jsonl`.
- Mapping DeepAgents built-in filesystem/edit/shell tools into Novi policy.
- Write-local approval flow.
- Shell approval flow.
- Multi-turn session message ingestion.
- DeepAgents subagent specs derived from Novi agents.
- Persisting LangGraph checkpoints under `.novi/`.

## Verified

- Fake `deepagents` module test proves the adapter calls `create_deep_agent(...).invoke(...)`.
- Fake adapter test proves DeepAgents tool calls pass through Novi ToolRuntime.
- Real optional dependency import was verified with:
  - `uv run --python 3.12 --extra dev --extra deepagents python -c "import deepagents; ..."`
- Full deterministic suite remains network/API-free.
