# Research Loop

Novi 当前已经可以跑一个本地可审计、有产物的 research loop。它暂时不包含联网搜索、PDF 解析和浏览器自动化；这些属于后续 research tools。

## 基本命令

```bash
novi task "围绕接触先验整理已有知识，形成一版研究假设和下一步行动" --steps 2
```

继续：

```bash
novi task continue task_... --steps 2
```

查看：

```bash
novi trace latest
novi output latest
novi artifact list
```

## 每一步会发生什么

1. Novi 读取 task 的 `workflow_state`。
2. 选择当前 workflow step。
3. 构造 context pack 和 prompt archive。
4. 调用 kernel，例如 DeepAgents。
5. 归档模型回复、working files、model messages、tool calls。
6. 更新 run 和 task state。
7. 如果产生 contribution，后续继续会被 review gate 阻挡。

## 产物位置

每个 run 位于：

```text
.novi/runs/<run_id>/
```

关键文件：

```text
response.md
summary.md
model_calls.jsonl
deepagents_messages.jsonl
deepagents_files/
prompt.md
prompt_parts/
artifacts/
```

DeepAgents run 会登记：

- `model_response` artifact：模型主回复。
- `deepagents_file` artifact：模型写出的工作文件，例如 `research-note.md`、`next-actions.md`。

## 预期输出

模型 prompt 会鼓励产出：

- `research-note.md`：发现、综合、假设、不确定性。
- `next-actions.md`：下一步行动和开放问题。
- `proposals.md`：需要 review 的知识、skill 或 workflow 改动建议。

这些文件先作为 run artifacts 被归档。是否进入 accepted knowledge 或修改项目文件，仍需要 review/contribution 路径。

## 当前限制

- 还没有联网 search/web/pdf/browser 工具闭环。
- 还没有策略 runner 自动决定跑多少步或何时关闭 task。
- 还没有完整 TUI/Web 控制面。

