# Novi Lab Repo Bootstrap Summary

## 0. Project Name

**Project name:** Novi Lab  
**CLI name:** `novi`  
**Short name:** Novi

### One-line positioning

> Novi Lab is a skill-first, session-aware control plane for autonomous research, coding, training, and physical-AI experiments.

### Why not Axiom

Axiom is already used by existing AI/agent-related products and libraries, so continuing with that name risks confusion. Novi is shorter, less domain-constrained, and works well as a CLI/project name.

---

## 1. Core Direction

Novi Lab is **not** primarily a multi-agent framework, robot runtime, ROS wrapper, OpenClaw clone, or Codex replacement.

It is a **skill-first autonomous workbench / control plane** for:

- problem exploration;
- scientific research;
- literature review;
- coding and repo maintenance;
- experiment design;
- simulation;
- robot experiment/control through adapters;
- dataset management;
- model training;
- evaluation;
- memory and knowledge accumulation;
- audit, replay, and observability.

The key design is:

```text
Novi Core
  = sessions + skills + tools + runs + memory + artifacts + policies + context

External systems
  = modules/adapters/plugins
```

ROS, Isaac Sim, LeRobot, Codex, Claude Code, MCP servers, SearXNG, Crawl4AI, Rerun, Langfuse, Temporal, LangGraph, and IM channels are all optional modules/adapters, not the foundation of the platform.

---

## 2. Design Principles

### 2.1 Skill-first

Skills are first-class. A skill is a reusable workflow package, not just a prompt.

A skill may include:

- `SKILL.md`;
- instructions;
- examples;
- schemas;
- references;
- scripts;
- optional assets;
- optional policies;
- optional evals;
- optional hooks.

Novi should stay compatible with the common Agent Skills / `SKILL.md` convention. The skill standard should remain permissive: Novi may add optional metadata, but should not require skill authors to follow an overly strict custom format.

### 2.2 Run-centric

A run is the unit of execution and audit.

Sessions are long-lived work contexts. Runs are concrete executions inside a session.

Example:

```text
Session: SO-100 pick-place exploration
  Run 1: review papers
  Run 2: write experiment spec
  Run 3: run simulation
  Run 4: launch training
  Run 5: analyze failure
```

### 2.3 Module/plugin-ready, but not plugin-heavy at v0

V0 should support local modules and skills. Full plugin install/distribution and MCP integration can come later.

### 2.4 Tool use stays tool use

No need to rename tool use to “capability governance.”

Instead, keep simple names:

- Tool Registry
- Tool Runtime
- Tool Policy
- Tool Audit

The additional complexity is justified only around:

- tool schema validation;
- permissions;
- side-effect/risk level;
- preflight checks;
- approval gates;
- audit logs;
- artifact capture;
- memory evidence.

### 2.5 Control-plane-native

Novi should feel more like Codex / Claude Code in product shape:

- chat/control surface;
- sessions;
- visible runs;
- approval queue;
- inspectable tool calls;
- skill management;
- memory review;
- artifacts;
- audit/replay.

But Novi is not a coding agent itself. It may call Codex/Claude Code as external workers.

### 2.6 ROS is not the base layer

ROS should be a module/adapter.

Novi’s architecture should work equally for:

- research runs;
- coding runs;
- training runs;
- simulation runs;
- robot runs;
- evaluation runs.

Robot runtime cannot be assumed to be the bottom layer.

### 2.7 Avoid premature multi-agent complexity

Start with:

- Orchestrator Agent;
- Auditor Agent;
- skills as reusable workflows;
- deterministic services for tool runtime, session, context, memory, artifact, policy, run ledger.

Do not start with many free-chatting agents.

---

## 3. Core Abstractions

The stable core objects should be:

```text
SkillSpec
ToolSpec
ModuleSpec
SessionSpec
RunSpec
ContextPack
MemoryRecord
ArtifactRecord
PolicyRule
ChannelMessage
EventRecord
```

These should be designed early because they allow the rest of the system to be refactored later without losing continuity.

---

## 4. Core Architecture

### 4.1 Novi Core

```text
Novi Core
  ├─ Chat / Control Plane
  ├─ Session Manager
  ├─ Context Manager
  ├─ Skill Runtime
  ├─ Tool Registry
  ├─ Tool Runtime
  ├─ Policy Gate
  ├─ Run Ledger
  ├─ Memory Store
  ├─ Artifact Store
  ├─ Module Runtime
  └─ Lightweight Channel Adapter API
```

### 4.2 Modules

Modules provide tools, observations, artifacts, resources, and policies.

Example modules:

```text
Built-in or early modules:
  search
  browser
  filesystem
  shell_sandbox
  git
  python/notebook
  code_worker

Stub or later modules:
  ros
  sim
  training
  dataset
  rerun
  langfuse/phoenix
  mcp_client
  im_channel
```

### 4.3 Agents

V0 agents:

```text
Orchestrator Agent
  - handles dialogue
  - selects skills
  - creates runs
  - plans steps
  - calls tools through Tool Runtime
  - updates session summary
  - proposes memory candidates

Auditor Agent
  - checks tool calls against policy
  - reviews memory candidates
  - checks run completeness
  - flags missing evidence/artifacts
  - reviews spec drift
```

Specialist agents can be added later only when there is a real boundary:

- different permissions;
- different model;
- different context window;
- different output schema;
- different execution environment;
- different safety/audit requirements.

Before that, prefer skills over additional agents.

---

## 5. Skill Design

### 5.1 Skill as package

A skill should be a directory:

```text
skills/
  paper-review/
    SKILL.md
    scripts/
    references/
    assets/
    schemas/
    examples/
    evals/
```

The minimal skill should remain compatible with common skill standards:

```markdown
---
name: paper-review
description: Review papers, extract claims, build evidence tables, and propose research directions.
---

# Paper Review Skill

Instructions go here.
```

### 5.2 Optional Novi metadata

Novi can optionally read additional metadata from `SKILL.md` frontmatter or sidecar files.

Optional fields:

```yaml
name: robot-experiment
description: Design, run, and audit robot experiments.
version: 0.1.0
commands:
  - /robot-experiment
  - /design-experiment
requires_tools:
  - sim.run
  - artifact.write
optional_tools:
  - ros.action
  - rerun.log
policies:
  - require_sim_before_real
  - require_approval_for_real_robot
memory:
  writes:
    - episodic
    - procedural
  requires_evidence: true
```

But Novi should not reject skills just because they lack this metadata.

### 5.3 Built-in v0 skills

Recommended built-in skills:

```text
research.review
  literature review, source extraction, evidence table, claim graph

experiment.design
  problem framing, hypotheses, experiment plans, metrics

code.maintain
  repo inspection, patch proposal, test execution, refactor planning

run.audit
  inspect run logs, tool calls, artifacts, memory writes, policy violations

memory.curate
  summarize sessions, propose memory candidates, detect stale/unsupported memory
```

Physical-AI-oriented skills can start as optional/stub:

```text
robot.experiment
training.design
sim.evaluate
dataset.curate
```

---

## 6. Tool Runtime

### 6.1 ToolSpec

A tool should have a clear spec:

```yaml
id: training.launch
module: training
description: Launch a training job.
input_schema: TrainingLaunchInput
output_schema: TrainingLaunchResult
side_effect: true
risk: medium
policies:
  - require_dataset_hash
  - require_budget_limit
  - no_overwrite_best_checkpoint
audit:
  record_args: true
  record_result: true
  record_artifacts: true
```

For ROS-like modules:

```yaml
id: ros.action
module: ros
description: Call a ROS action.
input_schema: RosActionInput
output_schema: RosActionResult
side_effect: true
risk: high
policies:
  - require_allowlist
  - require_preflight
  - require_approval_if_real_robot
audit:
  record_args: true
  record_result: true
  record_artifacts: true
```

### 6.2 Tool lifecycle

Every tool call should go through:

```text
request
→ schema validation
→ permission check
→ policy/risk check
→ optional preflight
→ optional approval
→ execution
→ timeout/error handling
→ result normalization
→ artifact capture
→ event logging
```

### 6.3 Tool visibility vs execution

Important rule:

```text
Visible ≠ callable
Callable ≠ executable
Executable ≠ automatic
Automatic ≠ memory-writeable
```

The agent may see available tools, but execution must still go through Tool Runtime and Policy Gate.

---

## 7. Session Management

### 7.1 Session definition

A session is a long-lived working context.

```yaml
session:
  id: sess_20260428_001
  title: SO-100 pick-place exploration
  workspace: ./projects/so100
  mode: interactive
  active_skills:
    - research.review
    - experiment.design
  context_policy: project_default
  memory_policy: evidence_required
  created_at: ...
  updated_at: ...
```

### 7.2 Session contains

```text
messages
active skills
selected model/profile
workspace
context policy
runs
artifacts
memory candidates
approval state
channel bindings
session summary
```

### 7.3 Session vs Run

```text
Session = ongoing conversation/work context
Run     = one auditable execution
```

Do not treat a session as only a chat history.

---

## 8. Context Management

### 8.1 Context layers

Context should be explicitly compiled, not blindly appended.

Recommended layers:

```text
Global context
  platform rules, user preferences, safety defaults

Project context
  project spec, repo summary, relevant documents, active goals

Session context
  session summary, decisions, open questions, active skills

Run context
  current run objective, plan, state, recent tool results

Skill context
  skill instructions, examples, schemas, policies, resources

Retrieved memory
  relevant episodic/procedural/project memory
```

### 8.2 ContextPack

Each model call should receive a generated `ContextPack`.

```yaml
context_pack:
  id: ctx_001
  session_id: sess_001
  run_id: run_001
  model_profile: default
  token_budget: 48000
  includes:
    - system_policy
    - active_skill_instructions
    - session_summary
    - current_run_state
    - relevant_memory
    - selected_artifacts
    - available_tools
  excludes:
    - raw_old_messages
    - large_logs
    - unverified_memory
```

### 8.3 Rolling summaries

Each session should maintain an editable rolling summary:

```text
Objective
Current state
Confirmed facts
Important decisions
Open questions
Recent runs
Important artifacts
Known failures
Next suggested actions
```

### 8.4 Raw history policy

Do not always send full message history.

Prefer:

```text
recent messages
+ session summary
+ active skill instructions
+ current run state
+ retrieved memory
+ selected artifacts
```

---

## 9. Memory Management

### 9.1 Memory types

Start with four memory types:

```text
Project memory
  durable project facts, architecture decisions, long-term goals

Session memory
  rolling summary and session-level decisions

Episodic memory
  summaries of runs and their outcomes

Procedural memory
  reusable lessons about how to perform tasks/skills
```

Later optional types:

```text
Semantic memory
Spatial/world memory
Evaluation memory
Dataset/model lineage memory
```

### 9.2 Evidence-based memory writes

Long-term memory should not be written directly by the main agent.

Flow:

```text
agent proposes memory candidate
→ auditor/checker validates evidence
→ user or policy accepts
→ memory committed
```

Example:

```yaml
memory_candidate:
  type: procedural
  subject: skill.robot.pick_place
  claim: In sim tabletop_v1, top-down grasp failed when cup pose confidence < 0.75.
  evidence:
    runs:
      - run_001
      - run_004
  confidence: medium
  scope: sim_only
```

### 9.3 Memory rules

```text
Do not store secrets.
Do not store unverified assumptions as facts.
Do not store raw logs as memory.
Do not let memory overwrite evidence.
Use scope and confidence.
Keep artifact references instead of duplicating large content.
```

---

## 10. Run Ledger

### 10.1 RunSpec

A run records a concrete execution.

```yaml
run:
  id: run_20260428_001
  type: research.run
  objective: Find recent VLA papers and extract open problems.
  session_id: sess_001
  skill_refs:
    - research.review
  modules:
    - search
    - browser
  status: completed
  created_at: ...
  completed_at: ...
```

Other run types:

```text
research.run
coding.run
experiment.run
simulation.run
training.run
robot.run
evaluation.run
analysis.run
audit.run
```

### 10.2 Event log

Every run should produce append-only events.

Example events:

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
RunSummarized
```

### 10.3 Tool call log

Tool calls should be queryable independently.

```yaml
tool_call:
  id: tc_001
  run_id: run_001
  tool_id: search.query
  args_ref: artifacts/tool_args/tc_001.json
  result_ref: artifacts/tool_results/tc_001.json
  status: success
  latency_ms: 1200
  risk: low
  policy_result: allowed
```

---

## 11. Artifact Store

Artifacts are first-class.

Examples:

```text
search results
web pages
PDFs
notes
code patches
logs
metrics
checkpoints
configs
datasets
rosbags
Rerun recordings
screenshots
videos
plots
reports
```

Each artifact should record:

```yaml
artifact:
  id: art_001
  type: evidence_table
  path: artifacts/evidence_table.json
  run_id: run_001
  produced_by: tool.paper.extract
  hash: ...
  created_at: ...
  metadata:
    source_urls: []
```

Rule:

```text
Memory should point to artifacts instead of embedding large or unstable content.
```

---

## 12. Module System

### 12.1 ModuleSpec

Each module should provide:

```text
manifest
tools
resources
observations
artifacts
policies
optional hooks
```

Example:

```yaml
module:
  id: search
  type: knowledge_adapter
  tools:
    - search.query
    - web.fetch
  observations:
    - SourceList
    - WebPageSnapshot
  artifacts:
    - search_result
    - fetched_page
  policies:
    - citation_required_for_claims
```

ROS module example:

```yaml
module:
  id: ros
  type: execution_adapter
  tools:
    - ros.list
    - ros.read
    - ros.publish
    - ros.action
  observations:
    - RosGraphObservation
    - TopicSnapshot
    - RobotState
  artifacts:
    - rosbag
    - rviz_snapshot
  policies:
    - no_unallowlisted_publish
    - no_param_write_by_default
    - require_estop_available
```

Training module example:

```yaml
module:
  id: training
  type: experiment_adapter
  tools:
    - training.launch
    - training.stop
    - training.status
    - training.compare
  observations:
    - TrainingProgress
    - MetricSeries
    - ResourceUsage
  artifacts:
    - checkpoint
    - tensorboard_log
    - config
  policies:
    - require_dataset_hash
    - require_budget_limit
    - no_overwrite_best_checkpoint
```

---

## 13. ROSClaw Lessons to Reference

ROSClaw should be treated as inspiration, not as the base design.

Useful ideas to borrow:

```text
executive layer between agent and ROS
dynamic capability/tool discovery
observation normalization
before-tool-call validation
structured audit logging
model-agnostic interface
distinguishing visibility from authorization
pre-execution safety checks
digital twin / sim preflight
data accumulation from runs
```

Things not to copy directly:

```text
ROS as bottom layer
fixed robot-centric stack
fixed sense-think-act loop
free-form multi-agent chat
prompt-only safety
robot-only memory model
```

For Novi, ROS is just one module.

---

## 14. IM / Chat Channel Integration

### 14.1 Lightweight Channel Adapter

Do not build an OpenClaw-scale gateway at v0.

Instead:

```text
Telegram / Discord / Slack / Webhook
  ↓
Channel Adapter
  ↓
Session Router
  ↓
Novi Core
```

### 14.2 Channel adapter responsibilities

```text
auth / allowlist
message normalization
session routing
reply delivery
attachment ingestion
basic command parsing
rate limit
```

### 14.3 ChannelMessage

```yaml
message_event:
  channel: telegram
  sender_id: ...
  text: ...
  attachments: []
  session_hint: ...
  command: optional
```

### 14.4 Safety rules for IM

```text
DM can default to a main session.
Group chats require mention or slash command.
High-risk tools cannot be triggered directly from IM.
IM can inspect, approve, summarize, or enqueue.
IM should not directly execute robot actions, shell commands, or training jobs by default.
```

Example commands:

```text
/novi ask ...
/novi status
/novi run research ...
/novi approve run_123
/novi inspect run_123
```

---

## 15. MCP and Plugin Roadmap

### 15.1 V0: native local modules and skills

```text
skills/...
modules/...
```

### 15.2 V1: plugin installer

Plugin = installable skill/module package.

```bash
novi plugin install ./plugins/ros
novi plugin install github:user/novi-lerobot
```

A plugin should declare:

```text
manifest
permissions
tools
resources
hooks
version
```

### 15.3 V2: MCP client

Novi connects to external MCP servers.

Examples:

```text
filesystem MCP
github MCP
postgres MCP
browser MCP
lab-specific MCP
```

### 15.4 V3: MCP server

Novi exposes itself over MCP.

Resources:

```text
novi://sessions
novi://runs
novi://memory
novi://artifacts
novi://skills
```

Tools:

```text
novi.run.start
novi.skill.invoke
novi.memory.search
novi.artifact.read
novi.session.open
```

Prompts:

```text
novi.audit_run
novi.design_experiment
novi.review_paper
novi.summarize_session
```

---

## 16. Control Plane UX

### 16.1 CLI

Initial CLI commands:

```bash
novi
novi chat
novi run <type> <objective>
novi session list
novi session open <id>
novi skill list
novi skill install ./skills/paper-review
novi tool list
novi tool inspect <tool_id>
novi run inspect <run_id>
novi memory search "grasp failure"
novi memory review
novi connect telegram
```

### 16.2 TUI

TUI panes:

```text
current session
active skills
current run
pending tool calls
approval queue
run timeline
memory candidates
artifact list
```

### 16.3 Web dashboard

Minimal pages:

```text
Sessions
Runs
Skills
Tools
Memory
Artifacts
Approvals
Traces
Settings
```

Important questions the UI should answer:

```text
What session am I in?
Which skill is active?
What context was sent to the model?
Which tools were visible?
Which tools were called?
Which calls were blocked or approved?
What artifacts were produced?
What memory was proposed/written?
Why did the agent make this decision?
```

---

## 17. Repo Layout

Recommended initial local-first layout:

```text
novi/
  README.md
  pyproject.toml
  package.json                  # optional if web UI is included

  src/novi/
    __init__.py

    core/
      sessions.py
      context.py
      skills.py
      tools.py
      runs.py
      memory.py
      artifacts.py
      policies.py
      events.py
      models.py

    agents/
      orchestrator.py
      auditor.py
      prompts/

    modules/
      search/
      browser/
      filesystem/
      shell_sandbox/
      git/
      python_exec/
      ros_stub/
      training_stub/
      sim_stub/

    cli/
      main.py
      chat.py
      run.py
      skills.py
      sessions.py
      memory.py

    channels/
      base.py
      telegram.py
      discord.py
      webhook.py

    storage/
      sqlite.py
      fs.py
      migrations/

    schemas/
      skill.schema.json
      tool.schema.json
      module.schema.json
      session.schema.json
      run.schema.json
      memory.schema.json
      artifact.schema.json
      policy.schema.json

  skills/
    research.review/
      SKILL.md
      examples/
      schemas/
    experiment.design/
      SKILL.md
    code.maintain/
      SKILL.md
    run.audit/
      SKILL.md
    memory.curate/
      SKILL.md

  examples/
    projects/
      physical_ai_lab/
        .novi/

  docs/
    architecture.md
    skills.md
    sessions.md
    context.md
    tools.md
    memory.md
    modules.md
    mcp-roadmap.md
```

Project workspace layout:

```text
project-root/
  .novi/
    novi.yaml

    specs/
      project.yaml
      policies.yaml

    skills/
      paper-review/
        SKILL.md
        scripts/
        references/
        assets/

    modules/
      search.yaml
      ros.yaml
      training.yaml

    sessions/
      sess_001/
        session.yaml
        summary.md
        messages.jsonl
        context_packs/
        runs/

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
      ...
```

---

## 18. Storage Strategy

### 18.1 V0

Use local-first storage:

```text
filesystem for skills, sessions, runs, artifacts
SQLite for indexes and queryable metadata
JSONL for event logs and tool calls
Markdown for editable summaries and project memory
```

### 18.2 Later

Add:

```text
Postgres for multi-project/multi-user
pgvector or Qdrant for retrieval
object storage for large artifacts
OpenTelemetry + Langfuse/Phoenix for LLM traces
Rerun for robotics/multimodal visual logs
```

---

## 19. Suggested V0 Build Plan

### Milestone 1: local project skeleton

Implement:

```text
novi init
.novi directory
Skill loader
Session loader
Run ledger
Event log
Artifact writer
```

### Milestone 2: chat + session

Implement:

```text
novi chat
SessionManager
message log
rolling summary placeholder
ContextPack builder
```

### Milestone 3: skill runtime

Implement:

```text
load SKILL.md
list skills
activate skill in session
inject skill instructions into ContextPack
support skill commands
```

### Milestone 4: tool runtime

Implement:

```text
ToolRegistry
ToolSpec
schema validation
tool execution
tool_call log
basic policies
approval required flag
```

Initial tools:

```text
filesystem.read
filesystem.write_draft
search.query
web.fetch
shell.run_sandboxed
git.diff
python.run
```

### Milestone 5: run-centric execution

Implement:

```text
novi run research "..."
run.yaml
events.jsonl
tool_calls.jsonl
artifacts
summary.md
```

### Milestone 6: memory candidates

Implement:

```text
memory_candidate proposal
memory review CLI
commit/reject memory
project/session/episodic/procedural memory files
```

### Milestone 7: auditor

Implement:

```text
audit run
audit memory candidate
audit missing artifacts
audit risky tool calls
```

### Milestone 8: lightweight channel adapter

Implement one first:

```text
Telegram or webhook
```

Only allow:

```text
ask
status
inspect
approve
simple run enqueue
```

---

## 20. What Not to Build Yet

Do not build in v0:

```text
full OpenClaw-style gateway
multi-channel identity system
plugin marketplace
fleet robotics control
full MCP server
complex multi-agent graph
full web dashboard
automatic long-term memory without review
unrestricted shell/ROS/tool access
robot-first architecture
hard dependency on ROS
hard dependency on LangGraph/Temporal
```

---

## 21. Relationship to Codex / Claude Code

Codex and Claude Code are excellent coding agents/control surfaces, but Novi’s scope is broader.

Use them as:

```text
external coding workers
repo maintenance tools
implementation assistants
code review/refactor helpers
```

Novi owns:

```text
sessions
skills
runs
research context
experiment specs
tool registry
audit logs
memory
artifacts
training/robot/sim integrations
IM routing
cross-tool control plane
```

Example:

```text
Novi run: implement ROS module
  → creates coding.run
  → calls Codex or Claude Code as worker
  → captures diff, tests, logs
  → auditor reviews result
  → memory candidate proposed
```

Reason to build Novi instead of only using Codex/Claude Code:

```text
Codex/Claude Code optimize coding tasks.
Novi coordinates research, experiments, training, robots, memory, sessions, artifacts, and audit across tools.
```

---

## 22. Final Architecture Sentence

Use this as the repo README thesis:

> Novi Lab is a skill-first, session-aware control plane for autonomous research, coding, training, and physical-AI experiments. It organizes work around skills, sessions, runs, tools, memory, artifacts, and policies, while keeping external systems such as ROS, simulators, model trainers, Codex, Claude Code, MCP servers, and chat channels as pluggable modules.

---

## 23. Immediate Repo Checklist

Create these first:

```text
README.md
/docs/architecture.md
/docs/skills.md
/docs/sessions.md
/docs/context.md
/docs/tools.md
/docs/memory.md
/docs/runs.md
/src/novi/core/models.py
/src/novi/core/skills.py
/src/novi/core/sessions.py
/src/novi/core/context.py
/src/novi/core/tools.py
/src/novi/core/runs.py
/src/novi/core/memory.py
/src/novi/cli/main.py
/skills/research.review/SKILL.md
/skills/experiment.design/SKILL.md
/skills/run.audit/SKILL.md
```

First working demo:

```text
novi init
novi skill list
novi chat
novi run research "summarize recent work on physical AI skill learning"
novi run inspect <run_id>
novi memory review
```

That is enough to validate the core loop before adding ROS, training, simulation, MCP, or IM adapters.

