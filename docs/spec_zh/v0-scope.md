# V0 范围规格

状态：Draft

## 目标

V0 应证明 Novi 的核心闭环，而不是一开始就引入重型基础设施：

```text
初始化项目
加载技能
创建或打开会话
启动一个可审计 run
记录事件和工具调用
写入 artifact
提出 memory candidate
检查和审阅结果
```

## 必须具备

Proposal:

- `novi init` 在当前项目中创建本地 `.novi/` 工作区。
- 可以列出并加载 `skills/` 中的内置技能。
- 可以创建、列出、打开和总结 sessions。
- 可以启动、列出、检查、完成和失败 runs。
- 每个 run 都有 append-only 的事件日志。
- tool calls 与普通事件分开记录。
- artifacts 是一等记录，包含路径和元数据。
- memory candidates 可以被提出、列出、接受和拒绝。
- policies 至少能表达某个工具是否需要 approval。
- runs 可以记录 agent participants 及其 roles，即使 v0 只使用 orchestrator 和 auditor roles。
- CLI 能检查足够状态，用来解释发生了什么。

## 应该具备

Proposal:

- 最小 context pack builder。
- 小型 tool registry。
- run records 中包含 per-agent tool scope 和 context scope。
- stub 或本地 model runner interface。
- 对 specs 和 records 的基础 schema validation。
- run summary 文件。
- session rolling summary 文件。
- 基础 project memory 和 procedural memory 文件。

## 初始内置技能

Proposal:

先从这些开始：

- `research.review`;
- `run.audit`;
- `memory.curate`.

核心闭环稳定后再考虑：

- `experiment.design`;
- `code.maintain`;
- `dataset.curate`;
- `training.design`;
- `sim.evaluate`;
- `robot.experiment`.

## 初始模块

Proposal:

先从这些开始：

- `filesystem`;
- `shell_sandbox`;
- `git`;
- `python_exec`;
- `search_stub`.

网络搜索、浏览器自动化、ROS、仿真、训练、IM、MCP 和 observability 模块应后置，除非它们是验证第一条闭环所必需的。

## V0 不做

Deferred:

- 完整的 OpenClaw 式 channel gateway。
- 多渠道身份系统。
- 插件市场或插件分发。
- 机器人 fleet 控制。
- 完整 MCP server。
- 复杂 multi-agent graph 或自由形式 agent-to-agent chat。
- 完整 Web dashboard。
- 无审阅的自动长期记忆。
- 不受限的 shell、ROS 或 training 执行。
- robot-first 架构。
- 对 ROS 的硬依赖。
- 对 LangGraph 或 Temporal 的硬依赖。

## V0 成功标准

Proposal:

当用户可以运行：

```bash
novi init
novi skill list
novi session create "physical-ai literature scan"
novi run start research "summarize recent work on physical AI skill learning"
novi run inspect <run_id>
novi memory review
```

并能检查以下内容时，V0 就具备基本价值：

- 当前 active session 是什么；
- 当前 active skill 是什么；
- 哪些 agent roles 参与了 run；
- 创建了哪个 run；
- 使用了什么 context；
- 哪些 tools 可见；
- 哪些 tools 被调用；
- 产出了哪些 artifacts；
- 提出了哪些 memory；
- 还有哪些内容需要 review。
