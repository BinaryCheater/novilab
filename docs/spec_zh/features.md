# Feature 表

状态：Draft

本表用于梳理 Novi 的 feature 面，不代表最终优先级或实现顺序。优先级是讨论用标签。

## Feature 优先级说明

- `Core`：没有它就不是 Novi。
- `Early`：适合进入第一批可用版本讨论。
- `Next`：核心闭环稳定后再展开。
- `Later`：重要但不应阻塞前期。

## Feature 表

| Feature | 优先级 | 用户价值 | Novi 负责什么 | 依赖模块/外部项目 | 备注 |
|---|---|---|---|---|---|
| Project init | Core | 给项目建立 Novi 工作区 | 初始化 `.novi`、基础配置、目录和索引 | filesystem, CLI | 具体文件结构另定 |
| Skill registry | Core | 复用工作流，而不是每次从 prompt 开始 | 加载、列出、激活 `SKILL.md` | filesystem, YAML/frontmatter parser | 保持兼容通用 skill 约定 |
| Session management | Core | 长期工作上下文可恢复 | session 状态、summary、active skills/agents | filesystem, SQLite optional | session 不是纯 chat history |
| Run ledger | Core | 每次执行可审计、可回放 | run 状态、events、tool calls、summary | JSONL, filesystem, SQLite optional | run 是执行和审计单位 |
| Tool registry/runtime | Core | 所有能力统一授权、执行、记录 | tool specs、schema、execution、result normalization | local modules, MCP later | 外部工具不能绕过它 |
| Policy/approval | Core | 控制风险和副作用 | risk check、approval gate、blocked state | CLI first, TUI/Web later | 先简单，不做复杂 policy DSL |
| Artifact store | Core | 产物和证据可追踪 | 保存/索引 artifacts、hash、metadata | filesystem, object storage later | memory 应引用 artifacts |
| Context pack | Core | 控制模型上下文和可复现性 | 编译 session/run/skill/memory/tool context | kernel adapters | stable system prompt、structured chat messages 和 human archive 分离 |
| Agent participants | Core | 支持不同用途、权限、工具集的 agent | 记录 role、scope、产出和审计边界 | kernels, policy | multi-agent-capable，不做复杂 agent graph 起步 |
| Model provider configuration | Early | 可复现地连接真实 API provider | project-local model profile、base URL、secret handling、provider mode | OpenAI-compatible chat completions, Responses later | `.novi/novi.yaml` 优先；环境变量可 fallback |
| Project participants | Core/Early | 支持一个 project 中有多个人类参与者 | identity、role、permission、ownership、audit attribution | local identity, GitHub/GitLab later, SSO later | 新增多人协作基础 |
| Cowork assignments | Early | 把受控任务分派给人类 participant 或 worker | assignment、context scope、output、comments、review | CLI/TUI/Web, Codex, Claude Code, OpenHands, GitHub/GitLab later | 不是自由聊天，是受控协作 |
| Simple kernel | Early | 不依赖外部 agent 框架验证核心闭环 | deterministic execution/test harness | local code | 防止过早绑定 DeepAgents |
| DeepAgents/LangGraph kernel | Early/Next | 支持 API-backed 复杂研究和长任务 | kernel adapter、Novi wrapper tools、DeepAgents working-file artifact export、event bridge | DeepAgents, LangGraph | 使用 `MiniMaxAI/MiniMax-M2.5` 已验证 tool-using SiliconCloud run；后续补 streaming/checkpoints 和受控 shell/backend mapping |
| Research iteration workflow | Early | 把 topic 或松散材料转成 hypotheses、experiment plans 和 physical-prior candidates | workflow steps、skills、prompt protocol、artifact export、review boundary | DeepAgents, OpenAI-compatible provider | Phase 1.5 已有 working loop；不是未来唯一 research workflow |
| Research/search | Early | 获取外部资料和来源 | search、fetch、source artifact | `search_stub` first; Tavily/Brave/SearXNG/httpx later | provider 可替换；很多任务不需要广泛网页搜索 |
| Source/result intake | Early | 把 PDF、论文、网页、logs、datasets、plots、videos 和实验结果带入 research context | 保留原始文件、生成 extraction artifacts、轻量 result packets | Skills、外部命令、DeepAgents backend tools、curl/Tavily/browser later | 避免在真实任务证明前引入重 schema |
| Deep research | Early/Next | 多轮搜索、阅读、证据表、报告 | research run workflow、evidence artifacts | DeepAgents/LangGraph, search, browser, PDF parser/tools | 可接 hosted provider，但必须 artifact 化 |
| CLI control plane | Early | 用户可以检查和控制 Novi | init/configure/ask/run/output/trace/inspect/approve/review | Typer, Rich, prompt-toolkit | 第一控制面；正常使用不应要求读 raw JSONL |
| Memory review | Early/Next | 长期知识有证据和审核 | candidates、review、commit boundary | Markdown/JSONL, SQLite, vector later | 内部设计单独讨论 |
| Coding worker | Next | 让外部 coding agent 完成补丁/测试 | 创建 coding run、限制 scope、捕获 diff/logs | Codex, Claude Code, OpenHands | 通常通过 skill + worker adapter 表达 |
| Browser automation | Next | 处理动态网页、截图、登录态页面 | browser tools、screenshots、HTML artifacts | Playwright, browser-use, Browser MCP | 网络和登录需要 policy |
| TUI | Next | 更好观察 run timeline 和 approvals | timeline、tool calls、artifact tree | Textual, Rich | CLI 稳定后 |
| MCP client | Next | 接入外部 tools/resources | MCP tools 映射到 Novi Tool Runtime | MCP SDKs, langchain-mcp-adapters | MCP 不是基础层 |
| Web/API | Later | Dashboard、远程访问、团队协作 | HTTP API、dashboard surface | FastAPI, Starlette, React/Next.js | 不复制 core state |
| Channel adapters | Later | 从 IM 查询、审批、入队 | route、status、inspect、approve | Telegram, Discord, Slack, webhook | 高风险动作不能直接 IM 执行 |
| Simulation module | Later | 真实机器人前做仿真验证 | sim run、config、result artifacts | Isaac Sim, MuJoCo, Genesis, PyBullet | physical-AI 模块之一 |
| Training module | Later | 管理训练任务和结果 | job、metrics、checkpoints、budget policy | PyTorch, Lightning, LeRobot, W&B/MLflow | 需要 dataset/hash/policy |
| Dataset module | Later | 管理数据集版本和 lineage | dataset index、hash、sample、cleanup | HF Datasets, DVC, lakeFS later | 和 training/eval 强相关 |
| ROS module | Later | 接真实机器人系统 | topics/actions/services、robot state、rosbag | ROS/ROS2 | 高风险，必须 allowlist/preflight/approval |
| Observability | Later | 调试 LLM/tool/workflow 行为 | traces、latency、evals | OpenTelemetry, Langfuse, Phoenix, LangSmith | 不替代 RunLedger |

## Project Participants 与 Cowork 说明

这里要区分两层：

- `Project participants`：同一个 Novi project 中的多个人类参与者。
- `Cowork assignments`：把某个 session/run 中的明确任务分派给某个人类 participant 或 worker。

Codex、Claude Code、OpenHands 或其他 agent 的协作，大多可以通过 skill + worker adapter 表达。它们不需要单独定义成自由协作系统。

真正新增的产品要求来自多个人类参与同一个 project：身份、权限、所有权、评论、通知、review 状态、冲突追踪和审计归因。

Cowork 的核心价值是让 Novi 不只是“自己执行”，还可以把受控任务分派给人类或外部 worker，并把结果纳入同一个 session/run 的审计链。

典型场景：

- 多个人类共同参与一个 project，不同人拥有不同 session/run/artifact/memory review 权限；
- Alice 负责审阅 evidence table，Bob 负责批准 memory candidates；
- 让 Codex 实现一个 patch，Novi 记录 context、diff、test logs 和 review 结果；
- 让人类 reviewer 审核 memory candidates 或高风险 tool call；
- 让 research worker 收集 sources，再由 orchestrator 综合；
- 让 audit worker 检查 artifact 是否完整；
- 让 training/sim worker 执行外部 job 并回传 metrics。

Cowork 的最小原则：

- assignment 必须明确；
- 人类 participant 必须有 identity 和 role；
- context 必须可控；
- tool scope 必须受限；
- 输出必须回到 Novi artifacts/events/comments/decisions；
- review/approval/comment 必须可归因到人或 agent；
- 高风险动作必须经过 Novi policy；
- 外部协作者日志不是 Novi source of truth。

## Workflow 演化说明

不同具体任务可以在 `.novi/workflows/` 下定义自己的 project-local workflows。

Workflow 和 skill 自我改进应使用现有 reviewable contribution path：

- agent 提出 `.novi/workflows/`、`.novi/skills/` 或 `.novi/knowledge/` 的 patch；
- Novi 把 proposed change 记录为 contribution；
- review/check/accept 后应用；
- agent 不能静默覆盖 active workflows。
