# 2026-04-29 DeepAgents Kernel Boundary

## Decision

Novi should integrate DeepAgents as an optional execution kernel, not as Novi Core.

Novi Core owns durable project state:

- projects and sessions;
- run creation, status, and inspection;
- agent definitions and per-run participant snapshots;
- tool registry, tool scope, policy, approval, and audit;
- event and tool-call ledgers;
- artifacts and hashes;
- prompt packs and model-call archives;
- memory candidates and review state.

DeepAgents provides execution machinery:

- LLM tool-use loop;
- planning and todo management;
- file-oriented working context;
- subagents for isolated subtasks;
- summarization middleware;
- human-in-the-loop hooks;
- LangGraph durable execution and streaming.

The adapter translates between these layers. DeepAgents may execute work, but it must not become the source of truth for Novi sessions, runs, artifacts, memory, tools, or policies.

## Why Reuse DeepAgents

Continuing to hand-roll a full agent harness would duplicate mature work:

- correct model/tool message loops;
- read/write/edit/list/grep/glob file tools;
- command execution tool behavior;
- planning/todo workflow;
- subagent delegation;
- large-context handling and summarization;
- human approval hooks;
- LangGraph checkpointing and streaming.

Novi should avoid rebuilding that layer unless a requirement cannot be satisfied through the adapter.

## Integration Mode

Use DeepAgents as a normal optional Python dependency, not as vendored source.

Recommended first integration:

```toml
[project.optional-dependencies]
deepagents = [
  "deepagents>=0.5,<0.6",
  "langchain-openai>=0.3",
]
```

DeepAgents currently requires Python `>=3.11`. Novi Core currently declares Python `>=3.9`, so the adapter should either:

1. raise Novi's project Python requirement to `>=3.11`; or
2. keep Novi Core importable on older Python and make `novi run start --kernel deepagents` require a 3.11+ environment.

Preferred path: raise Novi to Python `>=3.11` before implementing the DeepAgents adapter. This keeps the codebase simpler and aligns with current agent ecosystem packages.

Do not vendor or fork DeepAgents initially. Use source checkout only for investigation, debugging, or upstream contribution. Vendor only if a blocking patch is rejected upstream or we need reproducible offline builds later.

## Adapter Boundary

Add a kernel interface:

```text
KernelAdapter.start_run(root, session, run_type, objective, agents, context_pack)
  -> RunExecutionResult
```

Initial kernels:

- `simple`: current deterministic runner.
- `deepagents`: optional adapter using `deepagents.create_deep_agent`.

The DeepAgents adapter should:

- receive Novi prompt parts and selected agent profile;
- expose only Novi-wrapped tools, or map DeepAgents built-ins through Novi policy;
- write DeepAgents final output to `response.md`;
- write model calls to `model_calls.jsonl`;
- write generated/changed files as Novi artifacts;
- mirror DeepAgents tool events into `tool_calls.jsonl` and `events.jsonl`;
- preserve DeepAgents internal checkpointing as execution state, not as the Novi run ledger.

## Tool Boundary

DeepAgents has built-in tools such as todo management, filesystem operations, command execution, and subagent invocation. Novi must classify them before exposure:

| DeepAgents capability | Novi mapping | Default policy |
|---|---|---|
| read/list/glob/grep files | `read_only` | allowed when in agent `tool_scope` |
| write/edit files | `write_local` | workspace-only, approval or explicit permission |
| execute command | `shell` | approval-required or blocked by default |
| task/subagent | `delegate` | allowed only through declared subagent specs |
| memory | `memory_candidate` | can propose only, never directly commit |

For the first adapter spike, prefer passing Novi wrapper tools into DeepAgents instead of exposing unrestricted DeepAgents filesystem or shell tools. Enable DeepAgents built-ins only after their calls can be mirrored into Novi policy and audit records.

## Prompt And Context Boundary

Novi prompt archives are not just a single string. The executor request should preserve modular parts so API prompt caching and human inspection remain predictable:

```text
prompt_parts/
  00-system.md
  10-tool-protocol.md
  20-agent.md
  30-skills.md
  40-tools.md
  50-session.md
  60-memory.md
  70-recent-messages.jsonl
  80-current-task.md
  90-tool-observations.jsonl
```

Stable prefix first:

1. system prompt;
2. tool-use protocol;
3. stable tool descriptions;
4. stable skill instructions;
5. agent profile.

Dynamic suffix later:

1. session summary;
2. recent messages;
3. current objective;
4. recent tool observations.

This helps provider prompt caching because stable prefixes change less often than per-turn state.

## What DeepAgents Does Not Replace

DeepAgents does not replace:

- `.novi/runs/<run_id>/run.yaml`;
- `events.jsonl`;
- `tool_calls.jsonl`;
- `prompt.md` / prompt parts;
- artifact metadata and hashes;
- memory candidate review;
- policy and approval state;
- agent definitions.

DeepAgents subagents are execution helpers. They are not automatically Novi platform agents. Promote a DeepAgents subagent to a Novi agent only when it needs separate audit identity, permissions, tool scope, context scope, or ownership.

## Next Implementation Step

Phase 1.5 should build the adapter skeleton before calling a real model:

- add `KernelAdapter` interface;
- rename current runner as `simple` kernel;
- add optional `deepagents` import path with clear missing-dependency error;
- add `--kernel simple|deepagents`;
- generate prompt parts and hashes;
- define tool mapping rules;
- write `model_calls.jsonl` and `response.md` placeholders;
- keep tests network-free and model-free.
