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

### `novi configure model <provider>`

Stores project-local model configuration in `.novi/novi.yaml`.

Initial providers:

```text
siliconflow
openai-chat
openai-responses
```

Expected behavior:

- `siliconflow` is a convenience profile for SiliconFlow's OpenAI-compatible chat-completions API.
- `openai-chat` configures any provider that exposes an OpenAI-compatible `/v1/chat/completions` endpoint.
- `openai-responses` is reserved for providers that support the OpenAI Responses API.
- API keys may be saved in `.novi/novi.yaml` for local prototypes, but the CLI must not echo secrets back to the terminal.
- Environment variables may remain as fallback, but project config is the preferred reproducible path for Phase 1.

Example:

```text
novi configure model siliconflow --model "deepseek-ai/DeepSeek-V4-Flash" --api-key "..."
```

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

## Ask Command

### `novi ask <message>`

Appends a user message to the active session, creates a run, sends the session's recent user/assistant turns as chat messages, records the assistant response, and prints the response to the terminal.

Expected behavior:

- uses the active session by default;
- supports `--session <id>` when shared session options are available;
- supports `--kernel simple|deepagents`;
- writes user/assistant turns to the session `messages.jsonl`;
- writes run artifacts such as `system_prompt.md`, `model_messages.jsonl`, `prompt.md`, `response.md`, and trace files;
- keeps `prompt.md` as a human-readable archive, not necessarily the exact provider request body.

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
- `model_calls.jsonl`;
- `summary.md`;
- `artifacts/`.

V0 starts with a deterministic mock/local runner and may use `--kernel deepagents` once a compatible model provider is configured. A `research` run should always create inspectable records; with the local runner it can create sample artifacts without requiring a real LLM or network search.

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

### `novi run output <run_id|latest>`

Prints the run's main response or summary artifact. This is the fastest way to see model output after a CLI run.

### `novi run trace <run_id|latest>`

Prints an operator-friendly trace summary for a run.

Should include:

- run id and status;
- model provider, model profile, base URL, and kernel;
- request/archive paths such as `system_prompt.md`, `model_messages.jsonl`, `prompt.md`, and `response.md`;
- DeepAgents message and file archive paths when present;
- tool calls with source attribution such as `manual`, `runner_preflight`, or `deepagents_model`;
- blocked/error information.

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

Prototype note: `novi tool show <tool_id>` may exist as the implemented name until the command surface is normalized.

## Doctor Commands

### `novi doctor model`

Checks the active model configuration without printing secrets.

Should show:

- provider;
- model;
- base URL;
- whether an API key is configured;
- whether the selected provider requires a compatible chat-completions or Responses API path.

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
