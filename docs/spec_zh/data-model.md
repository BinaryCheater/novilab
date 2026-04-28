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

具体 timestamp 和 random suffix 格式仍待确认。

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
coding
experiment
simulation
training
robot
evaluation
analysis
audit
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
- `policy_result`
- `approval_id`
- `artifact_ids`

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
- `metadata`
- `source_urls`
- `mime_type`
- `size_bytes`

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
        artifacts/
        summary.md
    memory/
      project.md
      procedural.jsonl
      episodic.jsonl
      candidates/
    artifacts/
```

Open decision：session directories 是否应嵌套 runs，还是所有 runs 都放在 `.novi/runs/` 并由 sessions 引用。当前建议是 runs 独立存储，sessions 引用 run ids。
