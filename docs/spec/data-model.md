# Data Model Spec

Status: Draft

This spec defines the minimal durable objects for v0. Field names are draft and should stay easy to map to JSON, YAML, Markdown, and SQLite indexes.

## IDs

Proposal:

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

Exact timestamp and random suffix format is still open.

## SkillSpec

Proposal:

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

Proposal:

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

## RunSpec

Proposal:

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
coding
experiment
simulation
training
robot
evaluation
analysis
audit
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

Proposal:

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
specialist
worker
observer
approver
```

Role rule: do not create an agent only to simulate conversation. Create or activate an agent when it has a distinct purpose, permission boundary, tool set, context scope, execution environment, output schema, or audit requirement.

## RunParticipant

Proposal:

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

Proposal:

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
- `compiled_prompt_ref`

Context packs should be inspectable after the run.

## ToolSpec

Proposal:

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

Proposal:

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
- `policy_result`
- `approval_id`
- `artifact_ids`

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

## ArtifactRecord

Proposal:

Required:

- `id`
- `type`
- `path`
- `run_id`
- `created_at`

Optional:

- `produced_by`
- `hash`
- `metadata`
- `source_urls`
- `mime_type`
- `size_bytes`

## MemoryCandidate

Proposal:

Required:

- `id`
- `type`
- `subject`
- `claim`
- `status`
- `created_at`

Optional:

- `evidence`
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

## EventRecord

Proposal:

Required:

- `id`
- `run_id`
- `type`
- `created_at`

Optional:

- `session_id`
- `actor`
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

## Suggested Project Layout

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

Open decision: whether session directories should contain nested runs, or whether all runs should live under `.novi/runs/` and be referenced by sessions. The current recommendation is independent runs referenced by sessions.
