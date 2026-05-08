# Novi Lab

Novi Lab 是一个本地优先、技能优先的研究控制平面。它把 session、run、workflow、tool、artifact、memory proposal、model call 和 review decision 保存在项目本地、可检查的记录中。

Novi 不是 Codex、Claude Code、DeepAgents 或其他执行 agent 的替代品。这些系统可以作为 worker 或 kernel 被 Novi 调用。Novi 负责项目状态、审计链路、workflow 记录、工具策略和 review 边界。

## 从这里开始

- [说明文档索引](docs/guide/README.md)
- [快速开始](docs/guide/quick-start.md)
- [核心概念](docs/guide/concepts.md)
- [CLI 说明](docs/guide/cli.md)
- [Workflow 模型](docs/guide/workflows.md)
- [Research Loop](docs/guide/research-loop.md)
- [Research Iteration](docs/guide/research-iteration.md)
- [文档导入](docs/guide/document-ingest.md)
- [Review 与 Artifacts](docs/guide/review-and-artifacts.md)
- [配置说明](docs/guide/configuration.md)
- [YAML 配置](docs/guide/yaml-config.md)
- [故障排查](docs/guide/troubleshooting.md)

## 当前能做什么

当前原型可以：

- 初始化本地 `.novi/` 工作区；
- 配置 OpenAI-compatible chat 模型和 LiteLLM proxy gateway；
- 运行感知 session 的 `ask`、`run`、`task` 命令；
- 通过 deterministic local kernel 或可选 DeepAgents kernel 执行；
- 归档 prompt pack、model messages、model calls、tool calls、trace 和 artifacts；
- 以 step contract 和 expected output 推进可恢复 task workflow；
- 暴露薄审计工具（filesystem、shell、web、git、artifact）；
- 创建实验目录骨架（`novi experiment init`）；
- 通过 `task note` 和 `task amend` 非阻塞注入人工指导；
- 用 `novi watch --follow` 实时观察 run 进度；
- 把导入文档处理成可审查 proposal；
- review、check、accept 文档 patch contribution。

当前最有用的闭环是：

```bash
novi init
novi configure model siliconflow --model "..." --api-key "..."
novi task "研究目标" --workflow research-iteration --kernel deepagents --rounds 1
novi trace latest
novi output latest
novi artifact list
```

## 文档结构

- `docs/guide/`：面向用户的说明文档，解释设计逻辑和实际用法。
- `docs/spec/`：英文工作规格。
- `docs/spec_zh/`：与英文版对齐的中文规格。
- `docs/plans/`：具体开发切片的实施计划。
- `docs/impl/`：实现记录和开发日志。

根目录 README 只做说明入口，不作为开发记录。

## 开发

使用 `uv` 管理 Python 环境：

```bash
uv sync --extra all
uv run --extra all pytest
```

开发期优先使用 console script：

```bash
uv run --extra all novi --help
```

## 仓库约定

- 不直接 push 到远端 `main`。
- 进入 `main` 的改动应通过 pull request。
- 面向用户的说明放在 `docs/guide/`。
- 开发记录放在 `docs/impl/`。
- 明确批准 spec 变更时，同步维护 `docs/spec/` 和 `docs/spec_zh/`。
