# Feature Table

Status: Draft, v0 direction accepted

This table summarizes Novi's feature surface. It does not define final priority or implementation order.

## Priority Labels

- `Core`: required for Novi to be Novi.
- `Early`: suitable for early usable versions.
- `Next`: after the core loop stabilizes.
- `Later`: important, but should not block early work.

## Feature Table

| Feature | Priority | User value | Novi responsibility | Dependencies / external projects | Notes |
|---|---|---|---|---|---|
| Project init | Core | Create a Novi workspace for a project | Initialize `.novi`, config, directories, indexes | filesystem, CLI | Use the layout in `data-model.md` |
| Skill registry | Core | Reuse workflows instead of starting from prompts | Load, list, activate `SKILL.md` | filesystem, YAML/frontmatter parser | Keep skill convention compatible |
| Session management | Core | Restore long-lived work context | Session state, summary, active skills/agents | filesystem, SQLite optional | Session is not just chat history |
| Run ledger | Core | Make each execution auditable | Run state, events, tool calls, summary | JSONL, filesystem, SQLite optional | Run is execution/audit unit |
| Tool registry/runtime | Core | Authorize, execute, and record capabilities | Tool specs, schema, execution, result normalization | local modules, MCP later | External tools cannot bypass it |
| Policy/approval | Core | Control risk and side effects | Risk checks, approval gate, blocked state | CLI first, TUI/Web later | Start simple, avoid policy DSL early |
| Artifact store | Core | Track outputs and evidence | Save/index artifacts, hash, metadata | filesystem, object storage later | Memory should reference artifacts |
| Context pack | Core | Control and reproduce model context | Compile session/run/skill/memory/tool context | kernel adapters | Stable system prompt, structured chat messages, and human archive are separate |
| Agent participants | Core | Support different purposes, permissions, tools | Record role, scope, outputs, audit boundary | kernels, policy | Multi-agent-capable, not graph-first |
| Model provider configuration | Early | Connect real API providers reproducibly | Project-local model profile, base URL, secret handling, provider mode | OpenAI-compatible chat completions, Responses later | `.novi/novi.yaml` first; env fallback allowed |
| Project participants | Next | Support multiple human participants in one project | Identity, role, permission, ownership, audit attribution | local identity, GitHub/GitLab later, SSO later | Defer full team model; keep v0 actor fields future-compatible |
| Cowork assignments | Next | Assign scoped work to a human participant or worker | Assignment, context scope, output, comments, review | CLI/TUI/Web, Codex, Claude Code, OpenHands, GitHub/GitLab later | Defer until after the local core loop |
| Simple kernel | Early | Validate core loop without external agent framework | Deterministic execution/test harness | local code | Avoid early DeepAgents lock-in |
| DeepAgents/LangGraph kernel | Early/Next | Support API-backed complex research and long tasks | Kernel adapter, Novi wrapper tools, DeepAgents working-file artifact export, event bridge | DeepAgents, LangGraph | Tool-using SiliconCloud run verified with `MiniMaxAI/MiniMax-M2.5`; next work is streaming/checkpoints and controlled shell/backend mapping |
| Research iteration workflow | Early | Turn a topic or loose materials into hypotheses, experiment plans, and physical-prior candidates | Workflow steps, skills, prompt protocol, artifact export, review boundary | DeepAgents, OpenAI-compatible provider | Phase 1.5 working loop; not the only future research workflow |
| Research/search | Early | Retrieve sources and external information | Search, fetch, source artifacts | `search_stub` first; Tavily/Brave/SearXNG/httpx later | Provider replaceable; broad web search is optional for many tasks |
| Source/result intake | Early | Bring PDFs, papers, web pages, logs, datasets, plots, videos, and experiment results into research context | Preserve originals, generated extraction artifacts, lightweight result packets | Skills, external commands, DeepAgents backend tools, curl/Tavily/browser later | Avoid heavy schema until real tasks prove the need |
| Deep research | Early/Next | Multi-round search, reading, evidence table, report | Research run workflow, evidence artifacts | DeepAgents/LangGraph, search, browser, PDF parser/tools | Hosted provider allowed only as adapter |
| CLI control plane | Early | Inspect and control Novi | init/configure/ask/run/output/trace/inspect/approve/review | Typer, Rich, prompt-toolkit | First control surface; raw JSONL should not be required for normal use |
| Memory review | Early/Next | Make long-term knowledge evidence-based | Candidates, review, commit boundary | Markdown/JSONL, SQLite, vector later | Internal design discussed separately |
| Coding worker | Next | Let external coding agents produce patches/tests | Create coding run, limit scope, capture diffs/logs | Codex, Claude Code, OpenHands | Usually expressed through skills plus worker adapter |
| Browser automation | Next | Handle dynamic pages, screenshots, logged-in pages | Browser tools, screenshots, HTML artifacts | Playwright, browser-use, Browser MCP | Network/login policy needed |
| TUI | Next | Better observe run timeline and approvals | Timeline, tool calls, artifact tree | Textual, Rich | After CLI stabilizes |
| MCP client | Next | Connect external tools/resources | Map MCP tools into Novi Tool Runtime | MCP SDKs, langchain-mcp-adapters | MCP is not foundation |
| Web/API | Later | Dashboard, remote access, collaboration | HTTP API, dashboard surface | FastAPI, Starlette, React/Next.js | Does not duplicate core state |
| Channel adapters | Later | Query, approve, enqueue from IM | Route, status, inspect, approve | Telegram, Discord, Slack, webhook | High-risk actions cannot execute from IM |
| Simulation module | Later | Validate before real robot | Sim run, config, result artifacts | Isaac Sim, MuJoCo, Genesis, PyBullet | Physical-AI module |
| Training module | Later | Manage training jobs and results | Jobs, metrics, checkpoints, budget policy | PyTorch, Lightning, LeRobot, W&B/MLflow | Needs dataset/hash/policy |
| Dataset module | Later | Manage dataset versions and lineage | Dataset index, hash, sample, cleanup | HF Datasets, DVC, lakeFS later | Related to training/eval |
| ROS module | Later | Connect real robot systems | Topics/actions/services, robot state, rosbag | ROS/ROS2 | High risk; needs allowlist/preflight/approval |
| Observability | Later | Debug LLM/tool/workflow behavior | Traces, latency, evals | OpenTelemetry, Langfuse, Phoenix, LangSmith | Does not replace RunLedger |

## Project Participants And Cowork Notes

There are two layers:

- `Project participants`: multiple human participants in one Novi project.
- `Cowork assignments`: scoped session/run tasks assigned to a human participant or worker.

Collaboration with Codex, Claude Code, OpenHands, or other agents can usually be expressed through skills plus worker adapters. It does not need a free-form collaboration system.

The main later product requirements come from multiple humans participating in the same project: identity, permission, ownership, comments, notifications, review state, conflict tracking, and audit attribution.

Cowork lets Novi assign scoped work to humans or external workers and bring the result back into the same session/run audit chain.

Typical cases:

- multiple humans participate in one project with different permissions over sessions, runs, artifacts, and memory review;
- Alice reviews an evidence table while Bob approves memory candidates;
- ask Codex to implement a patch while Novi records context, diff, test logs, and review result;
- ask a human reviewer to review memory candidates or a risky tool call;
- ask a research worker to collect sources before synthesis;
- ask an audit worker to check artifact completeness;
- ask a training/sim worker to run an external job and return metrics.

Minimum principles:

- assignment must be clear;
- human participants must have identity and role;
- context must be controlled;
- tool scope must be limited;
- output must return as Novi artifacts/events/comments/decisions;
- review/approval/comment must be attributable to a person or agent;
- high-risk actions must pass Novi policy;
- external collaborator logs are not Novi source of truth.

V0 rule:

- keep `actor`, `owner`, `reviewed_by`, and approval attribution fields future-compatible;
- do not implement full project participants, cowork assignments, comments, notifications, or team permissions in Phase 1.

## Workflow Evolution Notes

Different concrete tasks may define their own project-local workflows under `.novi/workflows/`.

Workflow and skill self-improvement should use the existing reviewable contribution path:

- agent proposes a patch for `.novi/workflows/`, `.novi/skills/`, or `.novi/knowledge/`;
- Novi records the proposed change as a contribution;
- review/check/accept applies it;
- active workflows are not silently overwritten by an agent.
