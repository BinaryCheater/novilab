# Novi Lab 规格草案

这个目录把启动说明整理成便于审阅和修改的中文规格草案。目标是在开始写代码之前，先把产品边界、架构方向和 v0 范围说清楚。

这些文档不是最终文档，而是工作草案。方向明确时，直接修改对应规格；仍需讨论的取舍，放到 `open-questions.md`。

## 当前文档

建议按这个顺序阅读：

1. `v0-scope.md`：收敛第一个可用版本。
2. `architecture.md`：定义核心产品形态和系统边界。
3. `tooling-and-modules.md`：讨论候选工具和模块边界。
4. `features.md`：整理产品 feature 表和优先级。
5. `roadmap.md`：整理方向性路线图。
6. `data-model.md`：定义持久对象和记录格式。
7. `cli.md`：定义第一版命令行界面。
8. `open-questions.md`：列出仍需确认的决策。

## 背景来源

背景来源是 `../../novi_lab_repo_bootstrap_summary.md`。它包含完整愿景和路线图。本目录中的规格文档会有意收敛范围，服务于第一个实际可构建版本。

## 工作定位

Novi Lab 是一个以技能为优先、感知会话状态的控制平面，用于自主研究、编码、训练和 physical-AI 实验。它围绕 skills、sessions、runs、tools、memory、artifacts 和 policies 组织工作，并把 ROS、仿真器、模型训练器、Codex、Claude Code、MCP servers 和聊天渠道等外部系统保持为可插拔模块。

## V0 设计倾向

V0 应验证核心闭环：

```text
novi init
novi configure model siliconflow --model "..."
novi skill list
novi session create
novi ask "..."
novi run start research "..."
novi run inspect <run_id>
novi run output latest
novi run trace latest
novi memory review
```

第一版应本地优先、可检查、易修改。它应支持 agent roles 和 per-agent scopes，但不应依赖 ROS、MCP、Web dashboard、插件市场或复杂 multi-agent orchestration。

## 审阅约定

编辑时使用这些标签：

- `Proposal`：当前建议方向。
- `Decision`：已经接受的方向。
- `Open`：仍需确认的问题。
- `Deferred`：真实需求，但不阻塞 v0。

审阅时重点看：

- v0 闭环是否足够有用；
- 持久记录是否缺少重要信息；
- 是否有内容对第一版过宽；
- 是否有术语含混或重复。

## 当前状态

核心 v0 方向已经接受，Phase 1 实现正在推进中。

当前原型已经可以创建本地 `.novi/` 工作区、列出 skills、创建和打开 sessions、创建 runs、归档 prompt/context 记录、保存 project-local model 配置、通过 deterministic local kernel 或可选 DeepAgents kernel 执行、调用 OpenAI-compatible chat-completions provider，并检查 run output/trace。`novi ask` 会记录多轮 user/assistant messages，并创建可审计 runs。由模型触发的 read-only tool call 可以经过 Novi Tool Runtime，并带 source attribution 写入日志。

本 spec 集已冻结。除非用户明确批准 spec 变更，否则不要编辑本目录文件。开发过程和实现记录应放在 `../impl/`。
