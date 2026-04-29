# 2026-04-29 Phase 1.3 LLM Connect Ready

## Goal

Move Novi to the point where a real LLM executor can be connected without changing the agent, tool, scope, or policy foundations.

## Direction

Before a model chooses tools, Novi needs a usable configuration and tool path:

- agents can be configured from the CLI;
- real read-only local tools exist behind the same runtime boundary as stubs;
- a human can manually call tools through the same scope and policy checks;
- model profiles can be assigned before provider adapters exist.

This phase still does not call a real LLM. It prepares the contract the LLM executor will use.

## Scope

- Add CLI commands for agent configuration:
  - `novi agent grant-tool <agent_id> <tool_id>`;
  - `novi agent revoke-tool <agent_id> <tool_id>`;
  - `novi agent add-skill <agent_id> <skill_id>`;
  - `novi agent set-model <agent_id> <model_profile>`.
- Add built-in read-only tools:
  - `filesystem.read`;
  - `git.status`.
- Add `novi tool call <tool_id> --agent <agent_id> --arg key=value` for manual runtime validation.
- Keep all calls going through scope and policy checks.

## Out Of Scope

- Real LLM calls.
- Prompt compilation.
- Streaming model events.
- Network tools.
- Write-local tools.
- Approval queue UX.

## Success Criteria

A user can create an agent, grant it `filesystem.read`, assign a future model profile, manually call `filesystem.read` through ToolRuntime, and see blocked behavior when the tool is not granted.

## Changed

- Added agent configuration commands:
  - `novi agent grant-tool <agent_id> <tool_id>`;
  - `novi agent revoke-tool <agent_id> <tool_id>`;
  - `novi agent add-skill <agent_id> <skill_id>`;
  - `novi agent set-model <agent_id> <model_profile>`.
- Added built-in read-only tools:
  - `filesystem.read`;
  - `git.status`.
- Added `novi tool call <tool_id> --agent <agent_id> --arg key=value`.
- Kept manual calls behind the same `execute_tool()` scope and policy path as runner calls.
- Added workspace path containment for `filesystem.read`.

## Verified

- Red/green test for agent configuration commands.
- Red/green test for manual `filesystem.read` blocked and allowed behavior.
- Full regression command:
  - `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest -v`
- Temporary-directory smoke flow:
  - `novi init`
  - create `note.md`
  - `novi agent create agent_reader --role reader`
  - `novi agent set-model agent_reader openai:gpt-4.1-mini`
  - `novi tool call filesystem.read --agent agent_reader --arg path=note.md` blocked before grant
  - `novi agent grant-tool agent_reader filesystem.read`
  - `novi tool call filesystem.read --agent agent_reader --arg path=note.md` succeeds
  - `novi tool list` shows `filesystem.read`, `git.status`, and `search_stub.query`
