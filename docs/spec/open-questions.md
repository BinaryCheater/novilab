# Open Questions

These decisions should be resolved or intentionally deferred before implementation.

Suggested review flow:

1. Mark any obvious answer as `Decision`.
2. Move accepted details into the relevant spec.
3. Leave unresolved tradeoffs here as `Open`.

## Product Scope

Decision:

1. The first user is a single local researcher/developer working inside one project directory.
2. The first useful workflow is `research.review`: create an auditable research run, capture records/artifacts, and propose reviewable memory.
3. V0 starts with a deterministic mock/local runner and stable records. A real LLM can be added after the local core loop is inspectable.

## Storage

Decision:

1. V0 starts filesystem-only. SQLite is deferred until query/index needs are proven.
2. Durable structured records must be valid YAML or JSONL from day one.
3. Artifacts should get content hashes when Novi writes or copies the file. Referenced external artifacts may omit hashes until fetched or captured.
4. Runs are stored independently under `.novi/runs/<run_id>/` and referenced from sessions by `run_ids`.

## CLI Behavior

Decision:

1. V0 uses explicit noun/verb commands such as `novi run start`.
2. `novi chat` is deferred until runs and sessions are stable.
3. Commands use the active session by default. Commands that operate on session-scoped state should also accept `--session <id>` once the CLI parser supports shared options.

## Skills

Decision:

1. The minimum accepted `SKILL.md` shape is a readable Markdown file with optional YAML frontmatter. If frontmatter is absent, Novi derives `id` from path/name and `description` from the first paragraph when possible.
2. Built-in skills are read from the installed package by default. `novi init` may create `.novi/skills/` for project-local skills but should not copy built-ins unless explicitly requested later.
3. Project-local skills override built-in skills with the same id, and `novi skill list` should make the override visible.

## Tools And Policy

Decision:

1. `read_only` is allowed by default and recorded. `write_local` is allowed only inside the workspace and must produce an event and artifact/diff reference when it writes. `shell`, `network`, `external_side_effect`, and `physical_world` require approval or are disabled by default in v0.
2. Shell execution can exist in v0 only as a sandboxed tool with approval required by default.
3. Network access is disabled by default for v0 tools. `search_stub` can simulate research outputs without real network access.
4. Failed or blocked tool calls record the requested tool id, args reference, actor/agent, risk, policy result, status, error/block reason, timestamps, and any partial artifact refs.

## Agents

Decision:

1. V0 ships only conceptual `orchestrator` and `auditor` roles. Other roles remain reserved names, not active defaults.
2. V0 agent definitions are project-local defaults with per-run participant snapshots.
3. V0 records per-agent tool visibility and execution permission snapshots, even if enforcement is simple.
4. Multiple model profiles in one run are deferred. V0 records a single model profile per run/participant, usually the mock/local runner profile.

## Memory

Decision:

1. V0 memory candidates are accepted or rejected by the local user through CLI. The auditor may recommend, but not commit memory.
2. Memory candidates should include evidence artifact refs when the claim depends on run output or external content. Pure procedural/project notes may point to the run summary as evidence.
3. Stale memory is represented by a new candidate that supersedes an accepted entry; the old entry remains readable with a superseded reference.

## Later Integrations

Open:

1. Which comes first after v0: MCP client, browser/search, training, simulation, ROS, or IM channel?
2. Should Codex and Claude Code be modeled as tools, modules, workers, or all three depending on use?
3. What is the minimum audit requirement before any physical-world robot command is allowed?
