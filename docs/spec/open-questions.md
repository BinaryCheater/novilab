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
3. V0 starts with a deterministic mock/local runner and stable records. A real LLM is optional once the local core loop is inspectable and project-local provider configuration exists.

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
5. For real research tasks, DeepAgents may use built-in working-file tools and, later, explicitly configured shell/browser/search backends. Novi should not reimplement PDF parsers, search engines, simulators, or trainers when a skill plus external command/tool can do the work.

## Agents

Decision:

1. V0 ships only conceptual `orchestrator` and `auditor` roles. Other roles remain reserved names, not active defaults.
2. V0 agent definitions are project-local defaults with per-run participant snapshots.
3. V0 records per-agent tool visibility and execution permission snapshots, even if enforcement is simple.
4. Multiple model profiles in one run are deferred. V0 records a single model profile per run/participant, usually the mock/local runner profile.

## Model Providers And Context

Decision:

1. Phase 1 supports project-local model configuration in `.novi/novi.yaml`, with environment variables as fallback.
2. OpenAI-compatible chat completions are enough for the first SiliconFlow-compatible path.
3. The model request boundary separates stable `system_prompt.md`, structured `model_messages.jsonl`, human-readable `prompt.md`, and trace records.
4. Recent user/assistant turns are sent as chat messages for multi-round conversation. This follows stateless chat-completions requirements and gives providers a stable prefix for cache-friendly requests where supported.
5. Provider compatibility is model-specific. A model should pass a tool-call smoke test before being used for DeepAgents tool-heavy workflows. SiliconCloud `MiniMaxAI/MiniMax-M2.5` has been verified for model-side Novi wrapper tool calls; a model that emits non-standard tool-call messages should be switched or normalized rather than treated as a Novi Tool Runtime failure.

Open:

1. Should API keys remain in `.novi/novi.yaml`, move to `.novi/secrets.yaml`, use environment variables only, or use OS keychain?
2. Should LiteLLM become the default provider gateway once Anthropic-style APIs or broader provider normalization are required?
3. Which provider-specific cache-control hints, if any, should Novi expose instead of relying only on stable message ordering?

## DeepAgents Boundary

Decision:

1. DeepAgents is an optional execution kernel, not the source of truth for sessions, runs, tools, memory, artifacts, or policies.
2. DeepAgents tool calls should enter Novi Tool Runtime and be logged with source attribution.
3. DeepAgents working files are execution working memory unless Novi explicitly exports them as artifacts.
4. DeepAgents working-file export is accepted as the fastest path for useful research artifacts such as topic briefs, evidence maps, experiment plans, iteration logs, physical-prior candidates, and proposals.
5. Shell, SSH, simulation, and training execution should be exposed through skills and configured DeepAgents/backend tools where possible. Novi records commands, logs, outputs, and artifacts rather than rebuilding those systems.

Open:

1. Which DeepAgents built-in high-risk tools should be enabled directly for trusted local runs, wrapped, or replaced by Novi tools?
2. How should DeepAgents subagents map to Novi platform agents or run participants?
3. Which LangGraph checkpoint/resume features should be surfaced in Novi run records?

## Workflows And Self-Modification

Decision:

1. Document merge, research loop, research iteration, and reflection are all workflows stored under `.novi/workflows/`.
2. Different concrete tasks may define project-local workflows.
3. Workflow and skill self-modification is allowed only through reviewable patch contributions. Agents may propose changes to `.novi/workflows/`, `.novi/skills/`, or `.novi/knowledge/`; accepted contributions apply the change.
4. Agents must not silently modify accepted workflow or skill files during a run.

Open:

1. Should ordinary task runs automatically parse `proposals.json` into workflow/skill patch contributions, or should proposal conversion stay explicit until real usage proves the desired behavior?

## Source And Result Intake

Decision:

1. PDFs, papers, web pages, datasets, logs, plots, videos, and experiment outputs enter first as artifacts.
2. PDF/paper parsing should be skill/tool driven using external commands or libraries; Novi should not own a native parser in v0.
3. Broad web search can use Tavily or another provider later; known URLs can be fetched by `curl` or browser/computer-use skills.
4. Experiment results should begin as lightweight Markdown result packets with optional frontmatter, linked artifacts, observations, interpretation, and next action.
5. Physical-prior candidates can remain in `physical-priors.md` and `proposals.md` until repeated runs show a need for structured prior contributions.

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
