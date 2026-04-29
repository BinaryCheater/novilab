# 2026-04-29 Phase 1.2 Tool Runtime And Policy

## Goal

Add the smallest Novi-owned tool runtime boundary before integrating real LLM executors, DeepAgents, MCP, browser tools, shell, or network providers.

## Direction

Tool capability can come from external libraries and frameworks later, but Novi must own the tool governance layer:

- tool registry;
- tool visibility and callability;
- policy decision;
- approval state;
- tool call logging;
- artifact attribution;
- blocked-call evidence.

This keeps future DeepAgents, MCP, browser-use, Playwright, search, shell, and coding-worker integrations behind the same audit and policy boundary.

## Phase 1.2 Scope

- Add a built-in tool registry with `search_stub.query`.
- Add `.novi/tools/` during `novi init` for future project-local tools.
- Add `novi tool list` and `novi tool show <tool_id>`.
- Add a `ToolRuntime` path that checks:
  - whether the tool exists;
  - whether the selected agent has the tool in `tool_scope`;
  - whether policy allows the tool risk class.
- Record allowed and blocked tool calls in `tool_calls.jsonl`.
- Keep `search_stub.query` deterministic and local.

## Out Of Scope

- Real search providers.
- Network fetch.
- Shell execution.
- MCP client/server.
- Approval queue UI.
- Real LLM-driven tool selection.

## Success Criteria

A run can execute `search_stub.query` only when the selected agent has that tool in scope. If the first selected agent lacks tool permission, the call is blocked, recorded, and visible through `novi run inspect`.

## Changed

- Added `src/novi_lab/tools.py` as the first Novi-owned tool runtime boundary.
- Added built-in tool spec for `search_stub.query`.
- Added `.novi/tools/` workspace initialization for future project-local tools.
- Added `novi tool list` and `novi tool show <tool_id>`.
- Routed deterministic runner tool calls through `execute_tool()`.
- Enforced agent `tool_scope` before tool execution.
- Recorded blocked tool calls with `policy_result: blocked` and `block_reason`.
- Updated `run inspect` to display blocked tool reasons.
- Updated run summaries to describe a tool runtime call attempt instead of assuming success.

## Verified

- Red/green test for `novi tool list/show`.
- Red/green test for allowed `search_stub.query` runtime execution.
- Red/green test for blocked calls when the selected agent lacks tool scope.
- Full regression command:
  - `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest -v`
- Temporary-directory smoke flow:
  - `novi init`
  - `novi tool list`
  - `novi tool show search_stub.query`
  - `novi session create "tool run"`
  - `novi run start research "inspect local tool runtime"`
  - `novi run inspect <run_id>`
  - `novi agent create agent_observer --role observer`
  - `novi run start research "attempt scoped search" --agent agent_observer`
  - `novi run inspect <blocked_run_id>`
