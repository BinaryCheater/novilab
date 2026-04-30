# 核心概念

## Novi 的定位

Novi 是本地优先的研究控制平面。它不把某个 LLM agent 框架当成项目真相来源，而是把项目状态保存为可检查的本地记录。

外部系统的角色：

- Codex、Claude Code、DeepAgents 等是 worker 或 kernel。
- 模型 provider 是可替换的执行后端。
- 工具、搜索、PDF、浏览器、仿真器等应通过 Novi Tool Runtime 和 policy 接入。

Novi 自己负责：

- session 和 task 的长期上下文；
- run 的执行记录；
- workflow step 的推进；
- tool/model 调用日志；
- artifact 归档；
- contribution 和 review gate；
- accepted knowledge 进入后续 context 的边界。

## 主要对象

### Workspace

`novi init` 会在当前项目创建 `.novi/`。这是 Novi 的本地 source of truth。

### Session

Session 表示长期工作上下文。`novi ask` 和 `novi task` 都会把消息和 run 关联到 session。

### Task

Task 表示一个可持续推进的目标，例如“整理接触先验并形成下一步实验计划”。Task 保存 `workflow_state`，可以通过 `novi task continue` 恢复。

### Workflow

Workflow 定义推进方式。它可以包含 system 步骤、agent 步骤、human review gate 和 decision 步骤。

### Run

Run 是一次执行和审计单位。每个 run 都有 objective、participants、context pack、prompt archive、model calls、tool calls、artifacts 和 summary。

### Artifact

Artifact 是可追溯产物，例如模型回复、研究笔记、导入文档、analysis note、DeepAgents working file。

### Contribution

Contribution 是待审变更，例如 document patch。Agent 产生的 contribution 通常需要 source refs；人类来源可以更宽松，但仍应保留 attribution。

## 设计原则

- 先可检查，再自动化。
- Agent 可以提出修改，但不应静默修改 accepted state。
- Domain 知识，例如“物理先验”，属于 skill 和文档库内容，不应变成 Novi 内置对象。
- 用户日常关注任务和内容，审计记录用于解释发生了什么。

