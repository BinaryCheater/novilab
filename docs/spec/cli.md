# CLI Spec

Status: Draft, v0 direction accepted, Phase 1.5 updates in progress

The CLI is Novi's first control surface. It should expose the core loop before
TUI, web dashboard, IM channels, or plugin distribution, while also defining the
same object and operation semantics those later surfaces will reuse.

The CLI has two jobs:

1. Provide a usable local operator experience.
2. Keep Novi state inspectable, auditable, and scriptable.

## Command Style

Decision:

Prefer explicit nouns and verbs:

```text
novi <noun> <verb> [args]
```

Examples:

```text
novi session create "physical-ai literature scan"
novi session open <session_id>
novi run inspect latest
novi tool expose filesystem.read agent_reader
```

Short aliases can exist when they improve day-to-day operation without hiding
state. The first accepted alias-style command is:

```text
novi ps
```

Commands use the active session by default. Session-scoped commands should also
support `--session <id>` once shared option handling is stable. The
active-session path remains the happy path.

## Output Conventions

Decision:

CLI output should be human-readable first, but not hostile to scripts.

- Operator overview and list commands may use Rich tables or panels.
- Trace, prompt, output, and record-inspection commands must keep IDs, paths,
  statuses, and block reasons visible as plain text.
- CLI output must never print secrets such as API keys.
- `latest` should refer to the current run in the active session wherever a run
  id is accepted and the meaning is unambiguous.
- Future structured output modes may include `--plain` and `--json`; do not
  require them for Phase 1.5 unless Rich output blocks real usage.

Rich is an accepted presentation dependency for:

- session/run lists;
- operator overview;
- review queues;
- future trace and artifact trees.

TUI/Web should call the same underlying query/control operations as CLI. They
should not create separate state semantics.

## Project And Operator Commands

### `novi init`

Creates a `.novi/` workspace in the current project.

Expected output:

- project config created;
- default directories created;
- default agent profiles created;
- built-in skills discovered;
- next suggested command.

### `novi status`

Shows lightweight workspace/config state.

Should show:

- workspace path;
- active session id;
- active model provider/profile when configured;
- whether API key material is present, without printing it.

`status` is not the main work overview. Use `novi ps` for sessions, runs, and
pending review queues.

### `novi ps`

Shows an operator overview of active work.

Should show:

- active session id, title, and current run;
- session list with active marker;
- recent runs for the active session;
- pending review counts such as memory candidates, approvals, workflow patches,
  and contributions as those queues exist.

This command is intentionally short because it should become the default "where
am I?" command.

### `novi configure model <provider>`

Stores project-local model configuration in `.novi/novi.yaml`.

Initial providers:

```text
siliconflow
openai-chat
openai-responses
```

Expected behavior:

- `siliconflow` is a convenience profile for SiliconFlow's OpenAI-compatible
  chat-completions API.
- `openai-chat` configures any provider that exposes an OpenAI-compatible
  `/v1/chat/completions` endpoint.
- `openai-responses` is reserved for providers that support the OpenAI
  Responses API.
- API keys may be saved in `.novi/novi.yaml` for local prototypes, but the CLI
  must not echo secrets back to the terminal.
- Environment variables may remain as fallback, but project config is the
  preferred reproducible path for Phase 1.

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
- whether it is active in the current session when that state is available.

### `novi skill inspect <skill_id>`

Shows skill metadata, path, commands, required tools, optional tools, and
policies when available.

Implementation note: this may be added after the list/discovery path is stable.

## Agent Commands

Agent commands manage project-local Novi AgentProfiles. These are platform
records, not DeepAgents YAML files. Novi may compile them into DeepAgents
subagents or other kernel/worker bindings.

### `novi agent list`

Lists project-local agents.

Should show:

- agent id;
- role;
- authority level;
- model profile;
- interface mode.

### `novi agent show <agent_id>`

Shows the full project-local AgentProfile.

Should show:

- role and description;
- authority level such as `collaborator`, `reviewer`, or `executor`;
- skill refs and prompt refs;
- tool scope;
- context scope;
- permission scope;
- model profile;
- interface mode;
- output schema;
- kernel binding hints.

### `novi agent create <agent_id> --role <role>`

Creates a project-local agent profile.

Default behavior:

- authority level: `executor`;
- permission scope: `read_only`;
- model profile: `deterministic-local`;
- interface mode: `headless`;
- no tools until granted.

### `novi agent grant-tool <agent_id> <tool_id>`

Adds a tool to the agent's declared tool scope.

Important: this does not by itself make the tool callable. The tool must also
be exposed to the agent through ToolSpec routing.

### `novi agent revoke-tool <agent_id> <tool_id>`

Removes a tool from the agent's declared tool scope.

### `novi agent add-skill <agent_id> <skill_id>`

Adds a skill reference to the agent profile.

### `novi agent set-model <agent_id> <model_profile>`

Sets the agent's model profile.

Phase 1.5 may still execute with one effective model per run, but the profile
should be recorded early for future per-agent routing.

## Tool Commands

Tool commands inspect and configure Novi ToolSpecs and execute manual tool calls
through Novi ToolRuntime.

Final tool availability is the intersection of:

```text
AgentProfile.tool_scope
+ ToolSpec.expose_to
+ policy/risk check
= callable tool
```

### `novi tool list`

Lists registered tools and their risk level.

Should show:

- tool id;
- risk;
- policy;
- short description.

### `novi tool show <tool_id>`

Shows schema, module/source, risk, policy, approval requirements, output
artifact behavior, and `expose_to` routing metadata.

`tool show` is the preferred name for Phase 1.5. `tool inspect` can be added as
an alias later if useful.

### `novi tool expose <tool_id> <agent_id>`

Adds an agent to the tool's `expose_to` routing list.

This is separate from `agent grant-tool`:

- `grant-tool` says the agent is allowed to request the tool in its profile;
- `tool expose` says the tool is routed to that agent;
- ToolRuntime still applies policy and risk checks at execution time.

### `novi tool call <tool_id> --agent <agent_id> --arg key=value`

Executes a manual tool call through Novi ToolRuntime.

The call must record:

- requested tool id;
- agent id;
- args reference;
- risk;
- policy result;
- status;
- source `manual`;
- block reason when blocked.

Useful block reasons include:

```text
tool_not_in_agent_scope
tool_not_exposed_to_agent
policy_not_allowed
path_outside_workspace
executor_not_implemented
```

## Session Commands

### `novi session create <title>`

Creates a session in the current project.

Should create:

- `session.yaml`;
- `summary.md`;
- `messages.jsonl`.

The new session becomes active by default.

### `novi session list`

Lists sessions with active marker, status, current run, and title.

Rich table output is acceptable.

### `novi session open <session_id>`

Marks a session as active for later commands.

This is the primary way to resume previous work. After opening a session,
`novi ask`, `novi run start`, `novi run list`, and `latest` run resolution
operate against that active session.

### `novi session inspect <session_id>`

Shows session summary, active skills, active agents, run ids, open questions,
memory candidates, artifacts, and message log path where available.

## Ask Command

### `novi ask <message>`

Appends a user message to the active session, creates a run, sends the
session's recent user/assistant turns as chat messages, records the assistant
response, and prints the response to the terminal.

Expected behavior:

- uses the active session by default;
- supports `--session <id>` when shared session options are available;
- supports `--kernel simple|deepagents`;
- supports `--agent <agent_id>` for selected participants where practical;
- writes user/assistant turns to the session `messages.jsonl`;
- writes run artifacts such as `system_prompt.md`, `model_messages.jsonl`,
  `prompt.md`, `response.md`, and trace files;
- keeps `prompt.md` as a human-readable archive, not necessarily the exact
  provider request body.

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
- `kernel_bindings.jsonl`;
- `summary.md`;
- `artifacts/`.

Expected options:

- `--kernel simple|deepagents`;
- `--agent <agent_id>` repeatable;
- `--session <id>` once shared session options are available.

V0 starts with a deterministic local runner and may use `--kernel deepagents`
once a compatible model provider is configured. A `research` run should always
create inspectable records; with the local runner it can create sample artifacts
without requiring a real LLM or network search.

### `novi run list`

Lists runs for the current or selected session by status, type, updated time,
and objective.

Rich table output is acceptable.

### `novi run inspect <run_id|latest>`

Shows:

- objective;
- status;
- agent participants, roles, and authority levels;
- active skills;
- context packs;
- kernel bindings;
- visible/callable/unavailable tools when available;
- tool calls;
- artifacts;
- memory candidates;
- summary;
- errors or blocked approvals.

### `novi run prompt <run_id|latest>`

Prints the human-readable prompt archive for the run.

This command is useful for debugging context construction and provider request
shape. It should not imply that `prompt.md` is exactly the provider request
body; structured request records such as `model_messages.jsonl` remain the
provider/kernel boundary.

### `novi run output <run_id|latest>`

Prints the run's main response or summary artifact. This is the fastest way to
see model output after a CLI run.

Markdown rendering through Rich is acceptable as long as IDs and paths remain
copyable.

### `novi run trace <run_id|latest>`

Prints an operator-friendly trace summary for a run.

Should include:

- run id and status;
- model provider, model profile, base URL, and kernel;
- request/archive paths such as `system_prompt.md`, `model_messages.jsonl`,
  `prompt.md`, and `response.md`;
- DeepAgents message and file archive paths when present;
- kernel bindings and unavailable tool reasons;
- tool calls with source attribution such as `manual`, `runner_preflight`, or
  `deepagents_model`;
- blocked/error information.

Rich tables, panels, and trees are especially appropriate here.

### `novi run cancel <run_id>`

Cancels a run when possible and records a `RunCancelled` event.

Implementation note: cancel becomes more meaningful once streaming or
long-running kernels exist.

## Review Commands

### `novi review`

Phase 1.5 candidate:

Shows a unified pending review queue.

Expected queues:

- memory candidates;
- workflow patches;
- knowledge or contribution imports;
- prompt/skill suggestions;
- approvals.

This command should be the human review entrypoint once workflow and
contribution records exist. Until then, `novi memory review` remains the
implemented memory-specific path.

## Memory Commands

### `novi memory review`

Lists memory candidates waiting for review.

### `novi memory accept <candidate_id>`

Commits a memory candidate to the correct memory store and records the decision.

For Phase 1.5, accepted memory may eventually write to or propose updates for a
layered Markdown knowledge vault, but direct automatic mutation should remain
policy-gated.

### `novi memory reject <candidate_id>`

Rejects a memory candidate and records the decision note when provided.

### `novi memory search <query>`

Searches project, session, episodic, procedural, and accepted knowledge memory.
V0 may start with simple text search.

## Knowledge And Contribution Commands

Phase 1.5 candidate:

### `novi import <path-or-url>`

Imports project knowledge, notes, links, paper snippets, prior experiment logs,
or direct agent-session exports.

Expected behavior:

- records the raw input as an artifact or external reference;
- creates a contribution or import record;
- does not automatically write accepted memory or accepted workflow state.

### `novi contribution list`

Lists imported or generated contributions by status, source, target, and title.

### `novi contribution inspect <contribution_id>`

Shows source refs, proposed changes, evidence refs, review state, and target
object.

### `novi contribution accept <contribution_id>`

Accepts or merges a contribution according to its target type and policy.

### `novi contribution reject <contribution_id>`

Rejects a contribution while preserving audit history.

## Workflow Commands

Phase 1.5 candidate:

### `novi workflow draft <objective>`

Creates a reviewable WorkflowSpec-like record or artifact with steps, success
signals, agent assignments, required artifacts, tool requirements, and iteration
triggers.

### `novi workflow list`

Lists workflow records by status, version, title, and updated time.

### `novi workflow inspect <workflow_id>`

Shows workflow steps, assigned agents, required tools, success signals,
accepted patches, pending patches, and related runs.

### `novi workflow patch <workflow_id>`

Creates or shows proposed workflow revisions. Agent-generated workflow changes
must be patches or contributions, not silent edits.

### `novi workflow accept-patch <patch_id>`

Accepts a workflow patch and records the review decision.

### `novi workflow reject-patch <patch_id>`

Rejects a workflow patch and records the review decision.

## Doctor Commands

### `novi doctor model`

Checks the active model configuration without printing secrets.

Should show:

- provider;
- model;
- base URL;
- whether an API key is configured;
- whether the selected provider requires a compatible chat-completions or
  Responses API path.

Future doctor commands may include:

```text
novi doctor workspace
novi doctor tools
novi doctor deepagents
```

## Approval Commands

### `novi approval list`

Lists pending approvals.

### `novi approval approve <approval_id>`

Approves a pending action and records the approval event.

### `novi approval reject <approval_id>`

Rejects a pending action and records the rejection event.

Approval commands are still deferred until write/shell/network or other
approval-gated tools are implemented.

## TUI And Interactive Commands

Deferred:

The CLI should remain the stable command surface before Textual or other TUI
work starts. Future interactive commands may include:

```text
novi session switch
novi review
novi watch latest
```

Potential dependencies:

- Rich for tables, panels, trees, progress, and markdown rendering;
- Textual for a full TUI;
- prompt-toolkit or questionary for selection and confirmation prompts.

## Deferred Commands

Deferred:

These are intentionally deferred:

- `novi plugin install`;
- `novi connect telegram`;
- `novi mcp serve`;
- `novi dashboard`;
- direct ROS, simulation, or training commands.

They can be added after the local run loop and Phase 1.5 review loop are stable.
