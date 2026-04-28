# CLI 规格

状态：Draft

V0 CLI 应先暴露核心闭环，再考虑 TUI、Web dashboard、IM channels 或 plugin distribution。

## 命令风格

Proposal:

优先使用显式 noun + verb：

```text
novi <noun> <verb> [args]
```

短 alias 可以在命令行为稳定后再添加。

## Project Commands

### `novi init`

在当前项目中创建 `.novi/` 工作区。

预期输出：

- project config created；
- default directories created；
- built-in skills discovered or copied；
- next suggested command。

### `novi status`

显示当前 project、active session、active run、pending approvals 和 memory candidates。

## Skill Commands

### `novi skill list`

列出 built-in 和 project-local skills。

应显示：

- skill id；
- source；
- short description；
- 是否在当前 session 中 active。

### `novi skill inspect <skill_id>`

显示 skill metadata、path、commands、required tools、optional tools 和 policies。

## Session Commands

### `novi session create <title>`

在当前项目中创建 session。

应创建：

- `session.yaml`；
- `summary.md`；
- `messages.jsonl`。

### `novi session list`

列出 sessions，包含 status、updated time、title 和 current run。

### `novi session open <session_id>`

把某个 session 标记为后续命令使用的 active session。

### `novi session inspect <session_id>`

显示 session summary、active skills、run ids、open questions、memory candidates 和 artifacts。
当 session 有 active agent roles 时，也应显示它们。

## Run Commands

### `novi run start <type> <objective>`

在 active session 中创建并启动 run。

V0 可以优先支持这些 run types：

```text
research
audit
analysis
```

该命令应创建：

- `run.yaml`；
- `events.jsonl`；
- `tool_calls.jsonl`；
- `summary.md`；
- `artifacts/`。

### `novi run list`

列出当前 session 的 runs，显示 status、type、updated time 和 objective。

### `novi run inspect <run_id>`

显示：

- objective；
- status；
- agent participants 和 roles；
- active skills；
- context packs；
- visible tools；
- tool calls；
- artifacts；
- memory candidates；
- summary；
- errors 或 blocked approvals。

### `novi run cancel <run_id>`

在可取消时取消 run，并记录 `RunCancelled` event。

## Memory Commands

### `novi memory review`

列出等待 review 的 memory candidates。

### `novi memory accept <candidate_id>`

把 memory candidate 提交到对应 memory store，并记录 decision。

### `novi memory reject <candidate_id>`

拒绝 memory candidate，并在有说明时记录 decision note。

### `novi memory search <query>`

搜索 project、session、episodic 和 procedural memory。V0 可以先使用简单文本搜索。

## Tool Commands

### `novi tool list`

列出 registered tools 及其 risk level。

### `novi tool inspect <tool_id>`

显示 schema、module、risk、policies 和 approval requirements。

## Approval Commands

### `novi approval list`

列出 pending approvals。

### `novi approval approve <approval_id>`

批准 pending action，并记录 approval event。

### `novi approval reject <approval_id>`

拒绝 pending action，并记录 rejection event。

## 暂缓命令

Deferred:

这些命令有意后置：

- `novi plugin install`；
- `novi connect telegram`；
- `novi mcp serve`；
- `novi dashboard`；
- direct ROS、simulation 或 training commands。

它们可以在本地 run loop 稳定后再添加。
