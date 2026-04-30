# Novi Lab 使用说明

状态：Phase 1 原型可用。本文描述当前已经实现的本地 CLI 工作流，以及这些命令背后的设计逻辑。

## 1. 适用范围

Novi Lab 当前适合在一个本地项目目录中使用，用来创建 `.novi/` 工作区、管理 session、启动 run、接入 OpenAI-compatible chat-completions 模型、记录多轮对话、观察 model/tool trace，并保留可人工检查的 Markdown/YAML/JSONL 记录。

当前重点不是完整 multi-agent 平台，也不是 Web dashboard、MCP server 或机器人控制系统。Novi 的定位是本地优先、可检查、可审计的控制平面。

## 2. 安装与运行方式

开发期推荐使用 `uv run` 从仓库源码运行：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli --help
```

如果本机 `uv` cache 权限受限，可以把 cache 放到项目内：

```bash
UV_CACHE_DIR=.uv-cache uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli --help
```

如果已经通过包安装并暴露了脚本入口，也可以使用：

```bash
novi --help
```

## 3. 初始化工作区

在要使用 Novi 的项目目录中执行：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli init
```

成功后会创建 `.novi/`。这个目录是 Novi 的本地 source of truth，包含项目配置、sessions、runs、memory candidates、工具调用日志和模型调用日志。

查看状态：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli status
```

## 4. 配置模型

### 4.1 SiliconFlow

SiliconFlow 使用 OpenAI-compatible chat-completions API，可以这样配置：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli configure model siliconflow \
  --model "deepseek-ai/DeepSeek-V4-Flash" \
  --api-key "YOUR_API_KEY"
```

默认 base URL 是：

```text
https://api.siliconflow.cn/v1
```

### 4.2 通用 OpenAI-compatible provider

如果第三方供应商支持 `/v1/chat/completions`：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli configure model openai-chat \
  --model "MODEL_NAME" \
  --base-url "https://provider.example.com/v1" \
  --api-key "YOUR_API_KEY"
```

检查当前模型配置：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli doctor model
```

注意：Phase 1 原型会把 model config 写入 `.novi/novi.yaml`。CLI 不会回显 API key 的内容，只显示是否已设置。后续仍需要决定是否迁移到 `.novi/secrets.yaml`、环境变量或系统 keychain。

## 5. Session 工作流

创建 session：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli session create "siliconflow smoke"
```

列出 session：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli session list
```

打开某个 session：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli session open sess_...
```

检查 session：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli session inspect sess_...
```

Session 是长期工作上下文，不只是 chat history。当前实现会在 session 中记录 user/assistant messages，并把 run ids 关联回 session。

## 6. 运行任务

### 6.1 单次 run

使用 deterministic local kernel：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli run start research "总结当前项目状态" --kernel simple
```

使用 DeepAgents kernel 和已配置的 API provider：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli run start research "用一句话说明 Novi 已经接入当前模型。" --kernel deepagents
```

`run start` 会创建 run 目录、写入 run record、context/prompt archive、model/tool logs、summary 和 artifacts。

### 6.2 多轮对话

推荐使用 `novi ask` 做多轮对话：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli ask "用一句话说明你是谁。"
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli ask "上一句回答里提到的系统叫什么？"
```

`ask` 会：

- 向 active session 的 `messages.jsonl` 追加 user message；
- 使用最近的 user/assistant turns 组成 chat messages；
- 创建一个新的 run；
- 执行 kernel；
- 把 assistant response 写回 session messages；
- 在终端打印 response。

## 7. 查看输出与 Trace

查看最新 run 的模型输出：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli run output latest
```

查看最新 run 的 trace：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli run trace latest
```

查看 run 结构化摘要：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli run inspect run_...
```

查看 prompt archive：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli run prompt run_...
```

关键文件通常在：

```text
.novi/runs/<run_id>/
  run.yaml
  events.jsonl
  tool_calls.jsonl
  model_calls.jsonl
  system_prompt.md
  model_messages.jsonl
  model_request.yaml
  prompt.md
  prompt_parts/
  deepagents_messages.jsonl
  deepagents_files/
  response.md
  summary.md
  artifacts/
```

其中：

- `response.md` 是主输出。
- `model_calls.jsonl` 记录模型调用元数据。
- `tool_calls.jsonl` 记录工具调用、来源、policy result 和执行状态。
- `system_prompt.md` 保存稳定 system/skill/tool instructions。
- `model_messages.jsonl` 保存结构化 chat messages。
- `prompt.md` 是人类可读归档，不保证等同于 provider 的精确请求体。

## 8. Tool 使用

列出工具：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli tool list
```

查看工具：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli tool show filesystem.read
```

手动调用工具：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli tool call filesystem.read \
  --agent agent_orchestrator \
  --arg path=README.md
```

设计上，所有工具调用都应经过 Novi Tool Runtime，而不是让 kernel 或外部框架直接拿高风险工具。当前已验证的重点是 read-only 工具调用记录和 DeepAgents model-triggered tool call 的路由。写文件、shell、network、external side effect 和 physical world 类能力需要更严格的 policy/approval 后再扩大。

## 9. Memory Review

查看待审 memory candidates：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli memory review
```

接受：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli memory accept memcand_...
```

拒绝：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli memory reject memcand_...
```

设计原则是：agent/kernel 可以提出 memory candidate，但不能直接写入长期 memory。长期记忆必须可审阅、可追溯，并尽量引用 run/artifact evidence。

## 10. 文档处理与 Patch Review

导入文档后，可以先让 Novi 的 deterministic document-merge workflow 处理导入贡献：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli process contrib_... \
  --workflow document-merge \
  --target .novi/knowledge/topics/physical-priors.md
```

这会创建一个 processing run、一个 analysis note artifact，以及一个 `document_patch` contribution。没有 `--target` 时只生成 analysis note，不生成可 apply patch。

使用 DeepAgents/LLM 路径：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli process contrib_... \
  --workflow document-merge \
  --target .novi/knowledge/topics/physical-priors.md \
  --kernel deepagents
```

LLM 路径会把 WorkflowSpec、`document.curate`、`document.merge`、导入文档和目标文档拼成 `processing_prompt.md`。模型应优先返回 virtual files：

```text
/analysis_note.md
/proposed.md
```

如果执行环境不支持 virtual files，也可以返回 JSON：

```json
{"analysis_markdown": "...", "proposed_markdown": "..."}
```

Novi 会把 analysis 写成 artifact，把 proposed target document 转成 `document_patch` contribution。是否合并仍然由 `contribution check/accept` 控制。

检查 patch：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli contribution check contrib_...
```

接受并应用 patch：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli contribution accept contrib_...
```

要求修改：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli contribution request-changes contrib_... \
  --reason "Need clearer source links."
```

第一版 patch target 只允许 `.novi/knowledge/`、`.novi/workflows/` 和 `.novi/skills/`。如果目标文件在 patch 生成后被修改，accept 会标记 conflict，不会写入目标文件。

## 11. Workflow 配置

`novi init` 会创建默认 workflow：

```text
.novi/workflows/document-merge.yaml
```

列出 workflows：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli workflow list
```

查看 workflow：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli workflow show document-merge
```

WorkflowSpec 用来描述混合步骤：system 机械步骤、agent 步骤和 human review gate。当前 `document-merge` 包含 load source、analyze、draft patch、check、review、apply 等步骤。`novi process` 会把 workflow id/version、step results 和 `workflow_prompt.md` 归档到 run，后续接入 LLM 时可直接使用这些步骤说明和 skill refs。

## 12. Agent 配置

列出 agents：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli agent list
```

查看 agent：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli agent show agent_orchestrator
```

创建 agent：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli agent create agent_reviewer --role auditor
```

授予工具：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli agent grant-tool agent_reviewer filesystem.read
```

添加 skill：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli agent add-skill agent_reviewer run.audit
```

Agent 在 Novi 中首先是权限、工具、上下文和审计边界，不是为了模拟多人聊天而存在。

## 13. 设计逻辑

### 13.1 Local-first

Novi 把 `.novi/` 作为本地可读的记录系统。必须结构化的内容使用 YAML/JSONL；需要人类阅读、审查、归档的内容优先使用 Markdown。

### 13.2 Run 是审计单位

每次执行都是 run。Run 记录 objective、participants、context pack、model calls、tool calls、events、artifacts、summary 和 memory candidates。这样用户可以在任务结束后回答三个问题：发生了什么、为什么发生、产物在哪里。

### 13.3 Session 管长期上下文

Session 负责承载长期工作上下文和多轮 messages。`novi ask` 不只是聊天命令，它仍然创建 run，让每一轮模型执行都可审计。

### 13.4 Prompt 与请求分层

Novi 把 prompt/context 拆成几类文件：

- 稳定部分：system prompt、skill instructions、tool descriptions。
- 动态部分：recent user/assistant messages。
- 归档部分：人类可读 prompt archive 和 prompt parts。
- 执行 trace：model calls、DeepAgents messages、tool calls。

这种分层让多轮对话拼接更清楚，也有利于支持 provider 侧 prompt/cache 命中。

### 13.5 DeepAgents 是 kernel，不是 source of truth

DeepAgents 可以负责复杂执行循环、工具调用和后续 subagent/checkpoint 能力。但 Novi 仍拥有 sessions、runs、tools、artifacts、memory、policy 和 audit。DeepAgents working files 默认是执行工作区，只有被 Novi export/register 后才成为 artifacts。

### 11.6 Provider 可替换

当前先支持 OpenAI-compatible chat completions，足够连接 SiliconFlow 等第三方供应商。LiteLLM 后续可以作为 provider gateway，但不是 Phase 1 的前置条件。

## 12. 常见问题

### 12.1 401 但 curl 成功怎么办？

优先检查 `.novi/novi.yaml` 里的 `model.api_key` 是否和 curl 使用的是同一个 key，再运行：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli doctor model
```

如果 `API key: unset`，说明当前 workspace 没有配置 key，或命令运行在另一个目录。

### 12.2 CLI 没有输出怎么办？

先看最新 run 输出：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli run output latest
```

再看 trace：

```bash
uv run --python 3.12 --extra dev --extra deepagents python -m novi_lab.cli run trace latest
```

### 12.3 compatible 模式缺什么？

OpenAI-compatible chat completions 足够支持基础 messages 和兼容 tool calling。但它可能缺少 Responses API 的 richer reasoning items、native hosted tools 或 provider-managed state。Novi 当前把这些差异隔离在 model provider adapter 边界内。

## 13. 当前限制

- 真实 research/search、web fetch、browser automation 还未完整实现。
- DeepAgents 的 streaming、checkpoint/resume、subagent mapping 还在后续阶段。
- DeepAgents built-in write/shell tools 默认不直接开放，需要映射到 Novi Tool Runtime 和 policy。
- API key 存储仍是原型方案，需要后续安全 hardening。
- 多人协作、TUI/Web、MCP server、Physical-AI modules 均不属于当前可用核心。
