# 2026-04-29 Phase 1.4 Prompt Pack And Readable Archive

## Goal

Prepare Novi for a real LLM executor while making run archives human-readable by default.

## External References Reviewed

- OpenAI Agents SDK separates agent instructions, tools, handoffs, tracing, and context management. Novi adopts the separation of instructions/tools/context, but keeps run records and policy owned by Novi.
- LangGraph emphasizes explicit state, messages, tool nodes, and durable execution. Novi keeps this idea as an adapter boundary, while storing its own prompt and run artifacts.
- AutoGen exposes per-agent system messages and tool/workflow participation. Novi maps that to agent definitions and participant snapshots.
- OpenHands and SWE-agent show that coding agents need detailed tool-use rules and inspectable logs. Novi captures this as Markdown prompts plus JSONL tool/event ledgers.
- smolagents keeps prompt templates explicit and tool descriptions visible to the model. Novi does the same in `prompt.md`.

## Storage Principle

Use Markdown for human-facing content and YAML/JSONL only where structure is required.

Current Phase 1.4 run archive:

```text
.novi/runs/<run_id>/
  run.yaml              # structured run state and participant snapshots
  context_pack.yaml     # structured context selection policy
  model_request.yaml    # structured executor request metadata
  prompt.md             # human-readable model input
  response.md           # reserved for future model output
  timeline.md           # human-readable event summary
  events.jsonl          # append-only structured event ledger
  tool_calls.jsonl      # append-only structured tool-call ledger
  summary.md            # human-readable run summary
  artifacts/
    <artifact_id>.yaml
    <artifact_id>-agent-step.md
    <artifact_id>-research-note.md
```

Memory candidates now use:

```text
.novi/memory/candidates/
  <candidate_id>.yaml   # status, evidence refs, review state
  <candidate_id>.md     # claim, evidence, review-readable text
```

## Context Management

Current context handling is explicit but still simple:

- `context_pack.yaml` records what is included and excluded.
- `prompt.md` compiles the system prompt, run objective, active agent, context pack, skills, and visible tools.
- Raw old messages are excluded by default.
- Unreviewed memory is excluded by default.
- Tool visibility comes from the selected agent's `tool_scope`.

This is not yet semantic retrieval or long-context compression. It is the stable interface a future LLM executor will consume.

## Skill Support

Novi supports `SKILL.md` discovery from built-in and project-local skills. Agents store `skill_refs`; the prompt pack includes the selected agent's skill descriptions. Skills are not yet full executable packages with scripts/assets/hooks, but the loading boundary exists.

Built-ins:

- `research.review`
- `run.audit`
- `memory.curate`

## Multi-Turn Dialogue

Current multi-turn support is storage-oriented, not model-oriented:

- sessions have `messages.jsonl`;
- sessions have `summary.md`;
- runs attach to sessions;
- `context_pack.yaml` excludes raw old messages by default.

Missing before real multi-turn agent use:

- CLI commands to append user/assistant messages;
- rolling session summarization;
- retrieval of relevant prior run artifacts/memory;
- prompt inclusion policy for recent messages.

## Tool Calls

All tool calls should go through `execute_tool()`:

- checks tool existence;
- checks selected agent `tool_scope`;
- checks policy;
- executes deterministic/read-only local adapter;
- returns a structured call record for `tool_calls.jsonl`.

Manual tool validation already uses the same path via `novi tool call`.

## Changed

- Added `src/novi_lab/prompts.py`.
- Added a default Markdown system prompt.
- Added per-run `prompt.md` and `model_request.yaml`.
- Added per-run `timeline.md`.
- Added `novi run prompt <run_id>`.
- Added Markdown companions for memory candidates.

## Verified

- Red/green test for run prompt pack and human-readable timeline.
- Red/green test for memory candidate Markdown companion.
- Full regression command:
  - `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest -v`
