# 工具选择与模块设定规格

状态：Draft

本规格只讨论候选工具和模块边界。它不是实现计划、文件结构、数据模型或 milestone 安排。

## 目的

Proposal:

Novi 应被构建为一个 platform core，外接可替换的 execution kernels 和可选 modules。

Platform core 应拥有：

- skills；
- sessions；
- runs；
- context；
- tool registry 和 policy；
- artifacts；
- memory flow；
- approvals；
- audit state。

外部工具和框架可以提供执行能力或集成能力，但不应成为 Novi 状态的 source of truth。

## 选择原则

Proposal:

优先选择符合以下条件的工具：

- 适合 local-first 的研究、编码、训练、仿真和 physical-AI workflows；
- 能被 Novi-owned interfaces 包装；
- 支持 inspection、approval、audit 和 replay；
- 不把 Novi 绑定到单一 vendor、model、framework 或 runtime；
- 可以简单起步，并在之后替换。

避免引入那些要求 Novi 放弃 sessions、runs、memory、artifacts、permissions 或 policy 所有权的工具。

## 核心语言方向

Proposal:

Python 应作为第一版 core runtime，因为预期领域包括研究、ML、机器人、仿真、训练、scientific Python、ROS 和本地自动化。

TypeScript 后续仍可能有价值，尤其是：

- web control plane；
- browser-heavy modules；
- Pi 或其他 TypeScript-native agent kernels；
- frontend tooling。

这是 runtime preference，不是永久产品约束。

## Agent Kernel 候选

Proposal:

Novi 应定义 agent kernel adapter boundary。Kernel 可以执行 run、stream events、请求 tools、等待 approval、恢复执行。但 kernel 不应拥有 Novi records。

### DeepAgents + LangGraph

建议作为第一个 serious research/experiment kernel 候选。

适合：

- 复杂多步任务；
- planning 和 task decomposition；
- 通过 working files 管理上下文；
- 用 subagents 做 context isolation；
- human-in-the-loop approval flows；
- 通过 LangGraph durable execution 和 resume；
- model-provider flexibility。

边界：

- DeepAgents subagents 是 execution-level helpers，不自动等于 Novi platform agents。
- DeepAgents tools 应包装 Novi Tool Runtime。
- DeepAgents memory 或 filesystem state 不应绕过 Novi review/registration，直接成为 Novi long-term memory 或 artifacts。

### Simple Kernel

建议作为最小 fallback 和 test kernel。

适合：

- 不依赖外部 agent framework 跑通 core loop；
- deterministic tests；
- 验证 sessions、runs、tool policy、artifacts 和 inspection；
- 避免过早 lock-in。

### Pi Agent Core

可作为后续 spike，用于 interactive local coding-agent-like workflows。

适合：

- local interactive agent experience；
- embedded coding-style sessions；
- TypeScript-side experiments。

边界：

- Pi session state 是 execution state，不是 Novi source of truth；
- tool calls 仍应通过 Novi Tool Runtime；
- 在它证明稳定适配 Novi 需求前，不作为默认基础。

### Codex、Claude Code、OpenHands

应视为 external coding workers，而不是 Novi core runtime。

适合：

- implementation tasks；
- refactors；
- code review；
- tests 和 patch generation。

边界：

- Novi 创建并审计 coding run；
- worker 产出 diffs、logs 和 artifacts；
- Novi 记录结果、policy decisions 和 memory candidates。

## 工具与模块组

Proposal:

Modules 应暴露 tools、resources、observations、artifacts 和 policies。第一阶段讨论应关注模块边界，而不是具体实现。

### 本地项目模块

候选模块：

- filesystem；
- git；
- shell sandbox；
- python execution；
- notebook execution。

这些模块支撑 local-first 工作和编码/研究 workflows，也有真实风险，因此需要 policy gate。

### 研究模块

候选模块：

- search；
- web fetch；
- browser automation；
- PDF/document parsing；
- citation and source extraction。

Hosted search 早期有用，但应保持未来替换为 self-hosted 或其他 adapter 的可能。

### MCP 模块

MCP 应被视为外部 tool/resource adapter，而不是 Novi 的基础。

早期方向：

- core tool runtime 稳定后再加入 MCP client；
- MCP tools 必须经过 Novi policy、approval 和 audit；
- 只有当 Novi records 和 APIs 稳定后，再考虑 MCP server。

### Coding Worker 模块

候选 workers：

- Codex；
- Claude Code；
- OpenHands。

它们应作为 Novi run 内部的 external workers，而不是替代 Novi control-plane state。

### Physical-AI 模块

候选模块：

- ROS；
- simulation；
- training；
- dataset；
- evaluation；
- Rerun 或 multimodal logging。

这些模块应保持模块化。Novi 不应变成 robot-first，也不应让 ROS 成为 base layer。

## 暂缓区域

Deferred:

- 详细文件结构；
- 具体数据模型；
- milestone plan；
- memory system design；
- TUI design；
- chat channel integration；
- plugin marketplace；
- full MCP server；
- robotics execution policy。

这些都是真实需求，但应分别单独制定规格。

## 待确认问题

Open:

1. 是否以 Simple Kernel 先验证 core，再把 DeepAgents + LangGraph 作为第一个真实 kernel？
2. 第一个有用 demo 前，哪些 local project modules 是必需的？
3. 早期 research runs 是否接受 hosted search，还是 search 先从 stub/local adapter 开始？
4. Codex/Claude/OpenHands workers 应表示为 module、tool、kernel，还是单独的 worker category？
5. Physical-AI 模块应先讨论哪一类：simulation、training、dataset、ROS，还是 evaluation？
