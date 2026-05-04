# 数据模型规格

状态：Draft

本规格定义 v0 的最小持久对象。字段名仍是草案，但应容易映射到 JSON、YAML、Markdown 和 SQLite indexes。

## IDs

Proposal:

使用带前缀的稳定 ID：

```text
sess_<timestamp>_<short>
run_<timestamp>_<short>
ctx_<timestamp>_<short>
tc_<timestamp>_<short>
art_<timestamp>_<short>
memcand_<timestamp>_<short>
evt_<timestamp>_<short>
agent_<name_or_short>
```

使用 UTC compact sortable timestamp 加短随机后缀：

```text
YYYYMMDDTHHMMSSZ_<6-8 chars>
```

具体 random alphabet 可在实现时决定，但生成后的 ID 必须稳定。

## ProjectConfig

Decision:

`.novi/novi.yaml` 保存本地 project 配置。

必需字段：

- `version`
- `workspace`
- `created_at`
- `updated_at`

可选字段：

- `active_session_id`
- `model`

初始 model config 形态：

```yaml
model:
  provider: openai_chat
  model: deepseek-ai/DeepSeek-V4-Flash
  base_url: https://api.siliconflow.cn/v1
  api_key: local-secret
```

Provider values：

```text
openai_chat
openai_responses
deterministic_local
```

Secret rule：local prototype 可以把 `api_key` 保存在 `.novi/novi.yaml`，但 CLI 输出必须 redacted。是否迁移到 `.novi/secrets.yaml`、环境变量或 OS keychain，是后续 hardening 决策。

## SkillSpec

Proposal:

必需字段：

- `id`
- `name`
- `description`
- `path`
- `source`

可选字段：

- `version`
- `commands`
- `requires_tools`
- `optional_tools`
- `policies`
- `memory`

兼容规则：即使没有 Novi 专属 metadata，一个带通用 frontmatter 的普通 `SKILL.md` 也应能加载。

## SessionSpec

Proposal:

必需字段：

- `id`
- `title`
- `workspace`
- `status`
- `created_at`
- `updated_at`

可选字段：

- `mode`
- `active_skills`
- `active_agents`
- `model_profile`
- `context_policy`
- `memory_policy`
- `current_run_id`
- `run_ids`
- `summary_path`
- `message_log_path`

Session status values：

```text
active
paused
archived
```

## MessageLogEntry

Decision:

Session message log 以 JSONL 存在 `messages.jsonl`。

必需字段：

- `id`
- `session_id`
- `role`
- `content`
- `created_at`

可选字段：

- `run_id`
- `metadata`

初始 provider request 会把最近的 `user` 和 `assistant` turns 作为 chat messages。Tool messages 先归档在 run trace files 中；是否进入长期 session history，是单独的 context policy 决策。

## RunSpec

Proposal:

必需字段：

- `id`
- `session_id`
- `type`
- `objective`
- `status`
- `created_at`
- `updated_at`

可选字段：

- `completed_at`
- `owner`
- `actor`
- `kernel`
- `skill_refs`
- `module_refs`
- `participants`
- `context_pack_ids`
- `artifact_ids`
- `summary_path`
- `error`

Run types：

```text
research
analysis
audit
```

Reserved later run types：

```text
coding
experiment
simulation
training
robot
evaluation
```

Run status values：

```text
created
planning
running
waiting_approval
completed
failed
cancelled
```

由 task 支撑的 run 可以包含：

- `task_id`
- `workflow_id`
- `workflow_step_id`
- `workflow_step_title`
- `workflow_step_kind`

这些字段把 run 关联到 workflow-backed task，但不让 workflow engine 取代 run record 的 source of truth。

## WorkflowSpec

Decision:

Project-local workflows 以 YAML 存在 `.novi/workflows/`。

必需字段：

- `id`
- `version`
- `status`
- `title`
- `steps`

可选字段：

- `description`
- `inputs`
- `default_agents`
- `success_signals`

Workflow step 字段：

- `id`
- `title`
- `kind`
- `actor`
- `agent_ref`
- `skill_refs`
- `inputs`
- `outputs`
- `instructions`
- `condition`
- `required`
- `review_required`

V0 workflow examples：

```text
document-merge
research-loop
research-iteration
reflection-loop
```

Workflow 演化规则：workflow 可以通过 accepted patch contributions 修改，包括 agent-proposed patches；agent 不能静默覆盖 active workflow files。

## TaskSpec

Decision:

Workflow-backed tasks 存在 `.novi/tasks/<task_id>/`。

必需字段：

- `id`
- `objective`
- `workflow_id`
- `status`
- `created_at`
- `updated_at`

可选字段：

- `session_id`
- `run_ids`
- `current_run_id`
- `workflow_state`
- `summary_path`

`workflow_state` 至少应记录：

- `workflow_id`
- `current_step_id`
- `completed_step_ids`
- `iteration`

## AgentSpec

Proposal:

必需字段：

- `id`
- `role`
- `description`

可选字段：

- `model_profile`
- `default_tool_scope`
- `default_context_scope`
- `default_permission_scope`
- `output_schema`
- `policies`

Initial agent roles：

```text
orchestrator
auditor
```

Reserved later roles：

```text
specialist
worker
observer
approver
```

Role rule：不要只为了模拟对话而创建 agent。只有当 purpose、permission boundary、tool set、context scope、execution environment、output schema 或 audit requirement 存在真实区别时，才创建或激活 agent。

## RunParticipant

Proposal:

必需字段：

- `agent_id`
- `role`
- `status`
- `joined_at`

可选字段：

- `left_at`
- `model_profile`
- `skill_refs`
- `tool_scope`
- `context_scope`
- `permission_scope`
- `approval_scope`
- `produced_event_ids`
- `produced_artifact_ids`
- `produced_memory_candidate_ids`

Run participant status values：

```text
active
waiting
completed
failed
cancelled
```

## ContextPack

Proposal:

必需字段：

- `id`
- `session_id`
- `run_id`
- `agent_id`
- `created_at`
- `model_profile`
- `token_budget`
- `includes`
- `excludes`

可选字段：

- `skill_refs`
- `memory_refs`
- `artifact_refs`
- `tool_refs`
- `permission_refs`
- `messages_ref`
- `system_prompt_ref`
- `model_messages_ref`
- `prompt_parts_ref`
- `compiled_prompt_ref`

Context packs 应在 run 结束后仍可检查。

## ToolSpec

Proposal:

必需字段：

- `id`
- `module`
- `description`
- `input_schema`
- `output_schema`
- `side_effect`
- `risk`

可选字段：

- `policies`
- `approval_required`
- `timeout_seconds`
- `audit`

Risk values：

```text
read_only
write_local
network
shell
external_side_effect
physical_world
```

## ToolCallRecord

Proposal:

必需字段：

- `id`
- `run_id`
- `tool_id`
- `status`
- `created_at`
- `updated_at`

可选字段：

- `agent_id`
- `args_ref`
- `result_ref`
- `error`
- `latency_ms`
- `risk`
- `source`
- `executor`
- `policy_result`
- `block_reason`
- `approval_id`
- `artifact_ids`

Tool call source values：

```text
manual
runner_preflight
deepagents_model
system
```

Tool call status values：

```text
requested
blocked
waiting_approval
approved
running
success
error
cancelled
```

## ModelCallRecord

Decision:

Model calls 与 tool calls 分开，写入 `model_calls.jsonl`。

必需字段：

- `run_id`
- `agent_id`
- `kernel`
- `status`
- `prompt_path`
- `response_path`

可选字段：

- `model_provider`
- `model_profile`
- `model_base_url`
- `started_at`
- `completed_at`
- `model_messages_path`
- `system_prompt_path`
- `exported_files`
- `error`

`prompt_path` 指向人类可读 archive。存在 `model_messages_path` 时，它指向真正传到 provider/kernel 边界的 chat-message sequence。

## ArtifactRecord

Proposal:

必需字段：

- `id`
- `type`
- `path`
- `run_id`
- `created_at`

可选字段：

- `produced_by`
- `hash`
- `hash_algorithm`
- `metadata`
- `source_urls`
- `mime_type`
- `size_bytes`

Hash rule：Novi 写入或复制的 artifacts 应包含 content hash。引用但尚未 fetch/capture 的外部 artifact 可以暂时没有 hash。

Source 和 result artifacts 应保持灵活。PDF、论文、网页、datasets、plots、videos、logs、configs、scripts 和 result packets 都可以是 artifacts。优先保留原始文件，并附加 generated extraction 或 analysis artifacts，而不是强行塞进重 schema。

## ResultPacket

Decision:

实验结果以轻量 Markdown packets 进入系统，而不是 rigid database rows。

建议可选 frontmatter：

```yaml
type: experiment_result
title:
status:
topic:
artifacts:
tags:
```

建议正文部分：

```text
What Was Tried
Observations
Interpretation
Next Action
```

Packet 可以通过 artifact path 链接 raw data、plots、videos、logs、configs 或 scripts。后续 LLM workflows 可以在下一次 run 中从自然语言抽取 claims、observations、interpretations 和 prior updates。

## MemoryCandidate

Proposal:

必需字段：

- `id`
- `type`
- `subject`
- `claim`
- `status`
- `created_at`

可选字段：

- `evidence`
- `supersedes`
- `confidence`
- `scope`
- `proposed_by`
- `reviewed_by`
- `reviewed_at`
- `decision_note`

Memory candidate status values：

```text
proposed
accepted
rejected
superseded
```

Memory types：

```text
project
session
episodic
procedural
```

V0 rule：memory candidates 由本地用户通过 CLI accept/reject。Auditor output 可以提出 recommendations，但不能直接 commit long-term memory。

Physical-prior candidates 可以先作为 `physical-priors.md` 这类 Markdown artifacts 存在。只有当多轮真实任务证明 Markdown review 不足时，才需要单独的结构化 record。

## ContributionRecord

Decision:

Reviewable changes 用 contributions 表示。

初始 contribution types：

```text
knowledge_import
document_patch
```

`document_patch` 可指向：

```text
.novi/knowledge/
.novi/workflows/
.novi/skills/
```

这就是初始 workflow/skill self-modification 边界。Agent-proposed workflow 或 skill changes 必须先变成 pending contributions，通过 checks/review 后才能应用。

## EventRecord

Proposal:

必需字段：

- `id`
- `run_id`
- `type`
- `created_at`

可选字段：

- `session_id`
- `actor`
- `agent_id`
- `summary`
- `payload_ref`
- `payload`

Common event types：

```text
RunCreated
SkillActivated
ContextPackBuilt
ToolRequested
ToolPolicyChecked
ToolApproved
ToolRejected
ToolExecuted
ArtifactCreated
MemoryCandidateProposed
AuditorReviewed
RunCompleted
RunFailed
RunSummarized
```

`actor` 可以表示 local user、agent 或 system process。V0 不需要完整多人 identity，但每个 decision 和 tool action 都应可归因。

## ProjectParticipant

Deferred:

完整 project participant record 延后到 collaboration/cowork phase。V0 不假设 team collaboration，但 `actor`、`owner`、`reviewed_by` 和 event attribution 等字段应兼容未来 human identities。

后续预期字段：

- `id`
- `display_name`
- `role`
- `status`
- `permissions`
- `created_at`
- `updated_at`

## ApprovalRecord

Proposal:

V0 需要 policy-gated tool calls 的 approval state，但可以从一个由 `ToolCallRecord.approval_id` 引用的简单 record 开始。

必需字段：

- `id`
- `run_id`
- `tool_call_id`
- `status`
- `risk`
- `requested_by`
- `created_at`
- `updated_at`

可选字段：

- `resolved_by`
- `resolved_at`
- `decision_note`

Approval status values：

```text
pending
approved
rejected
expired
```

## CoworkAssignment

Deferred:

Cowork assignments 延后到 Phase 3。除了 comments 或 open questions 中的 future-compatible references，不应进入 Phase 1 implementation plan。

## 建议项目目录

Proposal:

```text
project-root/
  .novi/
    novi.yaml
    specs/
      project.yaml
      policies.yaml
    sessions/
      sess_001/
        session.yaml
        summary.md
        messages.jsonl
    runs/
      run_001/
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
        artifacts/
        summary.md
    memory/
      project.md
      procedural.jsonl
      episodic.jsonl
      candidates/
    workflows/
      research-loop.yaml
      research-iteration.yaml
      document-merge.yaml
    skills/
    tasks/
    artifacts/
      imports/
    contributions/
    approvals/
```

Runs 独立存储在 `.novi/runs/`，sessions 通过 `run_ids` 引用它们。这让 run 作为独立 audit unit 保持清晰。
