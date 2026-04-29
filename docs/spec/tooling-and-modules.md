# Tooling And Modules Spec

Status: Draft, v0 direction accepted

This spec is a technical tooling discussion document. It organizes candidate modules, external projects, integration boundaries, and implementation approaches. It is not a final decision, detailed file layout, data model, or milestone schedule.

## Goal

Proposal:

Novi should be built as a platform core with replaceable execution kernels, tool modules, workers, UI surfaces, and channel adapters.

Novi Core should own:

- skills;
- sessions;
- runs;
- context;
- tool registry;
- tool policy;
- artifacts;
- memory flow;
- approvals;
- audit state;
- agent participants;
- module registration.

External projects may provide execution, retrieval, browser, coding, simulation, training, or UI capability. They should not become the source of truth for Novi sessions, runs, memory, artifacts, permissions, or policies.

## Selection Principles

Proposal:

Prefer external tools that:

- fit local-first research, coding, training, simulation, and physical-AI workflows;
- can be wrapped behind Novi-owned interfaces;
- support inspection, approval, audit, resume, and replay;
- allow vendor, model, framework, or runtime replacement;
- can start with minimal capability and grow later;
- can express side effects and risk clearly.

Avoid frameworks that require Novi to give up ownership of core state. An external tool may execute work, but it should not replace Novi's run ledger, tool policy, artifact store, or memory review flow.

## Module Overview

Proposal:

| Module / capability | Responsibility in Novi | Candidate external projects | Integration boundary |
|---|---|---|---|
| Core runtime | Platform state for sessions, runs, skills, tools, artifacts, policy, audit | Python, Pydantic, SQLite, JSONL, filesystem | Novi owns state; external frameworks use authorized interfaces |
| Agent kernel | Execute runs, stream events, request tools, pause/resume | DeepAgents, LangGraph, Simple Kernel, Pi Agent Core | Kernel does not own Novi records; tool calls go through Tool Runtime |
| Local project tools | Filesystem, git, shell, Python/notebook execution | pathlib, GitPython/dulwich, subprocess/Docker, nbclient, ipykernel | Policy-gated by default; writes and shell are workspace-scoped |
| Research/search | Search, web fetch, source extraction, citation evidence | Tavily, SearXNG, Brave Search API, httpx, trafilatura, markdownify, Crawl4AI | Search/fetch outputs become artifacts; claims need source refs |
| Browser automation | Dynamic pages, logged-in pages, screenshots, web interaction | Playwright, browser-use, Browser MCP | Browser actions are visible tools; screenshots/HTML/downloads become artifacts |
| Deep research | Multi-round search, reading, evidence tables, synthesis reports | DeepAgents + LangGraph, search modules, web fetch, browser module, PDF parser, optional hosted deep-research providers | Runs through Novi; sources and reports become auditable artifacts |
| Documents/PDF | Parse PDFs, pages, papers, reports | PyMuPDF, pypdf, unstructured, trafilatura, LlamaIndex/Haystack later | Parser is a module tool; it does not write memory directly |
| Memory | Memory candidates, review, commit, retrieval | filesystem/Markdown/JSONL, SQLite, later pgvector/Qdrant | Memory system is specified separately; this doc only sets tool boundaries |
| CLI | Init, inspect, review, approve, run control | Typer, Rich, prompt-toolkit, questionary | First control surface; must explain state and audit |
| TUI | Run timeline, tool calls, approvals, memory candidates, artifacts | Textual, Rich | Enhances CLI after state model stabilizes; does not change core state |
| Web/API | Dashboard, HTTP API, webhook, future collaboration | FastAPI, Starlette, React/Next.js later | Surface/API only; does not store authoritative state separately |
| Channels | Telegram/Discord/Slack/Webhook entrypoints | python-telegram-bot, discord.py, slack-sdk, FastAPI webhook | Channels route, ask, approve, inspect, or enqueue; high-risk work returns to policy |
| MCP client | External MCP tools/resources | official MCP SDKs, langchain-mcp-adapters | MCP is an adapter; MCP tools still go through Novi policy/audit |
| MCP server | Expose Novi to external agents/tools | official MCP SDKs | Deferred until Novi records/APIs stabilize |
| Project participants | Multiple human participants in one project | local identity, GitHub/GitLab later, SSO later | Record identity, role, permission, ownership, review, audit attribution |
| Cowork | Assign scoped session/run work to humans or workers | CLI/TUI/Web, Codex, Claude Code, OpenHands, GitHub/GitLab, Linear/Jira later | Coworker is a scoped participant; tasks, context, permissions, outputs, and review are recorded by Novi |
| Coding workers | External code implementation, refactor, test, review | Codex, Claude Code, OpenHands | Worker participates in a Novi run; diffs/logs/results become artifacts |
| Observability | Traces, LLM calls, tool latency, evals | OpenTelemetry, Langfuse, Phoenix, LangSmith | Tracing does not replace RunLedger |
| Physical-AI modules | ROS, simulation, training, datasets, evaluation, multimodal logs | ROS/ROS2, Isaac Sim, MuJoCo, LeRobot, Rerun, TensorBoard, MLflow/W&B | Modules only; Novi is not robot-first and ROS is not the base layer |

## Core Language And Runtime

Proposal:

Python should be the first core runtime because Novi's expected domains include research, ML, robotics, simulation, training, scientific Python, ROS, and local automation.

TypeScript remains useful later for:

- web control plane;
- browser-heavy modules;
- Pi or other TypeScript-native agent kernels;
- frontend tooling;
- some MCP/browser ecosystem adapters.

This is a priority, not a permanent constraint. The important point is that Novi Core state and interfaces allow other runtimes to connect through adapters.

## Agent Kernel Candidates

Decision:

Novi should define an agent kernel adapter boundary. A kernel can execute a run, stream events, request tools, wait for approval, and resume work. It must not own Novi records.

Phase 1 starts with Simple Kernel or an equivalent deterministic local runner and keeps that path for offline validation. A first optional DeepAgents adapter is now part of the Phase 1 prototype for API-backed runs, while advanced DeepAgents/LangGraph features remain incremental work.

| Kernel | Good for | Not good for | Current view |
|---|---|---|---|
| Simple Kernel | Core loop, tests, no-framework validation | Complex reasoning or research | Keep it to avoid early framework lock-in |
| DeepAgents + LangGraph | Research, analysis, experiment design, long-running workflows, subagents | Owning memory/artifacts/policy directly | Optional Phase 1 prototype exists; deepen incrementally |
| Pi Agent Core | Interactive local coding-like sessions, TS-side experiments | Default source of truth | Later spike |
| Codex/Claude Code/OpenHands | External coding worker | Replacing Novi core runtime | Integrate as worker/module |

### What DeepAgents + LangGraph Provide

DeepAgents is closer to an agent harness for complex multi-step tasks. It can provide:

- planning and task decomposition;
- multi-step execution loops for research and analysis runs;
- subagents for context isolation;
- filesystem working memory for drafts and intermediate notes;
- human-in-the-loop approval;
- tool permission patterns;
- multi-model and multi-provider flexibility.

LangGraph is closer to a stateful agent/workflow runtime. It can provide:

- durable execution;
- checkpoints;
- pause/resume;
- interrupt for user input or approval;
- streaming events;
- long-running agent state management.

Boundaries:

- DeepAgents subagents are execution-level helpers, not automatically Novi platform agents.
- LangGraph checkpoints are execution recovery state, not Novi RunLedger.
- DeepAgents filesystem is working memory, not Novi ArtifactStore or long-term memory.
- DeepAgents tools must wrap Novi Tool Runtime and must not receive high-risk native tools directly.
- DeepAgents built-in filesystem and shell tools should be mapped deliberately to Novi tools before being enabled; direct high-risk built-ins are not the default.
- Stable system, skill, and tool instructions should be separated from dynamic conversation turns to support cache-friendly provider requests.
- `prompt.md` is a human-readable archive. `model_messages.jsonl` and related request records represent the structured provider/kernel boundary.
- Novi still owns sessions, runs, tools, artifacts, memory, policy, and audit.

## Model Provider Adapter

Decision:

Phase 1 supports project-local model configuration in `.novi/novi.yaml`, with environment variables as fallback.

Initial provider modes:

| Provider mode | API shape | Use case |
|---|---|---|
| `deterministic_local` | no network | Offline tests, inspectable records, no LLM dependency |
| `openai_chat` | OpenAI-compatible `/v1/chat/completions` | SiliconFlow, DeepSeek-compatible gateways, and other compatible providers |
| `openai_responses` | OpenAI Responses API | Reserved for providers that support Responses semantics |

The current compatible-provider path uses chat-completions semantics. That is enough for basic messages and tool calling when the provider implements compatible tool-call fields, but it may not expose Responses-only capabilities such as richer reasoning items, native hosted tools, or provider-managed state.

LiteLLM remains a useful future gateway for more providers and Anthropic-style APIs, but it is not required for the first SiliconFlow-compatible path.

## Research, Web Search, And Deep Research

Proposal:

Novi should compose research capabilities from modules rather than depend on one search API.

| Capability | Responsibility | Candidate external projects | Output |
|---|---|---|---|
| `search.query` | Keyword search and candidate sources | `search_stub` first; Tavily, Brave Search API, SearXNG, SerpAPI later | Search result artifact |
| `web.fetch` | Static page fetch, HTML/text capture | httpx, requests, trafilatura, markdownify | Fetched page artifact |
| `browser.open/read` | Dynamic pages, JS-rendered pages, logged-in pages | Playwright, browser-use, Browser MCP | Screenshot/HTML/text artifacts |
| `pdf.parse` | PDF and paper parsing | PyMuPDF, pypdf, unstructured | Document text artifact |
| `source.extract` | Extract claims, quotes, metadata, citations | Custom parser, LlamaIndex/Haystack later | Source note/evidence artifact |
| `deep_research.run` | Multi-round search, reading, evidence table, synthesis report | DeepAgents + LangGraph orchestrating the above tools; optional hosted deep-research provider adapter | Research report, evidence table, source bundle |

Recommended deep research flow:

```text
research objective
→ build context pack
→ plan search strategy
→ search.query
→ web.fetch / browser.open / pdf.parse
→ source.extract
→ evidence table
→ synthesis report
→ artifacts registered
→ memory candidates proposed only through memory flow
```

Principles:

- Deep research is a run type or skill-driven workflow, not an external black box.
- Phase 1 may simulate research sources through `search_stub` so record shape and inspection work before network/provider choices.
- A hosted deep-research provider can be integrated, but only as an adapter whose output becomes Novi artifacts and evidence records.
- Important claims should trace back to source artifacts.
- Browser, download, login, paid access, and high-frequency crawling need policy.
- Search providers should remain replaceable.

## Memory Tool Boundaries

Proposal:

The memory system will be specified separately. This spec only defines tooling boundaries.

Candidate storage/retrieval tools:

- Markdown/JSONL for local-readable memory notes and episodic/procedural records;
- SQLite for local indexes, filtering, and review queues;
- pgvector/Qdrant for later vector retrieval;
- LlamaIndex/Haystack for later document indexing and retrieval pipelines.

Boundaries:

- Agents or kernels may propose memory candidates.
- External retrieval libraries may help search memory.
- No external library may bypass review flow and write long-term memory directly.
- Memory should reference artifacts/evidence rather than copy large unstable content.

## CLI, TUI, Web, And Channels

Proposal:

These are control surfaces, not the core source of truth.

| Surface | Responsibility | Candidate external projects | Integration boundary |
|---|---|---|---|
| CLI | Init, run, inspect, approve, memory review, tool inspect | Typer, Rich, prompt-toolkit, questionary | First priority; must be explainable and auditable |
| TUI | Timeline, tool calls, approval queue, artifact tree, memory candidates | Textual, Rich | Built after CLI stabilizes; uses Core API |
| Web/API | Dashboard, project management, collaboration, webhook | FastAPI, Starlette, React/Next.js later | Deferred; does not duplicate core state |
| IM Channels | Status, inspect, approve, enqueue run | Telegram, Discord, Slack, webhook | High-risk actions cannot execute directly from IM |

Recommendations:

- CLI should be the first control plane.
- TUI fits after run/event/tool state stabilizes.
- Channel adapters should initially allow only ask/status/inspect/approve/enqueue.
- Web dashboard should not come before core state and inspectability.

## Tool Runtime And Policy

Decision:

All external tool calls should pass through Novi Tool Runtime. Whether a tool comes from DeepAgents, MCP, browser, shell, Codex worker, or channel command, it should enter the same policy/audit path.

| Risk type | Example | Default handling |
|---|---|---|
| read-only | Read project files, inspect git diff | Record event |
| write-local | Write draft, create artifact | Restrict workspace, record diff/artifact |
| network | Search, fetch, API call | Disabled or approval-gated in v0; record URL/provider when enabled |
| shell | Shell command, Python execution | Sandbox, timeout, approval |
| external side effect | Send message, create issue, submit job | Disabled or approval-gated |
| physical world | ROS action, robot control, real device | Deferred; later requires preflight, approval, strong audit |

## MCP Position

Proposal:

MCP is a good tool/resource adapter, but should not be Novi's foundation.

Suggested path:

- build Novi Tool Runtime first;
- then add MCP client and map MCP tools/resources into Novi tools/resources;
- route all MCP calls through Novi policy, approval, and audit;
- discuss MCP server only after Novi records/APIs stabilize.

## Coding Worker Position

Proposal:

Codex, Claude Code, OpenHands, and similar tools fit as coding workers.

They can handle:

- repo inspection;
- patch generation;
- refactors;
- test execution;
- code review;
- migration tasks.

Novi should handle:

- creating the coding run;
- providing the context pack;
- limiting worker tool/workspace scope;
- capturing diffs, logs, test results, and artifacts;
- auditing results;
- proposing memory candidates.

## Cowork Position

Proposal:

Cowork is Novi's ability to coordinate collaborators inside a project, session, or run. The most important new requirement is not making Codex and other agents chat. It is allowing multiple real human participants in one project and bringing their identity, permissions, ownership, comments, approvals, and audit attribution into Novi.

Collaboration with Codex, Claude Code, OpenHands, or other agents can usually be represented through skills plus worker adapters. They are one coworker type, but they should not define the cowork product surface.

Cowork is not the same as multi-agent chat. It is closer to assigning scoped work inside a session/run to a participant and bringing the result back into Novi for audit.

| Coworker type | Good for | Candidate external projects/interfaces | Novi should record |
|---|---|---|---|
| Project participant | Project ownership, session/run ownership, review, approval, approach choice, experiment judgment | Local users, CLI/TUI/Web, GitHub/GitLab, Linear/Jira later | Identity, role, permission, ownership, assignment, decision, comments |
| Coding worker | Patch, refactor, tests, migration | Codex, Claude Code, OpenHands | Prompt/context, diff, logs, test result, review status |
| Research worker | Source collection, paper screening, evidence table | DeepAgents subagent, browser/search tools, hosted research adapter | Sources, notes, artifacts, confidence |
| Experiment worker | Run config, training/sim job, metric collection | Local runner, cluster job, training module | Config, job id, metrics, artifacts |
| Audit worker | Policy check, artifact completeness, memory evidence review | Auditor agent, static checker, human reviewer | Findings, blocked items, approval state |

Core cowork boundaries:

- a coworker must have a clear assignment;
- a human participant must have auditable identity;
- project/session/run/artifact/memory candidates should express ownership or reviewer;
- a coworker should receive only the minimum required context;
- a coworker should use only authorized tool scope;
- coworker output must be registered as artifact, event, comment, decision, or memory candidate;
- a coworker must not bypass Novi policy for high-risk actions;
- external worker sessions/logs are not Novi source of truth.

New requirements from multiple human participants:

- permissions: different members can execute, approve, or review different actions;
- comments: people need comments on runs, artifacts, memory candidates, tool calls, and assignments;
- review state: pending/requested_changes/approved/rejected-style states are needed;
- notifications: assignees need review, approval, and task updates;
- conflict awareness: concurrent edits to specs, summaries, memory, or assignments should be traceable;
- attribution: important events must record which person or agent triggered them.

Possible UX:

```text
novi project participant list
novi project participant add <user>
novi cowork assign <run_id> --to alice --task "review evidence table"
novi cowork assign <run_id> --to codex --task "implement patch"
novi cowork assign <run_id> --to bob --task "review memory candidates"
novi cowork status <run_id>
novi cowork inspect <assignment_id>
novi cowork accept <assignment_id>
novi cowork reject <assignment_id>
```

These commands are directional examples, not final CLI design.

## Physical-AI Module Position

Proposal:

Physical-AI capabilities should be a module family, not Novi's base assumption.

| Module | Responsibility | Candidate external projects | Integration boundary |
|---|---|---|---|
| ROS | Topics/actions/services, robot state, rosbag | ROS/ROS2 | High risk; needs allowlist, preflight, approval |
| Simulation | Simulation run, scene/config, result capture | Isaac Sim, MuJoCo, Genesis, PyBullet | Sim-first; preflight before real robot |
| Training | Training jobs, metrics, checkpoints | PyTorch, Lightning, LeRobot, W&B/MLflow/TensorBoard | Budget, dataset hash, checkpoint policy |
| Dataset | Dataset index, versions, cleaning, sampling | Hugging Face Datasets, DVC, lakeFS later | Lineage and hash matter |
| Evaluation | Benchmarks, metrics, reports | pytest, custom evals, lm-eval-like patterns | Eval result is an artifact |
| Multimodal logs | Trajectories, video, state, visual logs | Rerun, rosbag, TensorBoard | Large files go through artifact store |

## Not Fixed Here

Deferred:

- detailed file layout;
- concrete data models;
- milestone plan;
- internal memory system design;
- detailed TUI layout;
- channel identity and permission details;
- plugin marketplace;
- full MCP server;
- full robotics execution policy.

These are real needs, but they should be specified separately.

## Open Questions

Open:

1. Should browser automation enter the first real research module, or should early research use only static web fetch?
2. Should Codex/Claude/OpenHands be represented as one worker category or separate module/tool adapters?
3. Which should come first in Phase 3: multiple human project participants or coding workers?
4. What is the minimal memory retrieval boundary after v0 text search?
5. Which Physical-AI module should be discussed first: simulation, training, dataset, ROS, or evaluation?
