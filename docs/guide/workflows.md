# Workflow 模型

Workflow 描述任务如何推进。它不是把所有过程写死成机械流水线，而是给系统、agent 和人类 review 提供共同的执行骨架。

## WorkflowSpec 位置

初始化后默认 workflow 在：

```text
.novi/workflows/document-merge.yaml
.novi/workflows/research-loop.yaml
.novi/workflows/reflection-loop.yaml
```

查看：

```bash
novi workflow list
novi workflow show research-loop
```

## Step Kind

`kind` 是 workflow step 的类型提示，用来说明这一步应该如何执行或记录。常见类型：

- `load_source`：系统加载输入。
- `produce_artifact`：产出 artifact。
- `agent_run`：由 agent/kernel 执行。
- `produce_contribution`：产出待审 contribution。
- `check`：系统检查，例如 patch dry-run。
- `review_gate`：人类或 reviewer 审查。
- `apply_change`：应用已接受变更。
- `decision`：决定继续、暂停或关闭。

`actor` 表示执行方：

- `system`
- `agent`
- `human`
- `human_or_agent`

## Task 如何使用 Workflow

`novi task` 会读取 workflow，创建 task，并在 `task.yaml` 中保存：

```yaml
workflow_state:
  workflow_id: research-loop
  current_step_id: work
  completed_step_ids:
    - plan
  iteration: 1
```

每次 `task continue` 会选择当前 step，创建 run，归档 prompt/context/artifacts，然后推进 `workflow_state`。

## Review Gate

当 task 下有 pending contribution 时，`task continue` 会停下：

```bash
novi review --task task_... --check --agent
novi accept --reviewed --task task_...
novi task continue task_...
```

这保证 agent 不能绕过 review 直接修改 accepted state。

## 与通用 Agent Session 的关系

Codex、Claude Code 或 DeepAgents 可以在一个 session 中自己推理和推进任务。Novi 不试图替代这种推理过程。Novi 的 workflow 负责把关键边界显式化：

- 当前目标是什么；
- 当前 step 是什么；
- 用了哪些 context 和 tools；
- 产出了哪些 artifacts；
- 哪些变更需要 review；
- accepted state 如何进入下一轮。

