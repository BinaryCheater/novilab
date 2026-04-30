# 路线图草案

状态：Draft

本路线图是开发检查用草案，不是交付承诺。它把 Novi 从本地核心闭环逐步扩展到 research、多人类 project collaboration、cowork、memory、UI、MCP 和 physical-AI modules。

每个 phase 都可以作为开发 check 使用：

- `Entry check`：进入这一阶段前最好已经成立的条件。
- `Build check`：开发时要完成或验证的能力。
- `Acceptance check`：可以认为这一阶段基本可用的信号。
- `Defer`：明确不在本阶段解决的内容。

## 路线图原则

Proposal:

- 先建立 Novi 自己的状态和审计边界，再接复杂外部框架。
- 先做到 inspectable，再做到 autonomous。
- 先本地可用，再远程/团队协作。
- 先支持清晰的人类参与者、权限和归因，再支持更复杂的 worker 协作。
- 先记录和审批，再扩大工具权限。
- 先让 modules 可替换，再选择具体 provider。
- 当几个基础能力互相依赖时，用一个 integrated、inspectable 的闭环一起推进，而不是假装它们可以完全独立解决。

## Phase 0：规格收敛

目标：让产品边界、feature 面和技术候选足够清楚，可以开始做最小核心。

Entry check:

- [x] 已读启动说明和 technical tooling 背景文档。
- [x] 已确认 Novi 不是 robot-first、不是 multi-agent-first、不是 Codex replacement。
- [x] 已确认 Novi core 拥有 sessions、runs、tools、artifacts、memory flow、policy 和 audit。

Build check:

- [x] `architecture.md` 描述核心概念和边界。
- [x] `tooling-and-modules.md` 描述候选模块、外部项目和接入边界。
- [x] `features.md` 列出 core/early/next/later features。
- [x] `roadmap.md` 可作为开发检查清单。
- [x] `open-questions.md` 收集仍需确认的问题。
- [x] 中英文 spec 保持结构大体同步。

Acceptance check:

- [x] 能解释 Novi 的一句话定位。
- [x] 能解释 v0 为什么不依赖 ROS/MCP/Web dashboard/复杂 multi-agent graph。
- [x] 能解释 Codex/Claude/OpenHands 为什么是 worker，而不是 Novi source of truth。
- [x] 能解释多个人类 project participants 和 agent participants 的区别。

Defer:

- [x] 不定具体交付日期。
- [x] 完整 memory internals 后置。
- [x] 完整 cowork/team model 后置。

## Phase 1：本地核心闭环

目标：让 Novi 可以创建、执行、记录、检查一个本地 run，同时保留 deterministic local execution，并提供可选 API-backed DeepAgents 路径。

Entry check:

- [x] Phase 0 的核心边界已经可接受。
- [x] 已决定先做 local-first。
- [x] 已决定第一控制面是 CLI。
- [x] 已决定 Simple Kernel 或等价 fallback 存在。
- [x] Phase 1 implementation plan 已存在于 `docs/plans/`。

Build check:

- [x] project init 能创建本地 Novi workspace。
- [x] skill registry 能发现和列出 `SKILL.md`。
- [x] session 能创建、打开、列出、保存 summary。
- [x] run 能创建、更新状态、完成、失败。
- [x] run ledger 能记录 append-only events。
- [x] tool call log 与普通 event 分开。
- [x] model call log 与 tool call 分开。
- [x] artifact store 能登记本地产物。
- [x] tool registry 能列出本地 tools。
- [x] policy/approval 至少能表达 require approval / blocked。
- [x] context pack 和 prompt archives 能被生成并保存。
- [x] CLI 能 inspect project/session/run/tool/artifact。
- [x] Simple Kernel 能产生 deterministic research/analysis/audit run events。
- [x] project-local model config 能写入并检查。
- [x] OpenAI-compatible chat-completions provider 可用于 API-backed runs。
- [x] `novi ask` 能记录多轮 user/assistant messages 并创建 runs。
- [x] `novi run output` 和 `novi run trace` 能展示模型输出和执行 trace。
- [x] 可选 DeepAgents kernel 能调用 compatible provider，并把 read-only tool calls 路由到 Novi Tool Runtime。
- [x] memory candidates 能 proposed/listed/accepted/rejected。
- [x] development checkpoints 记录到 git，必要时记录到 `docs/impl/`。

Acceptance check:

- [x] 用户能运行最小链路：init、skill list、session create、run start、run inspect。
- [x] 用户能配置 compatible model provider，并运行 API-backed smoke test。
- [x] 一个 run 的 objective、status、events、tool calls、model calls、artifacts 都能被查看。
- [x] 用户能通过 CLI output/trace 回答“发生了什么、为什么、产物在哪里”。
- [x] 高风险或未授权工具不会绕过 policy 直接执行。
- [x] 即使没有真实 LLM，也能验证 core records。

Defer:

- [ ] 不接真实机器人。
- [ ] 不做完整 memory 系统。
- [ ] 不做 TUI/Web。
- [ ] DeepAgents advanced streaming、checkpoint/resume、subagent mapping、built-in write/shell tool mapping 后置。
- [ ] 不做复杂 permission matrix。

## Phase 1.5：Integrated Exploration Track

目标：在不放弃 local-first 和 inspectable core 的前提下，一起探索 configurable agents、workflow iteration、contribution review 和 scientific memory。

假设：这些基础能力互相依赖。Novi 不应把它们拆成互不相关的后置 phases，而应用一个小而完整的 loop 验证边界：

```text
import knowledge
-> compile/select agent profiles
-> generate or update workflow
-> execute scoped run
-> produce artifacts, workflow patches, and memory candidates
-> review/merge selected contributions
-> next run consumes accepted records
```

这一阶段应把“物理先验”等领域研究内容视为由 skill 定义、由文档库表达的知识，
而不是 Novi core object type。Novi 负责围绕这些内容提供 processing、review、
patch、lineage 和 context 机制。

Entry check:

- [ ] Phase 1 run ledger、artifact store、tool runtime 和 memory candidate flow 可用。
- [ ] `exploration.md` 已明确探索对象和 EvoScientist/DeepAgents 参考差异。
- [ ] Agent profile、workflow、contribution、memory 四个方向已各自定义一个最小可检查边界。
- [ ] 已接受这不是完整 multi-agent platform，也不是完整 collaboration system。

Build check:

- [ ] 能定义一个 project-local agent profile，包含 prompt refs、tool scope、permission scope、model profile 和 output contract。
- [ ] 能把 agent profile 编译或映射到当前 kernel，而不把 kernel-specific representation 当成 source record。
- [ ] 能记录一个 generated workflow 或 workflow artifact，包含 steps、success signals 和 iteration triggers。
- [ ] Agent 可提出 workflow patch，但不能静默修改 accepted workflow。
- [ ] 用户导入知识时形成 artifact 和 contribution，而不是直接进入 memory。
- [ ] Scoped agent 可把 imported knowledge 处理成 analysis note；当用户提供明确 target 时，可生成针对 document library、workflow records 或 project-local skills 的 patch contribution。
- [ ] 如果没有提供 patch target，document processing 可以建议 target，但不生成可 apply 的 patch。
- [ ] Patch contribution 可 dry-run/check、accept 后 apply、reject、request changes，或在 apply 失败时标记 conflict 且不修改 target files。
- [ ] Agent-generated patch contributions 必须携带来自 imports、runs、artifacts、analysis notes、accepted knowledge 或 worker bundles 的 source refs；human-authored changes 可以更宽松，但仍需 attribution。
- [ ] Agent 可从导入知识和 run artifacts 中产生 claim/memory candidate。
- [ ] Reviewer/user 可 accept/reject/request changes，并把 decision 写入 ledger。
- [ ] Accepted memory 或 accepted workflow revision 可进入下一次 run 的 context pack。
- [ ] Direct DeepAgents-like session 的输出可被导入为 artifacts/contributions，但不能绕过 review。

Acceptance check:

- [ ] 一次 demo 能展示 imported knowledge、agent profile、workflow patch、review decision 和 evidence-backed memory candidate 的完整链路。
- [ ] 一次 demo 能展示 imported document 被处理成 analysis note 和针对明确 target 的 document patch，并通过 review 被 accept/reject。
- [ ] `novi run inspect` 或等价 inspect surface 能解释每个状态变化来自谁、依据什么 evidence、是否被接受。
- [ ] DeepAgents/LangGraph checkpoint 可用于 execution recovery，但 Novi run ledger 仍是 source of truth。
- [ ] 新增对象没有迫使 Novi 立即实现 realtime collaboration、full workflow engine 或完整 knowledge graph。

Defer:

- [ ] 不做完整 team workspace。
- [ ] 不做复杂 agent marketplace。
- [ ] 不做实时多人编辑。
- [ ] 不做完整 workflow scheduler。
- [ ] 不做完整 scientific knowledge graph。
- [ ] 不为“物理先验”等项目特定研究概念建立框架内置对象。
- [ ] 不把 EvoScientist 的 channel/memory/sandbox 设计整体照搬进 Novi。

## Phase 2：Research 与 Deep Research

目标：让 Novi 能处理真实研究任务，产生可追溯 sources、evidence table、report 和 artifacts。

Entry check:

- [ ] Phase 1 的 run ledger、artifact store、tool runtime 可用。
- [ ] Phase 1.5 已澄清哪些 agent、workflow、contribution、memory 对象是真需求，哪些只是探索脚手架。
- [ ] search/web/pdf/browser 的风险边界已写入 tooling spec。
- [ ] 已决定第一版 search 使用 hosted provider、self-hosted provider，还是 stub。

Build check:

- [ ] `search.query` 能返回候选来源并保存 search result artifact。
- [ ] `web.fetch` 能保存 HTML/text artifact。
- [ ] `pdf.parse` 或 document parser 能提取论文/报告正文。
- [ ] `source.extract` 能提取 metadata、citation、claim 或 quote。
- [ ] research run 能生成 evidence table。
- [ ] research run 能生成 synthesis report。
- [ ] report 中的重要 claim 能关联 source artifact。
- [x] DeepAgents/LangGraph kernel adapter 已作为 serious kernel 候选接入。
- [x] 初始 DeepAgents read-only tools 已通过 Novi Tool Runtime 包装。
- [ ] DeepAgents advanced built-ins、streaming、checkpoints 和 subagent mapping 需继续有控制地接入。
- [ ] browser automation 的接入条件明确，即使暂不实现。

Acceptance check:

- [ ] 用户可以发起 research/deep-research run。
- [ ] run 产出 sources、evidence table、report、artifacts。
- [ ] provider 可替换，不把 Tavily/Brave/SearXNG/hosted deep research 作为架构中心。
- [ ] 重要网页/PDF/浏览器结果可回看。
- [ ] deep research 不是外部黑盒，输出进入 Novi audit/artifact 流。

Defer:

- [ ] 不要求完整 browser automation。
- [ ] 不要求 memory 自动吸收 research 结论。
- [ ] 不要求多用户协作 UI。
- [ ] 不做付费/登录/高频抓取的完整策略，只保留 policy 边界。

## Phase 3：Project Collaboration 与 Cowork

目标：支持一个 project 中的多个人类参与者，并能把明确任务分派给人类 participant 或外部 worker。

Entry check:

- [ ] session/run/artifact 至少能表达 owner/reviewer 的概念。
- [ ] events 能记录 actor attribution。
- [ ] policy/approval 已有基本状态。
- [ ] 已确认 Codex/Claude/OpenHands 协作通常通过 skill + worker adapter 表达。

Build check:

- [ ] project participant 能被添加、列出、禁用或标记 inactive。
- [ ] participant 有 identity、display name、role。
- [ ] project/session/run/artifact/memory candidate 能记录 owner/reviewer。
- [ ] comments 可以附着到 run、artifact、tool call、memory candidate、assignment。
- [ ] review state 支持 pending/requested_changes/approved/rejected。
- [ ] approval 能归因到具体 human participant。
- [ ] cowork assignment 能创建、列出、检查、接受、拒绝。
- [ ] assignment 有 assignee、task、context scope、status、result refs。
- [ ] human review/approval flow 能走通。
- [ ] coding worker adapter 的边界明确：context、workspace/tool scope、diff/log capture。
- [ ] worker 输出能登记为 artifact/event/comment/decision。
- [ ] 外部 worker 的 session/log 不作为 Novi source of truth。

Acceptance check:

- [ ] 一个 project 可以有多个可识别的人类参与者。
- [ ] 不同 participant 可以拥有不同 review/approval 责任。
- [ ] 用户能看到谁创建、审批、评论、接受或拒绝了某个动作。
- [ ] 用户能把 review/coding/research 子任务分配出去并检查结果。
- [ ] Codex/Claude/OpenHands 结果能被审阅，而不是自动成为事实。

Defer:

- [ ] 不做完整组织/团队管理。
- [ ] 不做 SSO。
- [ ] 不做复杂实时协同编辑。
- [ ] 不做完整通知系统，只保留 notification 事件和接口边界。
- [ ] 不把 agent-to-agent chat 做成核心产品面。

## Phase 4：Memory Review

目标：建立 evidence-based memory 的实际闭环，让长期知识可审阅、可追溯、可修正。

Entry check:

- [ ] run/artifact/source refs 已稳定。
- [ ] comments/review state/actor attribution 至少有基础形态。
- [ ] 已单独讨论 memory 类型和写入规则。

Build check:

- [ ] agent/kernel/worker 可以提出 memory candidate。
- [ ] memory candidate 包含 claim、scope、confidence、evidence refs。
- [ ] memory review queue 可列出待审内容。
- [ ] human participant 可以 accept/reject/request changes。
- [ ] accepted memory 写入 project/session/episodic/procedural store。
- [ ] rejected/superseded memory 保留 decision record。
- [ ] memory search 能检索已接受 memory。
- [ ] memory 不复制大 artifacts，只引用 evidence。
- [ ] memory 写入事件进入 run/session audit。

Acceptance check:

- [ ] agent 不能直接写长期 memory。
- [ ] 每条长期 memory 能追溯到 evidence/run/artifact。
- [ ] 用户能审阅、接受、拒绝和修正 memory。
- [ ] stale 或 superseded memory 不会静默覆盖证据。

Defer:

- [ ] 不要求向量检索一开始存在。
- [ ] 不做复杂知识图谱。
- [ ] 不做自动长期记忆。
- [ ] 不做跨项目全局 memory 合并。

## Phase 5：更强 Control Surfaces

目标：在 CLI 稳定后，提高观察、审批、review、cowork 和 artifact 浏览效率。

Entry check:

- [ ] CLI inspect 已能解释核心状态。
- [ ] run events/tool calls/artifacts/comments/review state 已稳定。
- [ ] 已知道哪些操作最需要 UI 提效。

Build check:

- [ ] TUI 或增强 CLI 能显示 run timeline。
- [ ] 能查看 tool call table。
- [ ] 能查看 approval queue。
- [ ] 能查看 cowork assignments。
- [ ] 能查看 comments/review state。
- [ ] 能浏览 artifact tree。
- [ ] 能查看 memory candidates。
- [ ] Web/API 的边界明确：surface，不复制 core state。
- [ ] Channel adapter 的边界明确：ask/status/inspect/approve/enqueue。

Acceptance check:

- [ ] 用户不需要翻 raw JSONL 就能理解当前状态。
- [ ] approvals、comments、cowork assignments 有统一入口。
- [ ] UI 操作和 CLI 操作进入同一 core API/audit path。
- [ ] IM/channel 不直接执行高风险动作。

Defer:

- [ ] 不做完整生产级 dashboard。
- [ ] 不做复杂团队权限后台。
- [ ] 不做多租户。
- [ ] 不做移动端体验。

## Phase 6：External Ecosystem

目标：让 Novi 作为控制平面接入更多外部工具生态，同时保持 policy/audit/source-of-truth 边界。

Entry check:

- [ ] Tool Runtime 和 Policy Gate 已稳定。
- [ ] Module boundary 已稳定。
- [ ] 外部工具结果能被 artifact/event 化。

Build check:

- [ ] MCP client 能把外部 tools/resources 映射进 Novi。
- [ ] MCP calls 经过 Novi policy、approval、audit。
- [ ] coding worker category 可替换。
- [ ] observability 能记录 traces、latency、LLM/tool metadata。
- [ ] traces 不替代 run ledger。
- [ ] plugin/module packaging 的基本边界清楚。
- [ ] MCP server 是否需要进入下一阶段已有判断。

Acceptance check:

- [ ] 外部 tools/resources 可以被 Novi 安全调用。
- [ ] 外部 worker/provider 可以替换。
- [ ] 调试信息足够定位模型、工具、context 或 policy 问题。
- [ ] Novi source of truth 仍是 core records。

Defer:

- [ ] 不做完整 plugin marketplace。
- [ ] 不做 full MCP server，除非 API/records 已稳定。
- [ ] 不把 Langfuse/LangSmith/Phoenix 当作 run ledger。

## Phase 7：Physical-AI Modules

目标：在核心审计、工具权限、cowork、research 和 artifact 能力稳定后，接入 physical-AI 相关模块。

Entry check:

- [ ] 高风险 tool policy 已可用。
- [ ] approval/preflight/audit 已可用。
- [ ] artifact store 能处理 logs、configs、metrics、videos 等产物。
- [ ] simulation/training/dataset/evaluation/ROS 的先后关系已有选择。

Build check:

- [ ] simulation module 能记录 scene/config/result artifacts。
- [ ] training module 能记录 job、metrics、checkpoints、budget。
- [ ] dataset module 能记录 hash、lineage、version。
- [ ] evaluation module 能记录 metrics/report。
- [ ] multimodal logging 能登记视频、轨迹、Rerun/rosbag 等 artifacts。
- [ ] ROS module 只作为 adapter 存在。
- [ ] real robot action 需要 allowlist、preflight、approval、strong audit。
- [ ] sim-first 或 dry-run-first 策略明确。

Acceptance check:

- [ ] sim/training/dataset/eval 能作为 Novi modules 被 run 调用。
- [ ] 真实机器人动作不会绕过 policy。
- [ ] ROS 不是 Novi base layer。
- [ ] physical-AI 产物能被 artifact、memory、audit 引用。

Defer:

- [ ] 不做 fleet robotics control。
- [ ] 不做 robot-first runtime。
- [ ] 不做无审批真实机器人执行。
- [ ] 不做完整实验平台替代品。

## 跨阶段开发检查

这些检查不属于单一 phase，但每次扩展都应回看：

- [ ] 新能力是否进入 Novi Tool Runtime 或等价受控边界？
- [ ] 是否记录 actor、time、input、output、policy decision？
- [ ] 是否能 inspect？
- [ ] 是否能 replay 或至少解释？
- [ ] 是否产生 artifact 或 event？
- [ ] 是否可能写 memory？如果是，是否只产生 candidate？
- [ ] 是否引入新的 permission？
- [ ] 是否引入外部 source of truth？如果是，是否明确降级为 adapter？
- [ ] 是否破坏 local-first？
- [ ] 是否把某个 provider/framework 变成不可替换？

## 当前待定

Open:

1. 多人类 project participants 应在 research/deep-research 前还是后实现？
2. Memory review 应与 cowork 并行讨论，还是等 research run 稳定？
3. Browser automation 是否进入 Phase 2，还是 Phase 5 后？
4. Coding worker 是否作为 cowork 的第一个真实 worker adapter，还是应先做 human review/approval？
5. Physical-AI 中 simulation、training、dataset、evaluation、ROS 的先后关系如何定？
6. Phase 1.5 多宽才仍是 integrated exploration，而不是 overdesign？
7. `exploration.md` 中哪些新 records 应先进入 durable data model：`AgentProfile`、`WorkflowSpec`、`Contribution`、`KnowledgeImport`、`ClaimCandidate`、`MemoryRecord`？
8. 最小 demo 是什么，能证明 Novi 支持 scientific self-iteration，而不是只整理 agent transcripts？
