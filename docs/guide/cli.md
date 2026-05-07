# CLI 说明

## 主线命令

### Workspace

```bash
novi init
novi status
novi ps
```

### Task

```bash
novi task "研究目标"
novi task "研究目标" --steps 3
novi task "研究目标" --workflow experiment-loop --rounds 1
novi task list
novi task inspect task_...
novi task continue task_... --steps 2
novi task note task_... "下一轮优先检查失败归因"
novi task amend task_... "更新后的目标"
novi task pause task_...
novi task resume task_...
novi task close task_...
```

`task` 是推荐入口。它把目标绑定到 workflow，并为每一步创建可审计 run。
`note` 和 `amend` 是非阻塞 human-in-the-loop 机制：它们记录人工指导，
并在下一次 `task continue` 的 prompt 中注入，不会打断正在执行的 run。

### Ask

```bash
novi ask "问题"
```

`ask` 适合对话式询问，但仍会创建 run 并归档 trace。

### Run

```bash
novi run start research "目标"
novi run inspect latest
novi run prompt run_...
novi run output latest
novi run trace latest
novi run check latest --from-workflow
```

顶层别名：

```bash
novi output latest
novi trace latest
```

观察最新 run：

```bash
novi watch latest
novi watch latest --follow
```

`watch --follow` 会持续刷新运行状态；如果 run 已完成，会打印一次后退出。

### Experiment

```bash
novi experiment init scratch-exp/contact-prior-smoke
```

实验模板会创建：

```text
scratch-exp/contact-prior-smoke/
  README.md
  run.sh
  outputs/
  metrics.md
  notes.md
```

模板路径必须显式指定。Novi 会拒绝把模板创建到仓库的 `experiment/` 或
`experiments/` 目录下，避免碰到用户已有实验目录。

### Document Ingest

```bash
novi ingest notes.md --hint "如何理解这份材料"
novi ingest note-a.md note-b.md --task task_...
novi process
```

`ingest` 更适合日常使用；`process` 是底层处理入口。

### Review

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

### Artifacts

```bash
novi artifact list
novi artifact show art_...
```

### Knowledge

```bash
novi knowledge list
novi knowledge show contrib_...
```

### Agent, Tool, Workflow

```bash
novi agent list
novi agent show agent_orchestrator
novi tool list
novi tool show filesystem.read
novi tool call filesystem.write --arg path=notes/result.md --arg content="..."
novi tool call shell.run --arg "command=./run.sh" --arg cwd=scratch-exp/contact-prior-smoke
novi workflow list
novi workflow show research-loop
```

## ID 使用原则

Novi 仍保留 ids 以便审计和脚本化，但日常命令应尽量支持 `latest`、`all`、`--task` 和自动选择最新 pending item，减少手动复制 id。
