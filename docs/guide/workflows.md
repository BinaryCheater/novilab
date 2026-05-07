# Workflow 模型

Workflow 描述任务如何推进。它不是把所有过程写死成机械流水线，而是给系统、agent 和人类 review 提供共同的执行骨架。

## WorkflowSpec 位置

初始化后默认 workflow 在：

```text
.novi/workflows/document-merge.yaml
.novi/workflows/research-loop.yaml
.novi/workflows/research-iteration.yaml
.novi/workflows/analysis-loop.yaml
.novi/workflows/experiment-loop.yaml
.novi/workflows/improvement-loop.yaml
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

## Step Contract

Workflow step 可以声明运行时契约。Novi 不理解实验或分析的领域语义，但会把这些字段注入 prompt，并可用它们检查产物是否齐备：

```yaml
steps:
  - id: run_or_plan
    title: Run or plan experiment
    kind: agent_run
    actor: agent
    required_tools:
      - filesystem.read
      - filesystem.write
      - filesystem.list
      - shell.run
      - artifact.save
    expected_files:
      - metrics.md
      - notes.md
      - next-actions.md
    expected_artifacts:
      - shell_output
    continue_from:
      - prior_task_runs
      - latest_outputs
```

字段含义：

- `required_tools`：这一步预期可使用的工具。它会进入 prompt，帮助 agent 明确该用什么能力。
- `expected_files`：这一步预期在 workspace 里留下的文件。
- `expected_artifacts`：这一步预期在 Novi run artifact 中留下的 artifact 类型。
- `continue_from`：提示 agent 如何利用前序 run，例如 prior task runs 或 latest outputs。

执行 task 时，CLI 会打印当前 step 的 contract：

```bash
novi task "运行最小实验并总结结果" --workflow experiment-loop --rounds 1
```

检查当前 run 是否满足 workflow step 的 expected outputs：

```bash
novi run check latest --from-workflow
```

查看 task 当前缺什么：

```bash
novi task inspect task_...
```

## 非阻塞 Human-in-the-loop

Novi 当前采用 run 间指导，而不是 run 内强打断。人类可以在任何时候追加指导：

```bash
novi task note task_... "下一轮优先检查 Q6 failure attribution。"
novi task amend task_... "更新目标：跑最小 Q6 诊断并总结下一步。"
```

这些指导会保存在 task 记录中，并在下一次 `task continue` 构造 prompt 时作为
`Human guidance` 注入。它不会中断已经进入模型调用的 run。

如果需要阻止后续自动继续：

```bash
novi task pause task_...
novi task resume task_...
```

`pause` 只阻止下一次 `task continue`；它不是模型调用级别的取消或 checkpoint 恢复。

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
