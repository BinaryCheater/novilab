# Data Model Spec

Status: Draft, v0 direction accepted

This spec defines the minimal durable objects for v0. Field names are draft and should stay easy to map to JSON, YAML, Markdown, and SQLite indexes.

## IDs

Decision:

Use stable prefixed IDs:

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

Use UTC timestamps in compact sortable form plus a short random suffix:

```text
YYYYMMDDTHHMMSSZ_<6-8 chars>
```

The exact random alphabet can be chosen during implementation, but generated IDs must be stable once written.

## ProjectConfig

Decision:

`.novi/novi.yaml` stores local project configuration.

Required:

- `version`
- `workspace`
- `created_at`
- `updated_at`

Optional:

- `active_session_id`
- `model`

Initial model config shape:

```yaml
model:
  provider: openai_chat
  model: deepseek-ai/DeepSeek-V4-Flash
  base_url: https://api.siliconflow.cn/v1
  api_key: local-secret
```

Provider values:

```text
openai_chat
openai_responses
deterministic_local
```

Secret rule: local prototypes may store `api_key` in `.novi/novi.yaml`, but CLI output must redact it. Moving secrets into `.novi/secrets.yaml`, environment variables, or OS keychain remains an open hardening decision.

## SkillSpec

Decision:

Required:

- `id`
- `name`
- `description`
- `path`
- `source`

Optional:

- `version`
- `commands`
- `requires_tools`
- `optional_tools`
- `policies`
- `memory`

Compatibility rule: a plain `SKILL.md` with common frontmatter should load even when Novi-specific metadata is absent.

## SessionSpec

Decision:

Required:

- `id`
- `title`
- `workspace`
- `status`
- `created_at`
- `updated_at`

Optional:

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

Session status values:

```text
active
paused
archived
```

## MessageLogEntry

Decision:

Session message logs are stored as JSONL in `messages.jsonl`.

Required:

- `id`
- `session_id`
- `role`
- `content`
- `created_at`

Optional:

- `run_id`
- `metadata`

Initial provider requests include recent `user` and `assistant` turns as chat messages. Tool messages are archived in run trace files first; whether they become part of long-term session history is a separate context policy decision.

## RunSpec

Decision:

Required:

- `id`
- `session_id`
- `type`
- `objective`
- `status`
- `created_at`
- `updated_at`

Optional:

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

Run types:

```text
research
analysis
audit
```

Reserved later run types:

```text
coding
experiment
simulation
training
robot
evaluation
```

Run status values:

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

Decision:

Required:

- `id`
- `role`
- `description`

Optional:

- `model_profile`
- `default_tool_scope`
- `default_context_scope`
- `default_permission_scope`
- `output_schema`
- `policies`

Initial agent roles:

```text
orchestrator
auditor
```

Reserved later roles:

```text
specialist
worker
observer
approver
```

Role rule: do not create an agent only to simulate conversation. Create or activate an agent when it has a distinct purpose, permission boundary, tool set, context scope, execution environment, output schema, or audit requirement.

## RunParticipant

Decision:

Required:

- `agent_id`
- `role`
- `status`
- `joined_at`

Optional:

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

Run participant status values:

```text
active
waiting
completed
failed
cancelled
```

## ContextPack

Decision:

Required:

- `id`
- `session_id`
- `run_id`
- `agent_id`
- `created_at`
- `model_profile`
- `token_budget`
- `includes`
- `excludes`

Optional:

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

Context packs should be inspectable after the run.

## ToolSpec

Decision:

Required:

- `id`
- `module`
- `description`
- `input_schema`
- `output_schema`
- `side_effect`
- `risk`

Optional:

- `policies`
- `approval_required`
- `timeout_seconds`
- `audit`

Risk values:

```text
read_only
write_local
network
shell
external_side_effect
physical_world
```

## ToolCallRecord

Decision:

Required:

- `id`
- `run_id`
- `tool_id`
- `status`
- `created_at`
- `updated_at`

Optional:

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

Tool call source values:

```text
manual
runner_preflight
deepagents_model
system
```

Tool call status values:

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

Model calls are logged separately from tool calls in `model_calls.jsonl`.

Required:

- `run_id`
- `agent_id`
- `kernel`
- `status`
- `prompt_path`
- `response_path`

Optional:

- `model_provider`
- `model_profile`
- `model_base_url`
- `started_at`
- `completed_at`
- `model_messages_path`
- `system_prompt_path`
- `exported_files`
- `error`

`prompt_path` points to a human-readable archive. `model_messages_path`, when present, points to the actual chat-message sequence passed toward the provider/kernel boundary.

## ArtifactRecord

Decision:

Required:

- `id`
- `type`
- `path`
- `run_id`
- `created_at`

Optional:

- `produced_by`
- `hash`
- `hash_algorithm`
- `metadata`
- `source_urls`
- `mime_type`
- `size_bytes`

Hash rule: artifacts written or copied by Novi should include a content hash. Referenced external artifacts may omit hashes until fetched or captured.

## MemoryCandidate

Decision:

Required:

- `id`
- `type`
- `subject`
- `claim`
- `status`
- `created_at`

Optional:

- `evidence`
- `supersedes`
- `confidence`
- `scope`
- `proposed_by`
- `reviewed_by`
- `reviewed_at`
- `decision_note`

Memory candidate status values:

```text
proposed
accepted
rejected
superseded
```

Memory types:

```text
project
session
episodic
procedural
```

V0 rule: memory candidates are accepted or rejected by the local user through CLI. Auditor output may produce recommendations, but it must not directly commit long-term memory.

## EventRecord

Decision:

Required:

- `id`
- `run_id`
- `type`
- `created_at`

Optional:

- `session_id`
- `actor`
- `agent_id`
- `summary`
- `payload_ref`
- `payload`

Common event types:

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

`actor` can represent a local user, agent, or system process. V0 does not need full multi-human identity, but every decision and tool action should still be attributable.

## ProjectParticipant

Deferred:

Full project participant records are deferred until the collaboration/cowork phase. V0 should not assume team collaboration, but fields such as `actor`, `owner`, `reviewed_by`, and event attribution should remain compatible with future human identities.

Expected later fields:

- `id`
- `display_name`
- `role`
- `status`
- `permissions`
- `created_at`
- `updated_at`

## ApprovalRecord

Proposal:

V0 needs approval state for policy-gated tool calls, but it can start as a simple record referenced by `ToolCallRecord.approval_id`.

Required:

- `id`
- `run_id`
- `tool_call_id`
- `status`
- `risk`
- `requested_by`
- `created_at`
- `updated_at`

Optional:

- `resolved_by`
- `resolved_at`
- `decision_note`

Approval status values:

```text
pending
approved
rejected
expired
```

## CoworkAssignment

Deferred:

Cowork assignments are deferred until Phase 3. They should not be part of the Phase 1 implementation plan except as future-compatible references in comments or open questions.

## Suggested Project Layout

Decision:

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
    artifacts/
    approvals/
```

Runs live independently under `.novi/runs/` and are referenced by sessions through `run_ids`. This keeps runs as independent audit units.
