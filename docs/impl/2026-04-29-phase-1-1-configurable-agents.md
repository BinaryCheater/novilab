# 2026-04-29 Phase 1.1 Configurable Agents

## Goal

Add project-local agent definitions and simple sequential multi-agent runs without making DeepAgents, LangGraph, or any other external agent framework a Novi dependency.

## Direction

Novi agents are run participants owned by Novi Core. They are not DeepAgents subagents and are not free-form chat personas. An agent definition exists to make responsibility, tool visibility, context scope, permission scope, model profile, and audit attribution explicit.

DeepAgents remains a later execution kernel adapter. When it is introduced, it should execute through Novi's run, tool, artifact, memory, and policy boundaries rather than replacing them.

## Phase 1.1 Scope

- Add `.novi/agents/` during `novi init`.
- Create default project-local agent definitions for `agent_orchestrator` and `agent_auditor`.
- Add `novi agent list`, `novi agent show <agent_id>`, and `novi agent create <agent_id> --role <role>`.
- Allow `novi run start <type> <objective> --agent <agent_id>` to select one or more agents.
- Snapshot selected agent definitions into `run.yaml`.
- Write one deterministic step artifact and event per selected agent.
- Keep memory proposal reviewable and evidence-based.

## Out Of Scope

- DeepAgents or LangGraph integration.
- Parallel agent graphs.
- Agent-to-agent chat as a product surface.
- Real LLM execution.
- Network search or browser automation.
- Dashboard or TUI.

## Success Criteria

A user can initialize a workspace, define a custom reviewer/researcher/planner agent, start a run with selected agents, inspect the run, and see which agents participated, what scopes they had, and which deterministic artifacts they produced.

## Changed

- Added project-local agent records under `.novi/agents/`.
- Added default `agent_orchestrator` and `agent_auditor` records during `novi init`.
- Added `novi agent list`, `novi agent show <agent_id>`, and `novi agent create <agent_id> --role <role>`.
- Added `novi run start ... --agent <agent_id>` for selected sequential agent participants.
- Added per-agent deterministic step artifacts and `AgentStepCompleted` events.
- Updated run summaries to report agent step artifacts separately from the research note artifact.

## Verified

- Red/green test for default agent records.
- Red/green test for agent create/list/show CLI behavior.
- Red/green test for selected agent sequential run records.
- Full regression test command:
  - `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest -v`
- Temporary-directory smoke flow:
  - `novi init`
  - `novi agent create agent_researcher --role researcher`
  - `novi agent list`
  - `novi session create "agent run"`
  - `novi run start research "compare two planning approaches" --agent agent_researcher --agent agent_auditor`
  - `novi run inspect <run_id>`
