# 工具选择与模块设定规格

状态：Draft

本规格是一个更接近技术实现讨论的工具文档。它用于整理 Novi 可能需要的模块、外部项目、接入边界和实现方式，但不是最终技术定论，也不规定详细文件结构、数据模型或 milestone。

## 目标

Proposal:

Novi 应被构建为一个 platform core，外接可替换的 execution kernels、tool modules、workers、UI surfaces 和 channel adapters。

Novi Core 应保留这些状态和边界的所有权：

- skills；
- sessions；
- runs；
- context；
- tool registry；
- tool policy；
- artifacts；
- memory flow；
- approvals；
- audit state；
- agent participants；
- module registration。

外部项目可以提供执行能力、检索能力、浏览器能力、编码能力、仿真/训练能力或 UI 能力，但不应成为 Novi sessions、runs、memory、artifacts、permissions 或 policies 的 source of truth。

## 选择原则

Proposal:

选择外部工具时优先考虑：

- 是否适合 local-first 的研究、编码、训练、仿真和 physical-AI workflows；
- 是否能通过 Novi-owned interface 包装；
- 是否支持 inspection、approval、audit、resume 和 replay；
- 是否允许替换 vendor、model、framework 或 runtime；
- 是否能先以最小能力接入，之后逐步增强；
- 是否能清楚表达 side effects 和 risk。

避免引入那些要求 Novi 放弃核心状态所有权的框架。一个外部工具可以执行任务，但不能替代 Novi 的 run ledger、tool policy、artifact store 或 memory review flow。

## 总体模块表

Proposal:

| 模块/能力 | Novi 中负责什么 | 候选外部项目 | 接入边界 |
|---|---|---|---|
| Core runtime | sessions、runs、skills、tools、artifacts、policy、audit 的平台状态 | Python, Pydantic, SQLite, JSONL, filesystem | Novi 自己拥有状态；外部框架只能读写经授权的接口 |
| Agent kernel | 执行 run、流式事件、请求工具、暂停/恢复 | DeepAgents, LangGraph, Simple Kernel, Pi Agent Core | kernel 不拥有 Novi records；工具调用必须经过 Tool Runtime |
| Local project tools | 本地文件、git、shell、Python/notebook 执行 | pathlib, GitPython/dulwich, subprocess/Docker, nbclient, ipykernel | 默认 policy-gated；写入和 shell 必须限制 workspace |
| Research/search | 搜索、网页抓取、来源抽取、引用证据 | Tavily, SearXNG, Brave Search API, httpx, trafilatura, markdownify, Crawl4AI | search/fetch 产出 artifacts；claim 需要 source refs |
| Browser automation | 动态网页、登录后页面、截图、网页交互 | Playwright, browser-use, Browser MCP | 浏览器操作作为高可见 tool；截图/HTML/下载物登记为 artifacts |
| Deep research | 多轮搜索、阅读、证据表、综合报告 | DeepAgents + LangGraph, search modules, web fetch, browser module, PDF parser, optional hosted deep-research providers | 作为 Novi run 的一种执行模式；所有搜索、网页、引用和报告都进入 audit/artifact 流 |
| Documents/PDF | PDF、网页正文、论文、报告解析 | PyMuPDF, pypdf, unstructured, trafilatura, LlamaIndex/Haystack later | parser 是 module tool，不直接写 memory |
| Memory | memory candidate、review、commit、检索 | filesystem/Markdown/JSONL, SQLite, later pgvector/Qdrant | memory 系统单独设计；此处只规定工具边界 |
| CLI | 初始化、inspect、review、approve、run control | Typer, Rich, prompt-toolkit, questionary | 第一控制面；必须能解释 state 和 audit |
| TUI | run timeline、tool calls、approvals、memory candidates、artifacts | Textual, Rich | CLI 稳定后增强；不改变 core state model |
| Web/API | dashboard、HTTP API、webhook、未来多人协作 | FastAPI, Starlette, React/Next.js later | 只是 surface/API；不独立保存权威状态 |
| Channels | Telegram/Discord/Slack/Webhook 接入 | python-telegram-bot, discord.py, slack-sdk, FastAPI webhook | channel 只能路由、询问、审批、检查或入队；高风险执行必须回到 policy |
| MCP client | 接入外部 MCP tools/resources | official MCP SDKs, langchain-mcp-adapters | MCP 是 adapter；MCP tools 仍经过 Novi policy/audit |
| MCP server | 将 Novi 暴露给外部 agent/tools | official MCP SDKs | 后置；等 Novi records/API 稳定后再考虑 |
| Project participants | 同一个 project 中的多个人类参与者 | local identity, GitHub/GitLab later, SSO later | 记录 identity、role、permission、ownership、review、audit attribution |
| Cowork | 在 session/run 中分配受控任务给人类或 worker | CLI/TUI/Web, Codex, Claude Code, OpenHands, GitHub/GitLab, Linear/Jira later | coworker 是受限 participant；任务、上下文、权限、产物和 review 都由 Novi 记录 |
| Coding workers | 外部代码实现、重构、测试、review | Codex, Claude Code, OpenHands | worker 是 run participant/worker；产出 diff/log/artifacts |
| Observability | traces、LLM calls、tool latency、evals | OpenTelemetry, Langfuse, Phoenix, LangSmith | tracing 不能代替 run ledger；用于观测和调试 |
| Physical-AI modules | ROS、仿真、训练、数据集、评估、可视化日志 | ROS/ROS2, Isaac Sim, MuJoCo, LeRobot, Rerun, TensorBoard, MLflow/W&B | 全部作为 modules；Novi 不 robot-first，ROS 不做 base layer |

## 核心语言与运行时

Proposal:

Python 应作为第一版 core runtime。原因是 Novi 的重点领域包括 research、ML、robotics、simulation、training、scientific Python、ROS 和本地自动化。

TypeScript 仍有价值，但更适合后续这些方向：

- web control plane；
- browser-heavy modules；
- Pi 或其他 TypeScript-native agent kernel；
- frontend tooling；
- 某些 MCP/browser 生态适配。

这个选择是优先级，不是永久约束。关键是 Novi Core 的状态和接口要能让其他 runtime 通过 adapter 接入。

## Agent Kernel 候选

Decision:

Novi 应定义 agent kernel adapter boundary。Kernel 可以执行 run、stream events、请求工具、等待 approval、恢复执行，但不能拥有 Novi records。

Phase 1 从 Simple Kernel 或等价 deterministic local runner 起步，并保留这条路径用于 offline validation。当前 Phase 1 prototype 已加入可选 DeepAgents adapter，用于 API-backed runs；更完整的 DeepAgents/LangGraph 能力继续增量推进。

| Kernel | 适合用途 | 不适合做什么 | 当前判断 |
|---|---|---|---|
| Simple Kernel | core loop、测试、无外部依赖验证 | 复杂推理、多步研究 | 应保留，用于避免过早锁定框架 |
| DeepAgents + LangGraph | research、analysis、experiment design、long-running workflows、subagents | 不能直接拥有 memory/artifacts/policy | 已有可选 Phase 1 prototype；后续逐步加深 |
| Pi Agent Core | interactive local coding-like sessions、TS-side experiments | 不宜作为默认 source of truth | 后续 spike |
| Codex/Claude Code/OpenHands | 外部 coding worker | 不应替代 Novi core runtime | 作为 worker/module 接入 |

### DeepAgents + LangGraph 能提供什么

DeepAgents 更像 agent harness，适合处理复杂多步任务。它可以帮助 Novi 获得：

- planning 和 task decomposition；
- research/analysis run 的多步执行循环；
- subagents，用于隔离不同子任务的上下文；
- filesystem working memory，用于长任务草稿和中间材料；
- human-in-the-loop approval；
- tool permission pattern；
- 多模型/多 provider 的灵活性。

LangGraph 更像 stateful agent/workflow runtime。它可以帮助 Novi 获得：

- durable execution；
- checkpoint；
- pause/resume；
- interrupt 后等待用户输入或审批；
- streaming events；
- long-running agent state management。

边界：

- DeepAgents subagents 是 execution-level helpers，不自动等于 Novi platform agents。
- LangGraph checkpoint 是 execution recovery state，不等于 Novi RunLedger。
- DeepAgents filesystem 是 working memory，不等于 Novi ArtifactStore 或 long-term memory。
- DeepAgents tools 必须包装 Novi Tool Runtime，不能直接拿高风险工具。
- DeepAgents built-in filesystem 和 shell tools 应先明确映射到 Novi tools，再决定是否启用；默认不直接暴露高风险 built-ins。
- Stable system、skill、tool instructions 应与动态 conversation turns 分离，以支持 provider request 的 cache-friendly 结构。
- `prompt.md` 是人类可读 archive。`model_messages.jsonl` 和相关 request records 才代表结构化 provider/kernel 边界。
- Novi 仍然拥有 sessions、runs、tools、artifacts、memory、policy 和 audit。

## Model Provider Adapter

Decision:

Phase 1 支持把 model 配置保存到 `.novi/novi.yaml`，环境变量保留为 fallback。

初始 provider modes：

| Provider mode | API shape | 用途 |
|---|---|---|
| `deterministic_local` | no network | Offline tests、inspectable records、不依赖 LLM |
| `openai_chat` | OpenAI-compatible `/v1/chat/completions` | SiliconFlow、DeepSeek-compatible gateways 和其他 compatible providers |
| `openai_responses` | OpenAI Responses API | 预留给支持 Responses semantics 的 provider |

当前 compatible-provider path 使用 chat-completions semantics。只要 provider 实现 compatible tool-call fields，它足够支持基础 messages 和 tool calling；但可能缺少 Responses-only 能力，例如更丰富的 reasoning items、native hosted tools 或 provider-managed state。

LiteLLM 仍是后续有价值的 provider gateway，尤其适合更多供应商和 Anthropic-style APIs，但第一版 SiliconFlow-compatible path 不依赖它。

## Research、Web Search 与 Deep Research

Proposal:

Novi 应把 research 能力拆成可组合模块，而不是只依赖一个“搜索 API”。

| 能力 | 负责什么 | 候选外部项目 | 产出 |
|---|---|---|---|
| `search.query` | 关键词搜索、获取候选来源 | Tavily, Brave Search API, SearXNG, SerpAPI | search result artifact |
| `web.fetch` | 抓取静态网页、保存 HTML/正文 | httpx, requests, trafilatura, markdownify | fetched page artifact |
| `browser.open/read` | 动态网页、JS 渲染页面、登录态页面 | Playwright, browser-use, Browser MCP | screenshot/html/text artifacts |
| `pdf.parse` | PDF/论文解析 | PyMuPDF, pypdf, unstructured | document text artifact |
| `source.extract` | 抽取 claim、quote、metadata、citation | custom parser, LlamaIndex/Haystack later | source note/evidence artifact |
| `deep_research.run` | 多轮检索、阅读、证据表、综合报告 | DeepAgents + LangGraph orchestrating the above tools; optional hosted deep-research provider adapter | research report、evidence table、source bundle |

Deep research 的建议实现方式：

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

关键原则：

- Deep research 是 run type 或 skill-driven workflow，不是外部黑盒。
- Phase 1 可以通过 `search_stub` 模拟 research sources，让 record shape 和 inspection 先稳定，再决定 network/provider。
- 可以接 hosted deep-research provider，但它必须作为 adapter，输出仍要转成 Novi artifacts 和 evidence records。
- 每个重要 claim 应能追溯到 source artifact。
- 浏览器、下载、登录、付费或高频抓取都应有 policy。
- Search provider 可以替换，不能让 Tavily/Brave/SearXNG 任一方成为架构中心。

## Memory 工具边界

Proposal:

Memory 系统会单独设计。本规格只定义工具选型层面的边界。

候选存储/检索工具：

- Markdown/JSONL：本地可读 memory notes、episodic/procedural records；
- SQLite：本地索引、筛选、review queue；
- pgvector/Qdrant：后续向量检索；
- LlamaIndex/Haystack：后续文档索引和检索 pipeline。

边界：

- Agent 或 kernel 可以提出 memory candidates。
- 外部检索库可以帮助 search memory。
- 任何外部库都不能绕过 review flow 直接写 long-term memory。
- Memory 应引用 artifacts/evidence，而不是复制大量不稳定内容。

## CLI、TUI、Web 与 Channel

Proposal:

这些都是 control surfaces，不是 core source of truth。

| Surface | 负责什么 | 候选外部项目 | 接入边界 |
|---|---|---|---|
| CLI | init、run、inspect、approve、memory review、tool inspect | Typer, Rich, prompt-toolkit, questionary | 第一优先级；必须可解释和可审计 |
| TUI | timeline、tool calls、approval queue、artifact tree、memory candidates | Textual, Rich | CLI 稳定后做；读取/操作 Core API |
| Web/API | dashboard、项目管理、团队协作、webhook | FastAPI, Starlette, React/Next.js later | 后置；不复制 core state |
| IM Channels | status、inspect、approve、enqueue run | Telegram, Discord, Slack, webhook | 高风险动作不能直接从 IM 执行 |

建议：

- CLI 先承担主要 control plane。
- TUI 适合当 run/event/tool state 稳定后再做。
- Channel adapter 先只允许 ask/status/inspect/approve/enqueue。
- Web dashboard 不应早于 core state 和 inspect 能力。

## Tool Runtime 与 Policy

Proposal:

所有外部工具调用都应经过 Novi Tool Runtime。无论工具来自 DeepAgents、MCP、browser、shell、Codex worker 还是 channel command，都应进入同一条 policy/audit 路径。

| 风险类型 | 示例 | 默认处理 |
|---|---|---|
| read-only | 读取项目文件、查看 git diff | 记录事件 |
| write-local | 写入草稿、生成 artifact | 限制 workspace，记录 diff/artifact |
| network | search、fetch、API call | 记录 URL/provider，必要时限流 |
| shell | shell command、Python execution | sandbox、timeout、approval |
| external side effect | 发消息、创建 issue、提交任务 | approval |
| physical world | ROS action、机器人控制、真实设备 | preflight、approval、强审计 |

## MCP 位置

Proposal:

MCP 很适合作为工具和资源接入层，但不应成为 Novi 的基础层。

建议路径：

- 先有 Novi Tool Runtime；
- 再接 MCP client，把 MCP tools/resources 映射成 Novi tools/resources；
- 所有 MCP 调用经过 Novi policy、approval、audit；
- 只有当 Novi 自身 records/API 稳定后，再讨论 MCP server。

## Coding Worker 位置

Proposal:

Codex、Claude Code、OpenHands 等适合作为 coding worker。

它们可以负责：

- repo inspection；
- patch generation；
- refactor；
- test execution；
- code review；
- migration tasks。

Novi 负责：

- 创建 coding run；
- 提供 context pack；
- 限制 worker tool/workspace scope；
- 捕获 diff、logs、test results 和 artifacts；
- 审计结果；
- 提出 memory candidates。

## Cowork 位置

Proposal:

Cowork 是 Novi 在一个 project/session/run 中协调协作者完成工作的能力。这里最重要的新增需求不是“让 Codex 和其他 agent 聊天”，而是允许多个真实人类参与同一个 project，并把他们的身份、权限、所有权、评论、审批和审计纳入 Novi。

Codex、Claude Code、OpenHands 或其他 agent 的协作通常可以通过 skill + worker adapter 实现。它们是 coworker 的一种，但不应主导 cowork 的产品定义。

Cowork 不等同于 multi-agent chat。它更接近“把一个 session/run 中的部分工作分派给受控 participant，并把结果带回 Novi 审计”。

| Coworker 类型 | 适合任务 | 候选外部项目/接口 | Novi 需要记录 |
|---|---|---|---|
| Project participant | project ownership、session/run ownership、review、approval、方案选择、实验判断 | local users、CLI/TUI/Web、GitHub/GitLab、Linear/Jira later | identity、role、permission、ownership、assignment、decision、comments |
| Coding worker | patch、refactor、tests、migration | Codex、Claude Code、OpenHands | prompt/context、diff、logs、test result、review status |
| Research worker | source collection、paper screening、evidence table | DeepAgents subagent、browser/search tools、hosted research adapter | sources、notes、artifacts、confidence |
| Experiment worker | run config、training/sim job、metric collection | local runner、cluster job、training module | config、job id、metrics、artifacts |
| Audit worker | policy check、artifact completeness、memory evidence review | Auditor agent、static checker、human reviewer | findings、blocked items、approval state |

Cowork 的核心边界：

- coworker 必须有明确 assignment；
- 人类 participant 必须有可审计 identity；
- project/session/run/artifact/memory candidate 应能表达 ownership 或 reviewer；
- coworker 只能收到最小必要 context；
- coworker 只能使用授权 tool scope；
- coworker 输出必须登记为 artifact、event、comment、decision 或 memory candidate；
- coworker 不能绕过 Novi policy 直接执行高风险动作；
- 外部 worker 的 session/log 不是 Novi source of truth。

多人类参与带来的新增要求：

- permissions：不同成员能执行、审批、review 的动作不同；
- comments：需要对 run、artifact、memory candidate、tool call、assignment 留评论；
- review state：需要 pending/requested_changes/approved/rejected 这类状态；
- notifications：有人被分配 review、审批或任务时需要提醒；
- conflict awareness：多人修改 spec、summary、memory 或 assignment 时要能追踪；
- attribution：所有关键事件都要知道是哪个人或 agent 触发。

可能的用户体验：

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

这些命令只是方向示例，不是最终 CLI 设计。

## Physical-AI 模块位置

Proposal:

Physical-AI 能力应作为模块族，而不是 Novi 的底层假设。

| 模块 | 负责什么 | 候选外部项目 | 接入边界 |
|---|---|---|---|
| ROS | topic/action/service、robot state、rosbag | ROS/ROS2 | 高风险；需要 allowlist、preflight、approval |
| Simulation | 仿真运行、scene/config、结果采集 | Isaac Sim, MuJoCo, Genesis, PyBullet | sim-first；真实机器人前置验证 |
| Training | training job、metrics、checkpoints | PyTorch, Lightning, LeRobot, W&B/MLflow/TensorBoard | 预算、数据集 hash、checkpoint policy |
| Dataset | 数据集索引、版本、清洗、采样 | Hugging Face Datasets, DVC, lakeFS later | lineage 和 hash 重要 |
| Evaluation | benchmark、metric、report | pytest, custom evals, lm-eval-like patterns | eval result 作为 artifact |
| Multimodal logs | 轨迹、视频、状态、可视化 | Rerun, rosbag, TensorBoard | 大文件走 artifact store |

## 暂不在本文定死的内容

Deferred:

- 详细文件结构；
- 具体 data models；
- milestone plan；
- memory 系统内部设计；
- TUI 具体布局；
- channel identity 和 permission 细节；
- plugin marketplace；
- full MCP server；
- robotics execution policy 的完整规则。

这些都是真实需求，但应分别单独制定规格。

## 待确认问题

Open:

1. Browser automation 应进入第一个真实 research module，还是 early research 先只使用 static web fetch？
2. Codex/Claude/OpenHands 应表示为一个 worker category，还是分别建 module/tool adapters？
3. Phase 3 应先做多个人类 project participants，还是先做 coding workers？
4. V0 text search 之后，最小 memory retrieval boundary 是什么？
5. Physical-AI 模块应优先讨论 simulation、training、dataset、ROS 还是 evaluation？
