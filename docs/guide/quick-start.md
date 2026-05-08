# 快速开始

## 1. 初始化

在你的项目目录中运行：

```bash
novi init
```

检查状态：

```bash
novi status
```

## 2. 配置模型

SiliconFlow 示例：

```bash
novi configure model siliconflow \
  --model "deepseek-ai/DeepSeek-V4-Flash" \
  --api-key "YOUR_API_KEY"
```

通用 OpenAI-compatible provider：

```bash
novi configure model openai-chat \
  --model "MODEL_NAME" \
  --base-url "https://provider.example.com/v1" \
  --api-key "YOUR_API_KEY"
```

检查配置：

```bash
novi doctor model
```

## 3. 跑一个有产物的 research loop

```bash
novi task "围绕接触先验整理已有知识，形成一版研究假设和下一步行动" --steps 2
```

如果目标是快速完成 topic、证据、实验迭代和物理先验候选的闭环，使用：

```bash
novi task "围绕接触先验分析材料，设计下一轮最小实验，并抽取隐含物理先验" \
  --workflow research-iteration \
  --kernel deepagents \
  --rounds 1
```

查看输出：

```bash
novi output latest
novi trace latest
novi artifact list
```

实时观察 run：

```bash
novi watch latest --follow
```

继续推进：

```bash
novi task list
novi task continue task_... --rounds 1
```

在人类不阻塞主循环的情况下追加指导：

```bash
novi task note task_... "下一轮优先检查失败归因，不要扩大模型。"
novi task amend task_... "更新目标：跑最小 Q6 诊断并总结下一步。"
novi task continue task_... --rounds 1
```

`note` 和 `amend` 不会打断正在运行的 run。它们会记录到 task，并在下一次
`task continue` 构造 prompt 时注入为 `Human guidance`。

暂停和恢复：

```bash
novi task pause task_...
novi task resume task_...
```

暂停只阻止后续 `task continue`，不尝试中断已经进入模型调用的 run。

## 4. 导入文档

```bash
novi ingest notes.md --hint "和接触先验相关，整理进知识库"
```

挂到已有 task：

```bash
novi ingest notes.md --task task_... --hint "作为这个研究任务的背景材料"
```

## 5. Review 和接受变更

如果产生 proposal：

```bash
novi review --check --agent
novi accept --reviewed
```

按 task 过滤：

```bash
novi review --task task_... --check --agent
novi accept --reviewed --task task_...
```

## 开发源码运行

在仓库内运行源码版本：

```bash
uv run --extra all novi --help
uv run --extra all novi task "研究目标" \
  --workflow research-iteration \
  --rounds 1
```

## 原子工具和实验循环

默认 orchestrator 可见这些薄工具：

- `filesystem.read`
- `filesystem.write`
- `filesystem.list`
- `shell.run`
- `web.fetch`
- `artifact.save`
- `git.status`

创建一个通用实验骨架时必须显式指定路径。Novi 不会默认写入仓库里的
`experiment/` 或 `experiments/` 目录：

```bash
novi experiment init scratch-exp/contact-prior-smoke
```

运行或检查实验类 workflow：

```bash
novi task "运行最小实验并总结结果" \
  --workflow experiment-loop \
  --kernel deepagents \
  --rounds 1

novi run check latest --from-workflow
```
