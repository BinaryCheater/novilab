# 探索规格

状态：Exploration

本文记录设计探索，不是已经接受的实现范围。这里探索的对象是未来功能集合本身：可配置 multi-agent 工作、workflow 构建与迭代、多用户协作与内容合并、直接 agent 指导，以及科学记忆。本文也保留 EvoScientist/DeepAgents 对比，作为后续实现选择的参考材料。

核心设计命题是：

```text
Novi 如何同时构建可配置 multi-agent execution、自迭代 workflow、
多用户协作和可靠科学记忆，同时不失去 scope、state 和 audit 的控制？
```

目的不是把 Phase 1 立即扩大成完整平台，而是在 Phase 1 仍保持 local-first 和 inspectable 的前提下，把更大的产品命题放在眼前。

## 探索范围

Open:

本文不只是讨论“如何一次实现几个功能”。它首先讨论这些功能在 Novi 里究竟应该是什么意思。

当前探索的功能区包括：

1. 可配置 multi-agent 工作：agent profiles、prompts、tool sets、permissions、model profiles、output schemas、interfaces、kernel bindings，以及 per-run participant snapshots。
2. Workflow 构建与迭代：生成计划、workflow records、success signals、executable steps、reflection、workflow patches 和 accepted revisions。
3. 多用户协作与内容合并：project participants、imported knowledge、comments、review、contribution records、merge decisions 和 attribution。
4. 直接 agent 工作与用户指导：允许用户直接在 DeepAgents-like session 中工作，同时把有价值输出重新带回 Novi artifacts、contributions、memory candidates 或 workflow patches。
5. 可靠科学记忆：通过 claims、procedures、hypotheses、evidence、negative results、contradictions、confidence、review 和 supersession，让长期知识真的支持科学发现。

实现问题在这个探索之后：

```text
哪些对象和流程是真正的 Novi concepts？
哪些可以继续留在 adapter、kernel-local state、artifacts 或临时实现脚手架里？
```

## 背景

Novi 当前已经接受的方向是 skill-first、session-aware control plane。Novi 拥有 sessions、runs、tools、artifacts、memory candidates、policies、context packs 和 audit records。DeepAgents、LangGraph、MCP、Codex、Claude Code、browser tools、search providers、training systems 和 ROS 等外部系统是 adapters 或 modules。

现在的问题是：Novi 应该只是围绕外部 agent framework 的薄 local run ledger，还是应该成为一个更宽的 research operating layer，让 agents、humans、workflows、imported knowledge、memory 和 scientific evidence 共同演化？

用户意图更接近后者：

- 可配置 multi-agent 工作：prompts、tool sets、permissions、model profiles、interfaces 和 scopes 应该容易定义和修订；
- 自动 workflow 构建与迭代：agents 应该生成、执行、评估、修补 workflows，而不是只回答一次；
- 多用户协作与内容合并：用户应该能导入知识、指导 agents、review outputs、直接使用 DeepAgents-like surfaces，并把结果 merge 回共享 project state；
- 可靠自迭代科学记忆：长期 memory 应支持科学发现，而不只是 personalization 或 chat continuity。

澄清：

Novi 不应把“物理先验”这类领域研究概念编码成 core framework object。
领域概念应属于 project skills 和 Markdown 文档库。Novi 的职责是保留
provenance，用受限 agent 或 worker 运行相关 skill，记录 artifacts 和
proposed changes，在共享状态变化前要求 review，并让 accepted records 能被
后续 run 使用。

## 功能探索

### 可配置 Multi-Agent 工作

Open:

目标不是“多个 agents 能聊天”。Novi 需要一个配置和执行模型，让 agents 因为清晰边界而有用：

- responsibility：planner、researcher、coder、auditor、reviewer、operator、simulator、trainer 或 domain specialist；
- prompt and instruction set：稳定 system prompt、active skills、task protocol、output constraints 和 review criteria；
- tool set：visible tools、callable tools、executable tools，以及需要 approval 的 tools；
- permission scope：read、write、shell、network、external side effect、physical world、memory proposal、memory acceptance、workflow patch 或 review；
- context scope：project spec、session summary、imported knowledge、artifacts、accepted memory、recent messages、current workflow 或 selected run records；
- model profile：不同 providers、models、reasoning effort、cost limits 或 latency preferences；
- interface：CLI、TUI、web、channel、direct DeepAgents session、worker adapter 或 headless run；
- output contract：report、evidence table、patch、review decision、memory candidate、workflow patch、code diff、metrics 或 audit note。

设计张力：

如果 agent profiles 太弱，用户会绕过 Novi 去编辑 DeepAgents YAML、prompts 或 raw tool lists。如果它们太早变得太强，Novi 会在 run ledger、memory 和 workflow layer 被证明之前，提前变成完整 multi-agent framework。

当前工作方向：

Novi 应定义 project-local agent profiles 作为 platform records，然后编译到选定 execution kernel。DeepAgents subagent 是一种 compiled form，不是源记录。

### Workflow 构建与迭代

Open:

目标是 agent-assisted workflow loop，而不是静态 checklist。Novi 应帮助用户从 objective 到 workflow，从 workflow 到 execution，从 execution 到 evidence，再从 evidence 到可 review 的 workflow update。

Workflow 可能需要：

- objective 和 scope；
- assumptions 和 open questions；
- stages 或 steps；
- 每个 step 的 agent assignment；
- required tools 和 permissions；
- expected artifacts；
- success signals 和 stop criteria；
- iteration triggers；
- resource estimates 和 preflight checks；
- reflection outputs；
- workflow patches 和 accepted revisions。

设计张力：

EvoScientist 显示 prompt-driven workflows 可以非常有效且灵活。但当 workflow evolution 需要 review、replay、compare 或作为 future context 时，Novi 仍需要 record-shaped workflow state。

当前工作方向：

Workflow 应先从轻量 records 或 artifacts 开始，再通过 review promotion 进入更持久的状态。不要先建重型 workflow engine。第一要求是 workflow creation、execution、reflection 和 patching 可检查。

### Skill 驱动的文档处理与 Patch 合并

Open:

一个核心用户流程是：人类协作者导入 document、note、log 或 direct
agent-session export，其中内容可能清晰，也可能只是模糊观点或片段。用户不应
被要求手写 patch。Novi 应先把导入记录为 raw material，然后允许 scoped agent
基于 selected skills 处理它，并产出可 review 的结果。

第一版有用处理循环是：

```text
import document
-> preserve raw artifact and import contribution
-> process with a selected skill/workflow and scoped agent
-> write an analysis note artifact
-> optionally produce one or more document patch contributions
-> review/check the patch
-> accept applies the patch, reject preserves history, conflict blocks merge
-> later runs consume accepted document state and trace its provenance
```

Patch 是 agent 或 worker 的输出格式，不是主要的人类输入格式。人类可以提供
guidance 并选择 target document；提供 target 时它是 hard constraint。常规路线应是 agent 基于 import、用户 hint 和提供的 library context，生成 analysis note 和零个、一个或多个 patch candidates 供 review。

当前工作方向：

- 如果提供 target document，processing run 可以针对该 target 创建 patch
  contribution。
- 如果没有提供 target document，processing run 可以基于提供的 library context
  提出现有文档合并、新文档或需要 human 回答的问题。
- Patch target 第一版限制在 Markdown knowledge/document library、workflow
  records 和 project-local skills。
- Accepted specs、source code、tests 和 project configuration 不走这条 patch
  path。
- Agent-generated patches 必须携带来自 import、run、analysis artifact、
  accepted knowledge 或 worker bundle 的 source refs。Human-authored changes
  可以更宽松，但仍必须能 attribution。
- Accept patch 前先做 dry-run/check，只有 target scope 和 patch 有效时才
  apply，并记录 changed files 和 merge metadata。
- 如果 patch apply 失败，Novi 不修改 target files；它把 contribution 标记为
  conflict，并可 assign 给 merge/review agent，让其提出 revised patch 或
  review recommendation。

这样可以把领域研究内容留在 skills 和 documents 中，同时让 merge path 可审计。

### 多用户协作与内容合并

Open:

目标不只是 channels 或 chat access。Novi 需要让多个人类和 agents 能贡献共享 project state，同时不会静默覆盖 accepted knowledge、workflows、summaries 或 memory。

协作可能包括：

- 导入 papers、notes、datasets、logs、code、experiment results 或 direct agent-session exports；
- 把 review 或 analysis 分配给 humans、agents 或 external workers；
- 对 runs、artifacts、tool calls、memory candidates 和 workflow patches 评论；
- accept、reject 或 request changes；
- 把 selected contributions merge 到 project state；
- 把 rejected contributions 保留为 audit history；
- 将动作归因到 human、agent、worker 或 system process。

设计张力：

过早构建 realtime collaborative editing、完整 team admin、notifications 和细粒度权限，会冲垮 local-first core。但如果没有 contribution 和 merge model，多用户工作会退化成非结构化 chat transcript。

当前工作方向：

先做 contribution records 和 review decisions，而不是实时协同编辑。第一版 merge unit 可以较粗：imported artifact、extracted claim、memory candidate、workflow patch、skill patch 或 run summary patch。

对于文档库和 skill 的迭代，首选 merge unit 是 patch contribution。Agents
可以提出对 documents、workflows 或 project-local skills 的 patches，
但 accepted files 只有在 review 和 patch check 成功后才会被更新。

### 直接 Agent 工作与用户指导

Open:

目标包括用户直接在 DeepAgents-like agent surface 中工作，并给它指导让它迭代。Novi 不应阻止直接 agent 使用，但必须定义直接工作如何影响共享 project state。

重要场景：

- 用户启动 direct agent session 做探索性思考；
- 用户给出 high-level guidance，让 agent 自行迭代；
- agent 请求用户澄清或 checkpoint decision；
- direct session 生成 files、notes、reports、plans 或 code；
- 用户希望把部分输出导入 Novi；
- 用户希望丢弃或归档其余部分。

设计张力：

如果 Novi 强迫所有交互都通过 rigid run commands，会失去 DeepAgents 的流动性。如果 Novi 让 direct agent state 自动变成 project state，audit 和 merge boundaries 会消失。

当前工作方向：

把 direct agent sessions 视为 execution workspaces。它们的输出进入 Novi 时应成为 artifacts 和 contributions，再由 review/merge 决定哪些部分影响 accepted project state。

### 可靠科学记忆

Open:

目标不是 persistent chat memory。科学记忆必须帮助未来 runs 做出更好的研究决策，同时保持 evidence-based、reviewable 和 correctable。

Memory 可能需要表达：

- preferences 和 constraints；
- procedural lessons；
- known promising directions；
- known failed directions；
- hypotheses；
- claims；
- experimental setup；
- result summaries；
- negative results；
- contradictions；
- replications 或 failed replications；
- artifact links；
- confidence 和 scope；
- supersession history。

设计张力：

Markdown memory 易检查、易编辑，但对 contradiction、supersession、retrieval 和 evidence tracking 很弱。完整 knowledge graph 很强，但在 basic review loop 被证明之前太重。

当前工作方向：

从 evidence-backed memory candidates 和 accepted memory records 开始。最小持久单元应是带 type、scope、evidence refs、confidence、review decision 和 supersession state 的 claim 或 procedure。Markdown 可以继续作为可读表面，但底层 record 必须保留 provenance。

领域特定的科学构造不应全部成为 Novi object types。如果项目想维护“物理先验”
这样的主题，可以通过 skill-defined methods 和 Markdown documents 来汇总、
链接、修订相关知识。Novi 应追踪围绕这些工作的 documents、patches、
artifacts、review decisions、memory candidates 和 lineage。

## EvoScientist 在 DeepAgents 上实际构建了什么

Observation:

EvoScientist 不只是 DeepAgents 外面的一层 prompt。其公开代码显示，它围绕 `deepagents.create_deep_agent` 构建了一套 application stack：

- `subagent.yaml` 定义 planner、researcher、code、debug、data-analysis、writing 等角色化 subagents。
- 主 agent factory 组装 model configuration、DeepAgents backends、middleware、MCP tools、subagents、skills 和 system prompt。
- `CompositeBackend` 把 workspace files、skills 和 memories 路由到不同 virtual paths。
- Custom sandbox backends 做 path validation、command validation 和更安全的 shell behavior。
- Middleware 处理 memory injection/extraction、context editing、tool selection、tool errors，以及 agent-initiated user questions。
- MCP integration 支持 tool allowlists 和 `expose_to` routing，可把一个 server 的 tools 暴露给 main agent 或特定 subagents。
- Sessions 使用 LangGraph SQLite checkpoints，并做 pruning。
- Channel adapters 通过 shared message bus 接入多个聊天平台，带 allowlists、deduplication、mention gating、per-chat locks 和 outbound formatting。

解释：

EvoScientist 是一个 DeepAgents-native scientific assistant product。DeepAgents 和 LangGraph 是执行与 checkpointing substrate；EvoScientist 增加了有主张的科学角色、workflow prompts、middleware、memory files、channels 和 skill management。

## 参考对比

Observation:

下面的对比是 Novi 设计参考，不代表 Novi 必须实现 EvoScientist 的全部内容，也不代表 EvoScientist 是目标架构。

| 领域 | DeepAgents | EvoScientist | Novi 含义 |
|---|---|---|---|
| Execution loop | 提供 model/tool loop、planning、filesystem working memory、subagents、interrupts 和 LangGraph-based state | 以 `create_deep_agent` 为中心装配 agent | 可作为 kernel 复用；除非 Novi 需要 DeepAgents 暴露不了的边界，否则不重复造执行 loop |
| Agent configuration | 支持带 prompts、tools、models、permissions、middleware 的 subagent definitions | 用 `subagent.yaml` 外置固定科学角色 | 先定义 Novi `AgentProfile`，再编译成 DeepAgents subagents 或其他 worker bindings |
| Tool exposure | Tools 传入 agent，并可做 permission gating | 增加 MCP allowlists 和按目标 agent 的 `expose_to` routing | 借鉴 allowlist/routing，但外部 tool 应成为或包装成带 risk/policy 的 Novi ToolSpec |
| Filesystem | DeepAgents filesystem 是自然 working memory | 用 `CompositeBackend` 路由 workspace、skills、memories；custom sandbox 保护 paths/commands | Kernel files 是 working state；只有 review 后导出的内容成为 Novi artifacts 或 accepted project state |
| Workflow | 支持 todo/planning patterns 和 subagent task delegation | 用 prompts、skills、planner reflection、report templates 编码 scientific lifecycle | 保留 prompt 灵活性；当 workflow 影响 future work 时，提升为可检查 records 和 patches |
| Context management | 提供 summarization/context editing middleware | 增加面向科学会话的 context editing 和 tool selection middleware | Middleware 可留在 kernel adapter；Novi `ContextPack` 是可检查 context 边界 |
| Memory | 支持 persistent memory patterns 和 backend storage | 注入/抽取 Markdown memory，包括 user profile、preferences、experiment conclusions | 模式有价值，但 Novi memory 必须 reviewable、evidence-backed、能处理 contradiction |
| Human input | 支持 human-in-the-loop interrupts | 增加 `ask_user` 用于研究澄清和恢复决策 | 是好的 adapter pattern；Novi 应记录 question、answer、approval 和 resulting state changes |
| Channels | 本身不是 collaboration system | 提供多 channel adapters、allowlists、group context、message bus 和 per-chat locks | Channels 是 surface，不是 project participants、contributions 和 merge decisions 的替代品 |
| Sessions | 使用 LangGraph threads/checkpoints | SQLite checkpoints 保存 sessions，并 pruning old snapshots | Checkpoints 可链接到 runs 用于 execution recovery；Novi run ledger 仍是 source of truth |
| Scientific reliability | 提供机制，不提供科学认识论 | 增加 scientific prompts、skills、rigor checklists 和 memory evolution triggers | Novi 需要显式 evidence、claims、negative results、review 和 supersession records |

## 目标功能覆盖情况

Observation:

用户想要的能力在现有系统中的覆盖并不均匀：

| 目标能力 | DeepAgents 支持 | EvoScientist 支持 | Novi 缺口 |
|---|---|---|---|
| 可配置 multi-agent prompts/tools/permissions/interfaces | 强 execution primitives | 实用的 YAML subagents 和 MCP tool routing | Platform-owned agent profiles、versioning、audit、compile targets |
| 自动 workflow 构建与迭代 | Todos、planning、subagents、interrupts | Scientific lifecycle prompts、planner reflection JSON、skills | Workflow records、workflow patches、review/merge、next-run context inclusion |
| 多用户协作与内容合并 | 不是核心能力 | Multi-channel access、allowlists、group context | Participants、contributions、comments、review、merge decisions、conflict history |
| 用户导入知识由 agent 处理 | 可通过 files/tools 实现 | 可通过 workspace 和 skills 实现 | Formal import artifacts、extraction state、candidate generation、review |
| 用户直接在 DeepAgents-like surface 工作 | 原生支持 | CLI/TUI/script/channel 使用 | 导入 direct session outputs，同时不绕过 Novi review |
| 用户指导 autonomous iteration | Interrupts 和 long-running state | `ask_user`、human-on-the-loop posture、workflow reflection | Recorded guidance、decisions、workflow patches、accepted/rejected state changes |
| 可靠自迭代科学记忆 | Memory primitives | Markdown EvoMemory 和 memory-evolution skills | Evidence-backed claim/procedure records、contradictions、negative results、supersession |

## DeepAgents 与 EvoScientist 的覆盖

### 可配置 Multi-Agent

Decision candidate:

DeepAgents 提供 subagents、tools、model selection、permissions 和 human-in-the-loop interrupts 等有用 primitives。EvoScientist 证明了一个实用科学 agent 可以把 subagent definitions 外置到 YAML，并按 agent 注入 MCP tools。

Novi 缺口：

EvoScientist 的 subagents 是 execution helpers。Novi 需要 platform agent profiles，可 audit、version、scope、review，并可编译到 DeepAgents subagents 或其他 kernels。一个 Novi agent 只有在代表不同 responsibility、permission boundary、tool set、context scope、execution environment、output schema 或 audit identity 时，才应该成为 run participant。

### Workflow 构建与迭代

Decision candidate:

EvoScientist 主要通过 system prompts、skills、todos、planner-agent reflection 和 report templates 实现 workflow。这对科学 assistant 很有效，因为模型可以灵活适应。

Novi 缺口：

Novi 需要 workflows 作为 records，而不只是 prompt text 或 `/todos.md`。Workflow 应通过显式对象被生成、执行、评估和修订：

```text
WorkflowSpec
  -> WorkflowRun
  -> StepRun
  -> Reflection
  -> WorkflowPatch
  -> ReviewDecision
```

Agents 可以提出 workflow patches，但 Novi 应记录改了什么、为什么、什么 evidence 触发了改变，以及谁接受了它。

### 多用户协作与内容合并

Observation:

DeepAgents 本身不是 multi-user collaboration system。EvoScientist 有 multi-channel messaging、allowlists、group context 和 per-chat locks。这对访问和沟通有用，但不等于 project-level identity、ownership、review、merge、conflict handling 和 audit attribution。

Novi 缺口：

Novi 应把用户导入的知识、agent 输出、worker 输出、review comments 和 merge decisions 视为对 project state 的 contributions。第一层协作不应是实时协同编辑，而应是可 merge 的 contribution ledger：

```text
Contribution
  = actor
  + source
  + target object
  + proposed change
  + evidence refs
  + review state
  + merge decision
```

这可以同时支持多个人类、导入文档、direct DeepAgents sessions、Codex/Claude/OpenHands worker outputs 和 agent-generated revisions，而不让任何外部 channel 或 worker 成为 source of truth。

### 用户指导与直接 Agent 工作

Observation:

DeepAgents 支持 long-running sessions、interrupts 和 direct agent interaction。EvoScientist 暴露 direct CLI/TUI use、single-shot mode、scripts、channels、`ask_user` 和 session resume。

Novi 缺口：

Novi 应允许 direct DeepAgents-like work，但当 direct work 要影响 project state 时，它仍必须回到 Novi 边界。一个有用拆分是：

- interactive execution state 属于 kernel；
- accepted project state 属于 Novi；
- 从 direct agent session 导入的任何东西，都成为 artifacts、contributions、memory candidates、workflow patches 或 skill patches。

### 科学记忆

Observation:

DeepAgents 有 memory primitives 和 backend storage。EvoScientist 增加 memory middleware，把 user profile、preferences、learned preferences 和 experiment conclusions 注入 prompt 并抽取到 Markdown。

Novi 缺口：

这不足以支撑可靠科学发现记忆。Novi 的 memory 需要区分：

- user/project preferences；
- procedural know-how；
- research claims；
- hypotheses；
- experimental results；
- negative results；
- contradictions；
- superseded findings；
- reusable workflows；
- evidence artifacts。

持久单元不应只是“remembered text”。它应该是带 evidence、provenance、confidence、scope、status 和 supersession history 的可 review claim 或 procedure。

## Novi 的不同押注

Proposal:

Novi 不应与 DeepAgents 竞争 execution harness。它应在有用时把 Novi-owned state 编译到 DeepAgents-compatible execution，再把输出带回 Novi-owned records。

边界应是：

```text
Novi Core
  owns AgentProfile, WorkflowSpec, RunLedger, ToolRuntime, ArtifactStore,
  ContributionLedger, MemoryReview, Policy, ContextPack

DeepAgents/LangGraph
  executes model/tool loops, subagent tasks, filesystem working memory,
  interrupts, streaming, checkpoints, and summarization
```

DeepAgents checkpoints 是 execution recovery state，不是 Novi 的 run ledger。DeepAgents filesystem 是 working memory，不是 Novi 的 artifact store。DeepAgents memory 可以帮助执行，但不能直接提交 Novi long-term memory。

## Integrated Exploration 命题

Open:

早先较窄的验证切片是：

```text
import knowledge
-> run agent
-> produce evidence-backed memory candidates and workflow patch
-> user review/merge
-> next run consumes accepted records
```

用户认为这太窄，因为这些基础功能互相依赖。Multi-agent configuration、workflow iteration、collaboration 和 scientific memory 不是彼此独立的后置层；它们互相塑形。

重新表述的命题：

Novi 应一起验证这四个基础，但每个基础只跨一个薄而可检查的边界：

1. Agent profiles：一个可配置 primary agent，加一个 reviewer/auditor 或 specialist，记录 prompts、tools、permissions、model profile 和 output schema。
2. Workflow records：一个带 steps、success signals、iteration triggers 和 patch mechanism 的 generated workflow。
3. Contribution ledger：一个 imported knowledge contribution，以及一个 user/reviewer decision，可以 merge 或 reject agent-produced changes。
4. Scientific memory：一个从 run 生成、可接受或拒绝的 evidence-backed claim/procedure。

范围比单个 import-memory loop 更宽，但仍受控，因为每部分都浅、可记录、可检查。

## 避免 Scope Collapse 的控制规则

Decision candidate:

Integrated exploration 只有在这些 invariants 成立时才应推进：

- 每个 autonomous action 属于一个 run 或 assignment。
- 每个有意义输出成为 artifact、contribution、workflow patch、memory candidate、tool call、model call 或 event。
- Agents 不能直接修改 accepted project memory、accepted workflow versions 或 shared knowledge stores。
- Agent-generated workflow changes 是 patches，不是 silent edits。
- User imports 成为 artifacts 加 extracted candidates，而不是直接 memory。
- Direct DeepAgents sessions 可以产生 contributions，但未经 review 不成为 Novi source of truth。
- Multi-user collaboration 从 identity、comments、review 和 merge decisions 开始，不从 realtime editing 开始。
- 来自 DeepAgents、MCP、browser、shell、workers 或 channels 的 tool calls 必须通过 Novi ToolRuntime，或一个显式等价的 policy/audit boundary。
- Scientific memory 引用 evidence artifacts，并记录 confidence、scope、review status 和 supersession。
- LangGraph checkpoints 可以从 runs 链接，但不能替代 run records。

## 建议探索闭环

Proposal:

一个 integrated exploration run 未来应大致如下：

```text
1. User imports knowledge, notes, paper snippets, prior experiment logs, or
   direct guidance.
2. Novi records the import as an artifact and contribution.
3. Novi selects or compiles agent profiles into the execution kernel.
4. Agent creates or updates a WorkflowSpec.
5. Agent executes one or more workflow steps through Novi-scoped tools.
6. Agent may ask the user for clarification or propose workflow changes.
7. Agent produces artifacts, claim candidates, memory candidates, and workflow
   patches.
8. Reviewer/user accepts, rejects, or requests changes.
9. Accepted memory and workflow revisions become available to the next run.
10. `novi run inspect` can explain the whole path.
```

这个 loop 保留更大愿景，同时迫使每个 state transition 通过可检查 records。

## 候选新对象

Open:

当前 v0 data model 之外可能需要这些对象：

- `AgentProfile`：project-local agent definition，包含 prompt refs、tool scope、permission scope、model profile、interface mode、output schema 和 policies。
- `KernelAgentBinding`：某个 agent 编译到 DeepAgents、LangGraph、Codex、Claude Code 或其他 kernel/worker 的表示。
- `WorkflowSpec`：versioned workflow，包含 steps、success signals、agent assignments、required artifacts、tool requirements 和 iteration triggers。
- `WorkflowPatch`：对 workflow 的 proposed change，带 reason、evidence refs、proposer 和 review state。
- `Contribution`：针对 project state 的 imported 或 generated change proposal。
- `KnowledgeImport`：用户提供 documents、notes、logs 或 direct agent-session exports 后形成的 source artifact 加 extraction state。
- `ClaimCandidate`：从 evidence 抽取、尚未成为 memory 的 scientific claim。
- `MemoryRecord`：accepted memory，带 type、evidence refs、scope、confidence、review decision 和 supersession history。

这些对象不应一次全部实现。Exploration track 应先测试它们的边界是否真实，以及现有 `RunSpec`、`ArtifactRecord`、`MemoryCandidate` 和 `EventRecord` 是否能吸收其中一部分。

## Roadmap 含义

Proposal:

不要强行维持一个严格串行 roadmap，让 research、collaboration 和 memory 作为互相隔离的 phases 出现。Phase 1 之后应加入 integrated exploration track，用一个受控 loop 同时推进 configurable agents、workflow iteration、contribution review 和 scientific memory。

这不是一次构建完整平台。它意味着每个 phase 都应保留共同闭环：

```text
agent/workflow/collaboration/memory are advanced together,
but each only crosses one small, inspectable boundary at a time.
```

## 待定问题

Open:

1. Autonomous work 的首要用户可见容器应该是什么：session、run、workflow 还是 assignment？
2. Workflow versions 应是 global project objects、session-scoped objects，还是通过 review promoted 的 artifacts？
3. Direct DeepAgents session 应如何导入：完整 transcript、仅 artifacts、generated contribution bundle，还是三者都要？
4. 最小 scientific memory schema 如何表达 negative results 和 contradictions，同时不太早变成完整 knowledge graph？
5. Phase 2 exploration 足够的 merge model 是什么：append-only review decisions、patch files、git-backed diffs，还是 object-level merge records？
6. 当 Novi 可以 audit 它们后，应先启用哪些 DeepAgents built-ins：filesystem write/edit、todo management、subagent `task`、shell execute，还是 memory？
7. 最小 evaluation 是什么，能证明 Novi 支持真实 scientific discovery，而不是只整理 agent transcripts？
