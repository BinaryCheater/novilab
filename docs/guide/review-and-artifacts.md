# Review 与 Artifacts

## Review Gate

Novi 的默认策略是：agent 可以产出 proposal，但不能静默修改 accepted state。修改知识库、workflow 或 skill 的变更应成为 contribution，经过 review 后再接受。

常用命令：

```bash
novi review --check
novi review --check --agent
novi accept latest
novi accept all
novi accept --reviewed
```

按 task 过滤：

```bash
novi review --task task_... --check --agent
novi accept --reviewed --task task_...
```

## Deterministic Reviewer

当前 reviewer 是保守 deterministic policy：

- patch 能 clean apply；
- target scope 合法；
- agent source refs 完整；
- 无冲突。

满足条件的 `document_patch` 会标记为 `safe_to_accept`。冲突、raw import 或不完整来源会留给人类处理。

## Artifacts

Artifact 是 run 或 ingest 产生的可追溯文件。查看：

```bash
novi artifact list
novi artifact show art_...
```

常见 artifact 类型：

- `knowledge_import`
- `analysis_note`
- `model_response`
- `deepagents_file`
- `research_note`
- `agent_step_note`

## Trace

```bash
novi trace latest
```

Trace 会显示：

- accepted knowledge refs；
- model calls；
- DeepAgents messages；
- tool calls；
- artifacts；
- DeepAgents files；
- kernel bindings。

## 为什么不直接写文件

直接写 accepted state 会让用户无法判断：

- 来源是什么；
- 哪个 agent 做了修改；
- 是否经过检查；
- 是否和当前文档冲突；
- 后续 run 为什么看到了这些内容。

Contribution/review 路径让这些问题都有记录。

