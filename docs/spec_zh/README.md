# Novi Lab 规格

这个目录保存与英文 `docs/spec/` 对齐的中文规格。目标是把产品边界、架构方向和 v0/Phase 1.x 范围说清楚。

这些文档是工作规格，不是面向用户的使用说明。方向明确并且用户批准 spec 变更时，同步修改英文和中文规格；仍需讨论的取舍，放到 `open-questions.md`。

## 当前文档

建议按这个顺序阅读：

1. `v0-scope.md`：收敛第一个可用版本。
2. `philosophy.md`：定义 post-Phase 1 修订应遵循的 feedback-governed research-agent 哲学。
3. `architecture.md`：定义核心产品形态和系统边界。
4. `tooling-and-modules.md`：讨论候选工具和模块边界。
5. `exploration.md`：探索 configurable agents、workflow iteration、collaboration 和 scientific memory 如何共同演化。
6. `features.md`：整理产品 feature 表和优先级。
7. `roadmap.md`：整理方向性路线图。
8. `data-model.md`：定义持久对象和记录格式。
9. `cli.md`：定义第一版命令行界面。
10. `open-questions.md`：列出仍需确认的决策。

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

核心 v0 方向已经接受。Phase 1 本地核心实现已经可用，Phase 1.5 正在收敛为 integrated research loop。

当前原型已经可以创建本地 `.novi/` 工作区、列出 skills、创建和打开 sessions、创建 runs、归档 prompt/context 记录、保存 project-local model 配置、通过 deterministic local kernel 或可选 DeepAgents kernel 执行、调用 OpenAI-compatible chat-completions provider，并检查 run output/trace。`novi ask` 会记录多轮 user/assistant messages，并创建可审计 runs。`novi task` 可以创建由 workflow 支撑的可恢复任务、推进 workflow steps、把模型回复和 DeepAgents working files 归档为 artifacts，并在存在 pending contribution 时停在 review gate。`novi ingest` 会把导入文档保存为 artifacts，并可把 agent proposal 转成可 review 的 document patch contribution。

Phase 1.5 已经具备真实最小 research-iteration loop。`research-iteration` workflow 使用 `topic.research`、`document.evidence`、`experiment.iterate` 和 `physics.prior.extract` skills，把 topic 或松散材料转成 topic brief、evidence map、hypotheses、experiment plan、iteration log、physical-prior candidates 和 proposals。使用 SiliconCloud/OpenAI-compatible 的 `MiniMaxAI/MiniMax-M2.5` 已验证 DeepAgents 可以调用 Novi-wrapped tools，并把 working files 导出为 Novi artifacts。Provider compatibility 仍然和具体模型有关；如果某个模型返回不规范 chat-completions tool-call role，应优先切换模型，而不是把它视为 Novi Tool Runtime 错误。

Source intake 保持轻量。PDF、论文、网页、实验日志、datasets、plots 和 videos 应先作为 source/result artifacts 进入系统。Skills 和 DeepAgents 可以调用外部命令或后续 browser/search tools，把它们抽取成可用 Markdown。除非真实任务反复证明自然语言 result packet 和 Markdown review 太松，否则 Novi 不应过早引入重 scientific schema。

本 spec 集已冻结，除非用户明确批准 spec 变更。批准修改时应同步维护英文 `../spec/`。开发过程和实现记录应放在 `../impl/`；面向用户的说明文档应放在 `../guide/`。
