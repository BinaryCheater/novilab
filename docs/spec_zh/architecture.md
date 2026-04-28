# 架构规格

状态：Draft

## 定位

Proposal:

Novi Lab 是一个以技能为优先、感知会话状态的控制平面。它协调研究、编码、实验、仿真、训练、记忆、artifacts、审计和可选的 physical-AI 集成。

Novi 不是主要为了成为：

- multi-agent framework；
- robot runtime；
- ROS wrapper；
- OpenClaw clone；
- Codex 或 Claude Code replacement。

这不意味着 Novi 是 single-agent。Novi 应支持 multi-agent，用于区分不同用途、权限、工具集、上下文范围、执行环境和审计要求。

## 核心系统

Proposal:

```text
Novi Core
  = sessions
  + skills
  + tools
  + runs
  + memory
  + artifacts
  + policies
  + context
```

外部系统是 modules 或 adapters：

```text
ROS
Isaac Sim
LeRobot
Codex
Claude Code
MCP servers
search/browser services
training systems
IM channels
observability tools
```

## 核心职责

Novi Core 负责：

- session state；
- run creation 和 inspection；
- skill loading 和 activation；
- context pack generation；
- tool registry 和 execution lifecycle；
- policy checks 和 approvals；
- event logs 和 run ledgers；
- artifact records；
- memory candidates 和 review state。

Modules 提供：

- tools；
- resources；
- observations；
- artifact types；
- policy contributions；
- optional hooks。

## 主要概念

### Skill

可复用的 workflow package。一个 skill 可以包含 instructions、examples、schemas、references、scripts、assets、policies、evals 和 hooks。

Novi 应保持兼容通用 `SKILL.md` 约定，不应要求每个 skill 都具备 Novi 专属 metadata 才能加载。

### Session

长期存在的工作上下文。Session 不只是 chat history。它包含 active goals、selected skills、summaries、runs、artifacts、memory candidates、approvals 和 channel bindings。

### Run

Session 内的一次可审计执行。Run 是执行、回放、证据和检查的主要单位。

### Tool

由 module 暴露的可调用能力。可见、可调用、可执行、可自动执行、可写 memory 是不同权限层级。

### Memory

由证据支撑、可审阅的知识。长期 memory 应由 agent 提出、经过检查并被接受，而不是由主 agent 直接写入。

### Artifact

Run 产生或引用的持久输出或证据项。Memory 应指向 artifacts，而不是嵌入大量内容。

## Multi-Agent Support

Proposal:

Novi 应支持多个 agents 作为 session 或 run 中的 participants，但不把 multi-agent orchestration 作为产品中心。

当以下边界需要分离时，agent 边界是合理的：

- purpose 或 responsibility；
- model profile；
- context scope；
- tool scope；
- permission scope；
- execution environment；
- output schema；
- safety 或 audit requirements。

Agent 是执行参与者，不是最高层工作单位。最高层工作单位仍然是 sessions 和 runs。

每个 run 应能记录：

- 哪些 agents 参与；
- 每个 agent 的 role；
- 每个 agent 可见或可调用的 tools；
- 每个 agent 收到的 context；
- 每个 agent 适用的 policy 和 approval constraints；
- 每个 agent 产生的 events、tool calls、artifacts 和 memory candidates。

V0 不需要复杂 agent graph 或自由形式的 agent-to-agent chat。但 data model 应兼容多个 agents。

## V0 Agents

Proposal:

V0 在概念上先假设两个 agent role：

- Orchestrator：处理对话、skill 选择、run planning、tool calls、summaries 和 memory candidate proposals。
- Auditor：检查 tool calls、memory candidates、run completeness、evidence 和 spec drift。

第一版实现可以 stub 或简化 auditor，但 data model 应为 agent participants 和 audit records 留空间。

## Context Model

Proposal:

Context 应显式编译。模型调用应接收 `ContextPack`，而不是盲目追加所有历史消息。

建议的 context layers：

- global rules；
- project spec；
- session summary；
- current run state；
- active skill instructions；
- relevant memory；
- selected artifacts；
- available tools。

默认应排除 raw old messages、large logs 和 unverified memory。

## Storage Direction

Proposal:

V0 应本地优先：

- filesystem 存 sessions、runs、skills、artifacts 和 summaries；
- JSONL 存 append-only events 和 tool calls；
- Markdown 存 editable summaries 和 project memory；
- SQLite 可选，用于 indexes 和 queryable metadata。

SQLite 有价值，但即使没有数据库，filesystem records 也应能被人直接理解。
