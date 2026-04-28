# V0 Scope Spec

Status: Draft

## Goal

V0 should prove the core Novi loop without committing to heavy infrastructure:

```text
initialize project
load skills
create/open a session
start an auditable run
record events and tool calls
write artifacts
propose memory candidates
inspect and review results
```

## Must Have

Proposal:

- `novi init` creates a local `.novi/` workspace.
- Built-in skills can be listed and loaded from `skills/`.
- Sessions can be created, listed, opened, and summarized.
- Runs can be started, listed, inspected, completed, and failed.
- Every run has an append-only event log.
- Tool calls are recorded separately from general events.
- Artifacts are first-class records with paths and metadata.
- Memory candidates can be proposed, listed, accepted, and rejected.
- Policies can express at least whether a tool requires approval.
- Runs can record agent participants and their roles, even if v0 only uses orchestrator and auditor roles.
- The CLI can inspect enough state to explain what happened.

## Should Have

Proposal:

- A minimal context pack builder.
- A small tool registry.
- Per-agent tool scope and context scope in run records.
- A stub or local model runner interface.
- Basic schema validation for specs and records.
- A run summary file.
- A session rolling summary file.
- Basic project memory and procedural memory files.

## Initial Built-In Skills

Proposal:

Start with:

- `research.review`;
- `run.audit`;
- `memory.curate`.

Optional after the core loop works:

- `experiment.design`;
- `code.maintain`;
- `dataset.curate`;
- `training.design`;
- `sim.evaluate`;
- `robot.experiment`.

## Initial Modules

Proposal:

Start with:

- `filesystem`;
- `shell_sandbox`;
- `git`;
- `python_exec`;
- `search_stub`.

Network search, browser automation, ROS, simulation, training, IM, MCP, and observability modules should come later unless needed to validate the first loop.

## Out of Scope for V0

Deferred:

- Full OpenClaw-style channel gateway.
- Multi-channel identity system.
- Plugin marketplace or plugin distribution.
- Fleet robotics control.
- Full MCP server.
- Complex multi-agent graph or free-form agent-to-agent chat.
- Full web dashboard.
- Automatic long-term memory without review.
- Unrestricted shell, ROS, or training execution.
- Robot-first architecture.
- Hard dependency on ROS.
- Hard dependency on LangGraph or Temporal.

## V0 Success Criteria

Proposal:

V0 is useful when a user can run:

```bash
novi init
novi skill list
novi session create "physical-ai literature scan"
novi run start research "summarize recent work on physical AI skill learning"
novi run inspect <run_id>
novi memory review
```

and then inspect:

- what session was active;
- which skill was active;
- which agent roles participated;
- what run was created;
- what context was used;
- which tools were visible;
- which tools were called;
- what artifacts were produced;
- what memory was proposed;
- what still needs review.
