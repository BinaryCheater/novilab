# Open Questions

These decisions should be resolved or intentionally deferred before implementation.

Suggested review flow:

1. Mark any obvious answer as `Decision`.
2. Move accepted details into the relevant spec.
3. Leave unresolved tradeoffs here as `Open`.

## Product Scope

Open:

1. Who is the first user: a single local researcher/developer, a lab team, or external users?
2. What is the first useful workflow: research review, code maintenance, experiment design, or physical-AI run audit?
3. Should v0 connect to a real LLM immediately, or start with a mock/local runner and stable records?

## Storage

Open:

1. Should SQLite be included in v0, or should v0 start with filesystem-only records?
2. Should all durable records be valid YAML/JSON from day one?
3. Should artifacts always get content hashes in v0?
4. Should sessions contain runs, or should runs be stored independently and referenced by sessions?

## CLI Behavior

Open:

1. Should command style be `novi run start` or shorter forms like `novi run`?
2. Should `novi chat` be in the first milestone, or come after runs and sessions are stable?
3. Should commands require an active session, or allow `--session <id>` everywhere?

## Skills

Open:

1. What is the minimum accepted `SKILL.md` shape?
2. Should Novi copy built-in skills into `.novi/skills/`, or read them from the installed package?
3. Should project-local skills override built-in skills with the same id?

## Tools And Policy

Open:

1. Which risk levels require approval by default?
2. Should shell execution exist in v0, even if sandboxed?
3. Should network access be disabled by default for v0 tools?
4. What should be recorded for failed or blocked tool calls?

## Agents

Open:

1. What default agent roles should exist beyond `orchestrator` and `auditor`?
2. Should agent definitions live globally, per project, per session, or all three?
3. Should tool visibility and tool execution permission be configured per agent from v0?
4. Should one run support multiple model profiles at v0, or should that be a later capability?

## Memory

Open:

1. Who can accept memory candidates: user only, auditor only, or policy-driven auto-accept for low-risk summaries?
2. Should memory candidates require artifact references?
3. How should stale or superseded memory be represented?

## Later Integrations

Open:

1. Which comes first after v0: MCP client, browser/search, training, simulation, ROS, or IM channel?
2. Should Codex and Claude Code be modeled as tools, modules, workers, or all three depending on use?
3. What is the minimum audit requirement before any physical-world robot command is allowed?
