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

## Phase 0：规格收敛

目标：让产品边界、feature 面和技术候选足够清楚，可以开始做最小核心。

Entry check:

- [ ] 已读启动说明和 technical tooling 背景文档。
- [ ] 已确认 Novi 不是 robot-first、不是 multi-agent-first、不是 Codex replacement。
- [ ] 已确认 Novi core 拥有 sessions、runs、tools、artifacts、memory flow、policy 和 audit。

Build check:

- [ ] `architecture.md` 描述核心概念和边界。
- [ ] `tooling-and-modules.md` 描述候选模块、外部项目和接入边界。
- [ ] `features.md` 列出 core/early/next/later features。
- [ ] `roadmap.md` 可作为开发检查清单。
- [ ] `open-questions.md` 收集仍需确认的问题。
- [ ] 中英文 spec 保持结构大体同步。

Acceptance check:

- [ ] 能解释 Novi 的一句话定位。
- [ ] 能解释 v0 为什么不依赖 ROS/MCP/Web dashboard/复杂 multi-agent graph。
- [ ] 能解释 Codex/Claude/OpenHands 为什么是 worker，而不是 Novi source of truth。
- [ ] 能解释多个人类 project participants 和 agent participants 的区别。

Defer:

- [ ] 不定具体文件结构。
- [ ] 不定详细数据模型。
- [ ] 不定 memory 内部机制。
- [ ] 不定完整 CLI 命令。
- [ ] 不定具体交付日期。

## Phase 1：本地核心闭环

目标：在不依赖复杂外部 agent 框架的情况下，让 Novi 可以创建、执行、记录、检查一个本地 run。

Entry check:

- [ ] Phase 0 的核心边界已经可接受。
- [ ] 已决定先做 local-first。
- [ ] 已决定第一控制面是 CLI。
- [ ] 已决定 Simple Kernel 或等价 fallback 存在。

Build check:

- [ ] project init 能创建本地 Novi workspace。
- [ ] skill registry 能发现和列出 `SKILL.md`。
- [ ] session 能创建、打开、列出、保存 summary。
- [ ] run 能创建、更新状态、完成、失败。
- [ ] run ledger 能记录 append-only events。
- [ ] tool call log 与普通 event 分开。
- [ ] artifact store 能登记本地产物。
- [ ] tool registry 能列出本地 tools。
- [ ] policy/approval 至少能表达 require approval / blocked。
- [ ] context pack 能被生成并保存。
- [ ] CLI 能 inspect project/session/run/tool/artifact。
- [ ] Simple Kernel 能产生 deterministic run events。

Acceptance check:

- [ ] 用户能运行最小链路：init、skill list、session create、run start、run inspect。
- [ ] 一个 run 的 objective、status、events、tool calls、artifacts 都能被查看。
- [ ] 用户能回答“发生了什么、为什么、产物在哪里”。
- [ ] 高风险或未授权工具不会绕过 policy 直接执行。
- [ ] 即使没有真实 LLM，也能验证 core records。

Defer:

- [ ] 不接真实机器人。
- [ ] 不做完整 memory 系统。
- [ ] 不做 TUI/Web。
- [ ] 不要求 DeepAgents/LangGraph 已接入。
- [ ] 不做复杂 permission matrix。

## Phase 2：Research 与 Deep Research

目标：让 Novi 能处理真实研究任务，产生可追溯 sources、evidence table、report 和 artifacts。

Entry check:

- [ ] Phase 1 的 run ledger、artifact store、tool runtime 可用。
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
- [ ] DeepAgents/LangGraph kernel adapter 可以作为 serious kernel 候选接入。
- [ ] DeepAgents tools 通过 Novi Tool Runtime 包装。
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
