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
novi task list
novi task inspect task_...
novi task continue task_... --steps 2
novi task close task_...
```

`task` 是推荐入口。它把目标绑定到 workflow，并为每一步创建可审计 run。

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
```

顶层别名：

```bash
novi output latest
novi trace latest
```

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
novi workflow list
novi workflow show research-loop
```

## ID 使用原则

Novi 仍保留 ids 以便审计和脚本化，但日常命令应尽量支持 `latest`、`all`、`--task` 和自动选择最新 pending item，减少手动复制 id。
