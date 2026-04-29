# CLI Spec

Status: Draft, v0 direction accepted

The v0 CLI should expose the core loop before adding TUI, web dashboard, IM channels, or plugin distribution.

## Command Style

Decision:

Prefer explicit nouns and verbs:

```text
novi <noun> <verb> [args]
```

Short aliases can come later after command behavior is stable.

Commands use the active session by default. Session-scoped commands should also support `--session <id>` when practical, but the active-session path is the v0 happy path.

## Project Commands

### `novi init`

Creates a `.novi/` workspace in the current project.

Expected output:

- project config created;
- default directories created;
- built-in skills discovered or copied;
- next suggested command.

### `novi status`

Shows current project, active session, active run, pending approvals, and memory candidates.

## Skill Commands

### `novi skill list`

Lists built-in and project-local skills.

Should show:

- skill id;
- source;
- short description;
- whether it is active in the current session.

### `novi skill inspect <skill_id>`

Shows skill metadata, path, commands, required tools, optional tools, and policies when available.

## Session Commands

### `novi session create <title>`

Creates a session in the current project.

Should create:

- `session.yaml`;
- `summary.md`;
- `messages.jsonl`.

### `novi session list`

Lists sessions with status, updated time, title, and current run.

### `novi session open <session_id>`

Marks a session as active for later commands.

### `novi session inspect <session_id>`

Shows session summary, active skills, run ids, open questions, memory candidates, and artifacts.
It should also show active agent roles when the session has them.

## Run Commands

### `novi run start <type> <objective>`

Creates and starts a run in the active session.

V0 can support these run types first:

```text
research
audit
analysis
```

The command should create:

- `run.yaml`;
- `events.jsonl`;
- `tool_calls.jsonl`;
- `summary.md`;
- `artifacts/`.

V0 starts with a deterministic mock/local runner. A `research` run should create inspectable records and sample artifacts without requiring a real LLM or network search.

### `novi run list`

Lists runs for the current session by status, type, updated time, and objective.

### `novi run inspect <run_id>`

Shows:

- objective;
- status;
- agent participants and roles;
- active skills;
- context packs;
- visible tools;
- tool calls;
- artifacts;
- memory candidates;
- summary;
- errors or blocked approvals.

### `novi run cancel <run_id>`

Cancels a run when possible and records a `RunCancelled` event.

## Memory Commands

### `novi memory review`

Lists memory candidates waiting for review.

### `novi memory accept <candidate_id>`

Commits a memory candidate to the correct memory store and records the decision.

### `novi memory reject <candidate_id>`

Rejects a memory candidate and records the decision note when provided.

### `novi memory search <query>`

Searches project, session, episodic, and procedural memory. V0 may start with simple text search.

## Tool Commands

### `novi tool list`

Lists registered tools and their risk level.

### `novi tool inspect <tool_id>`

Shows schema, module, risk, policies, and approval requirements.

## Approval Commands

### `novi approval list`

Lists pending approvals.

### `novi approval approve <approval_id>`

Approves a pending action and records the approval event.

### `novi approval reject <approval_id>`

Rejects a pending action and records the rejection event.

## Deferred Commands

Deferred:

These are intentionally deferred:

- `novi plugin install`;
- `novi connect telegram`;
- `novi mcp serve`;
- `novi dashboard`;
- direct ROS, simulation, or training commands.

They can be added after the local run loop is stable.
