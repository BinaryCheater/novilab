# YAML 配置

Novi 把项目状态和配置保存为可读 YAML。用户通常通过 CLI 修改这些文件，但理解它们有助于排错和设计 workflow。

## `.novi/novi.yaml`

项目级配置。典型字段：

```yaml
version: 1
workspace: /path/to/project
active_session_id: sess_...
model:
  provider: openai_chat
  model: deepseek-ai/DeepSeek-V4-Flash
  base_url: https://api.siliconflow.cn/v1
  api_key: ...
```

LiteLLM proxy 配置示例：

```yaml
model:
  provider: litellm_proxy
  model: research-primary
  base_url: http://localhost:4000/v1
  api_key: os.environ/LITELLM_PROXY_API_KEY
  api_shape: responses
  auto_start: true
```

对应 gateway 配置位于：

```text
.novi/litellm/config.yaml
```

修改方式：

```bash
novi configure model siliconflow --model "..." --api-key "..."
novi litellm init --model-name research-primary --upstream-model openai/gpt-4.1-mini --upstream-api-key-env OPENAI_API_KEY
novi doctor model
```

## `.novi/agents/*.yaml`

Agent profile 表达权限、工具、skills、模型绑定和执行边界。

常见字段：

```yaml
id: agent_orchestrator
role: orchestrator
authority_level: executor
model_profile: default
skill_refs:
  - research.review
tool_scope:
  - search_stub.query
  - filesystem.read
permission_scope:
  - read_project
kernel_binding_hints:
  deepagents:
    binding: deepagents_subagent
```

查看：

```bash
novi agent show agent_orchestrator
```

## `.novi/workflows/*.yaml`

WorkflowSpec 描述 task 如何推进。

简化示例：

```yaml
id: research-loop
version: 1
status: active
steps:
  - id: plan
    title: Plan task
    kind: produce_artifact
    actor: agent
  - id: work
    title: Execute research step
    kind: agent_run
    actor: agent
  - id: review
    title: Review outputs
    kind: review_gate
    actor: human
  - id: continue
    title: Continue or close task
    kind: decision
    actor: human_or_agent
```

查看：

```bash
novi workflow show research-loop
```

## `.novi/tasks/task_.../task.yaml`

Task record 保存目标和 workflow 进度。

```yaml
id: task_...
objective: 整理接触先验相关知识
workflow_id: research-loop
status: active
session_id: sess_...
run_ids:
  - run_...
current_run_id: run_...
workflow_state:
  workflow_id: research-loop
  current_step_id: work
  completed_step_ids:
    - plan
  iteration: 1
```

查看：

```bash
novi task inspect task_...
```

## `.novi/runs/run_.../run.yaml`

Run record 是一次执行的索引。

```yaml
id: run_...
session_id: sess_...
type: research
objective: ...
kernel: deepagents
task_id: task_...
workflow_id: research-loop
workflow_step_id: work
artifact_ids:
  - art_...
```

Run 目录还包含 JSONL 日志、prompt archive、response、summary 和 artifacts。

## 手动编辑原则

- 可以阅读 YAML 排错。
- 尽量通过 CLI 修改配置和状态。
- 不要手动把 pending contribution 改成 accepted。
- 不要把 agent 输出直接复制进 accepted state，优先走 contribution/review。
- 改 workflow/agent/skill 前，先确认这是项目配置修改，而不是一次 run 的临时需求。
