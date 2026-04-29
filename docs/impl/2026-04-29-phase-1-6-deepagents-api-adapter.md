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

Configure an OpenAI-compatible chat-completions provider, including SiliconFlow:

```bash
novi configure model siliconflow --model Pro/zai-org/GLM-4.7 --api-key ...
```

This writes local project configuration to `.novi/novi.yaml`.

Environment variables remain as a fallback when no project model config exists:

```bash
export NOVI_MODEL_PROVIDER=openai_chat
export NOVI_API_KEY=...
export NOVI_API_BASE=https://api.siliconflow.cn/v1
export NOVI_MODEL=Pro/zai-org/GLM-4.7
```

Run:

```bash
novi init
novi session create "api run"
novi run start research "summarize this project" --kernel deepagents
```

If the selected agent has `model_profile: deterministic-local`, the DeepAgents adapter uses `NOVI_MODEL` or falls back to `openai:gpt-4.1-mini`.

When `NOVI_MODEL_PROVIDER=openai_chat`, the adapter constructs a `langchain_openai.ChatOpenAI` model with `use_responses_api=False` and passes that model instance to DeepAgents. This path is intended for providers that implement OpenAI chat completions but not OpenAI Responses.

## Implemented

- `--kernel deepagents` imports `deepagents.create_deep_agent`.
- The adapter passes Novi's `prompt.md` as the DeepAgents `system_prompt`.
- The adapter invokes DeepAgents with the run objective as the user message.
- Final output is written to `response.md`.
- Model call status is appended to `model_calls.jsonl`.
- DeepAgents receives Novi-wrapped tools instead of unrestricted native tools.
- Tool wrappers call `execute_tool()` and append records to `tool_calls.jsonl`.
- DeepAgents returned virtual files are exported into `deepagents_files/`, indexed in `run.yaml`, and recorded as artifact metadata.
- `novi configure model ...` stores model provider settings in `.novi/novi.yaml`; environment variables are fallback only.
- `NOVI_MODEL_PROVIDER=openai_chat` or stored `provider: openai_chat` supports OpenAI-compatible chat-completions APIs by passing a configured `ChatOpenAI` instance into DeepAgents.

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
