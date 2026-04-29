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

### `novi configure model <provider>`

把 project-local model 配置写入 `.novi/novi.yaml`。

第一批 provider：

```text
siliconflow
openai-chat
openai-responses
```

预期行为：

- `siliconflow` 是 SiliconFlow OpenAI-compatible chat-completions API 的便利配置。
- `openai-chat` 用于任何暴露 OpenAI-compatible `/v1/chat/completions` endpoint 的 provider。
- `openai-responses` 预留给支持 OpenAI Responses API 的 provider。
- Phase 1 原型可以把 API key 保存在 `.novi/novi.yaml`，但 CLI 不能把 secret 回显到终端。
- 环境变量可以继续作为 fallback，但 project config 是 Phase 1 更可复现的默认路径。

示例：

```text
novi configure model siliconflow --model "deepseek-ai/DeepSeek-V4-Flash" --api-key "..."
```

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

## Ask Command

### `novi ask <message>`

向 active session 追加一条 user message，创建 run，把 session 最近的 user/assistant turns 作为 chat messages 发送，记录 assistant response，并在终端打印 response。

预期行为：

- 默认使用 active session；
- shared session options 可用后支持 `--session <id>`；
- 支持 `--kernel simple|deepagents`；
- 把 user/assistant turns 写入 session 的 `messages.jsonl`；
- 写入 `system_prompt.md`、`model_messages.jsonl`、`prompt.md`、`response.md` 和 trace files；
- `prompt.md` 是人类可读 archive，不一定等同于 provider request body。

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
- `model_calls.jsonl`；
- `summary.md`；
- `artifacts/`。

V0 从 deterministic mock/local runner 起步；配置兼容模型 provider 后，可以通过 `--kernel deepagents` 使用 DeepAgents kernel。`research` run 无论是否连接真实 LLM，都应创建可检查 records。

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

### `novi run output <run_id|latest>`

打印 run 的主要 response 或 summary artifact。这是 CLI run 之后查看模型输出的最快入口。

### `novi run trace <run_id|latest>`

打印面向操作者的 run trace 摘要。

应包含：

- run id 和 status；
- model provider、model profile、base URL 和 kernel；
- `system_prompt.md`、`model_messages.jsonl`、`prompt.md`、`response.md` 等 request/archive 路径；
- 如果存在 DeepAgents message 和 file archive，也应显示；
- tool calls，并标明 `manual`、`runner_preflight` 或 `deepagents_model` 等 source attribution；
- blocked/error 信息。

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

原型说明：在命令面最终统一前，已实现命令可能叫 `novi tool show <tool_id>`。

## Doctor Commands

### `novi doctor model`

检查 active model 配置，但不打印 secrets。

应显示：

- provider；
- model；
- base URL；
- API key 是否已配置；
- 该 provider 应使用 compatible chat-completions 还是 Responses API 路径。

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
