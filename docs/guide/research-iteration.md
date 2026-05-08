# Research Iteration 循环

这个循环用于快速把 topic、文档、笔记和实验记录转换成可执行的假设、下一步实验和可审查的物理先验候选。

## Novi 负责什么

Novi 负责：

- session、task、run、trace 和 artifact；
- skill 和 workflow 指令；
- 可审查 contribution 和 accepted knowledge；
- 对需要审计的工具进行薄 policy 包装。

## DeepAgents 负责什么

DeepAgents 负责：

- 模型执行；
- agent loop 行为；
- 虚拟 working file 创建；
- 模型侧 tool 选择和 tool call 编排。

Novi 不试图在这个循环里重建完整的研究工具生态。需要工具时，优先暴露已有 DeepAgents-compatible 工具，或仅在审计和 policy 边界有意义时才添加薄 Novi 包装。

## 配置模型

```bash
novi configure model siliconflow \
  --model "deepseek-ai/DeepSeek-V4-Flash" \
  --api-key "YOUR_API_KEY"
```

或使用任意 OpenAI-compatible chat provider：

```bash
novi configure model openai-chat \
  --model "MODEL_NAME" \
  --base-url "https://provider.example.com/v1" \
  --api-key "YOUR_API_KEY"
```

运行前检查：

```bash
novi doctor model
```

SiliconCloud 使用建议：优先选择 LangChain 和 DeepAgents 能正确解析 OpenAI-compatible tool call 的模型。
已验证 `MiniMaxAI/MiniMax-M2.5` 能正确处理 Novi tool call。如果某模型返回空响应或 `finish_reason=tool_calls`
但无可执行 tool call，应在排查 Novi 之前先换模型。

## 从 Topic 开始跑

```bash
novi task "从接触先验角度分析这些材料，设计下一轮最小实验，并抽取隐含物理先验" \
  --workflow research-iteration \
  --kernel deepagents \
  --rounds 1
```

一轮（`--rounds 1`）表示一次完整 research iteration。当前 `research-iteration` workflow 内部跑两个 agent step：

1. `frame_topic`：框定主题并映射证据。
2. `iterate_and_extract`：提出下一轮实验迭代并抽取物理先验候选。

`--steps` 仍然保留，用于内部调试或部分 workflow 执行，但日常研究应使用 `--rounds`。

预期 DeepAgents working file 包括：

- `topic-brief.md`
- `evidence-map.md`
- `hypotheses.md`
- `experiment-plan.md`
- `iteration-log.md`
- `physical-priors.md`
- `next-actions.md`
- `proposals.md`

Novi 会把这些文件导出为 run artifact。

## 添加文档或实验记录

```bash
novi ingest notes/contact-prior-notes.md \
  --task task_... \
  --hint "作为 contact-prior research iteration 的证据材料"
```

对于 PDF 和论文，保留原始文件作为 source artifact，让 skill 或 DeepAgents 的 shell/tool 后端
用项目本地工具（如 `pdftotext`、PyMuPDF、Docling、Marker 或 OCR）提取文本。Novi 不应自己写
PDF 解析器，除非为了可重复性或 artifact 捕获需要薄包装。

对于已知 URL，使用 `curl` 或 browser/computer-use skill，将抓取的页面、清洗后的文本、截图或笔记
存为 artifact。仅在确实需要广域网页发现时才使用 Tavily 或类似搜索 API。

对于实验结果，从 result packet 开始，不要从刚性 schema 开始：

```markdown
---
type: experiment_result
title: Contact-prior trial 001
status: draft
topic: contact-prior
artifacts:
  - data/raw/trial-001.csv
  - plots/trial-001-pressure.png
---

# Contact-prior trial 001

## 尝试了什么

自然语言描述设置、参数和过程。

## 观察

原始结果、异常、失败模式、显著测量值。

## 解读

这看起来支持或削弱了什么，包括不确定性。

## 下一步

最小的有用跟进动作。
```

不清晰的结构留在自然语言里。下一轮 `research-iteration` 可以从 packet 中提取声明、观察、解读和先验更新。

继续前 review 所有 proposal patch：

```bash
novi review --task task_... --check --agent
novi accept --reviewed --task task_...
novi task continue task_... --workflow research-iteration --kernel deepagents --rounds 1
```

## 检查结果

```bash
novi trace latest
novi output latest
novi artifact list
```

把导出的 `physical-priors.md` 视为候选列表，而不是已接受的持久记忆。仅通过 review 路径接受有证据支撑的更新。

使用 `novi task inspect task_...` 查看当前 workflow step、已完成 step 和 run ID。完成一轮
`research-iteration` 后，`completed_step_ids` 应包含 `frame_topic` 和 `iterate_and_extract`，
该轮应有两条新 run ID。

不要立即把每个 prior 候选转成结构化记录。先用 Markdown review；只有在多次实际使用后发现
Markdown review 太松散时，才添加结构化 prior contribution。
