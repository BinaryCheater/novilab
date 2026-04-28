# Novi Lab Technical Implementation & Open-Source Tooling Reference

This document complements the prior Novi Lab architecture notes. It does not redefine the product philosophy. It focuses on implementation choices, reusable open-source components, integration boundaries, and near-term build strategy.

---

## 1. Implementation Assumption

Novi Lab should be built as a **platform core with replaceable agent kernels**.

The platform core owns:

- skill registry;
- session records;
- context pack generation;
- run ledger;
- tool registry and tool policy;
- artifact indexing;
- memory candidates and committed memory;
- control plane state;
- channel routing;
- module/plugin registration.

External frameworks provide execution capability:

- DeepAgents / LangGraph for research and long-running tasks;
- Pi Agent Core for local coding-agent-like interaction;
- Codex / Claude Code / OpenHands as external coding workers;
- MCP servers as external tool/resource providers;
- ROS / simulators / training frameworks as modules.

Do not let any one agent framework become the source of truth for sessions, memory, artifacts, or tool policy.

---

## 2. Recommended V0 Stack

### 2.1 Core language

**Recommended:** Python-first core.

Reason:

- better fit for research, ML, robotics, simulation, and training tooling;
- DeepAgents, LangGraph, EvoScientist-like workflows, ROS, LeRobot, and scientific Python tools are easier to integrate;
- CLI/TUI can be built quickly with Typer/Rich/Textual.

TypeScript can be added later for a web control plane or Pi kernel adapter.

### 2.2 Agent kernel

**Recommended V0 kernel:** DeepAgents + LangGraph.

Use DeepAgents for:

- research runs;
- experiment design;
- analysis runs;
- long-running multi-step workflows;
- subagent delegation;
- filesystem-based working memory;
- LangGraph checkpoint support.

Keep Pi as a second spike:

- interactive coding-like sessions;
- OpenClaw-like embedded kernel;
- TS-side agent runtime;
- possible local control-plane experience.

### 2.3 CLI / TUI

Use:

- Typer for CLI;
- Rich for tables, panels, logs, progress, trees;
- Textual for TUI;
- prompt-toolkit for interactive input;
- questionary for selection/confirmation prompts.

### 2.4 Storage

V0:

- filesystem for human-readable project state;
- JSONL for events and tool calls;
- SQLite for indexes and fast queries;
- Markdown for editable summaries and memory notes.

Later:

- Postgres for multi-user/multi-project;
- pgvector or Qdrant for retrieval;
- object storage for large artifacts;
- OpenTelemetry/Langfuse/Phoenix/LangSmith for tracing.

---

## 3. Repository Structure

Recommended implementation repository:

```text
novi/
  README.md
  pyproject.toml
  uv.lock

  src/novi/
    __init__.py

    core/
      models.py              # Pydantic domain models
      ids.py                 # stable ID generation
      events.py              # EventRecord and event bus
      skills.py              # SkillRegistry and SKILL.md loader
      sessions.py            # SessionManager
      context.py             # ContextPackBuilder
      tools.py               # ToolRegistry and ToolRuntime
      policies.py            # PolicyGate
      runs.py                # RunLedger and RunManager
      artifacts.py           # ArtifactStore
      memory.py              # MemoryCandidateStore and MemoryStore
      modules.py             # ModuleRegistry

    kernels/
      base.py                # AgentKernel protocol
      deepagents_kernel.py   # DeepAgents/LangGraph adapter
      simple_kernel.py       # tiny fallback kernel
      pi_kernel.py           # later spike
      workers.py             # Codex/OpenHands/Claude Code workers later

    modules/
      filesystem/
      shell_sandbox/
      search/
      web_fetch/
      git/
      python_exec/
      mcp_client/
      ros_stub/
      training_stub/
      sim_stub/

    cli/
      main.py
      init.py
      chat.py
      run.py
      skills.py
      sessions.py
      tools.py
      memory.py
      modules.py

    tui/
      app.py
      screens/
      widgets/

    channels/
      base.py
      webhook.py
      telegram.py

    storage/
      fs.py
      sqlite.py
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

  docs/
    implementation.md
    kernels.md
    tooling.md
    modules.md
    tui.md
    testing.md
```

Project workspace:

```text
project-root/
  .novi/
    novi.yaml
    specs/
    skills/
    sessions/
    runs/
    artifacts/
    memory/
    modules/
    indexes/
```

---

## 4. Domain Models to Implement First

Use Pydantic models even if the main agent kernel is not Pydantic AI.

### 4.1 SkillSpec

```python
class SkillSpec(BaseModel):
    id: str
    name: str
    description: str
    path: Path
    version: str | None = None
    commands: list[str] = []
    requires_tools: list[str] = []
    optional_tools: list[str] = []
    policies: list[str] = []
    tags: list[str] = []
    metadata: dict[str, Any] = {}
```

Skill loading should be permissive:

- read `SKILL.md` frontmatter if available;
- require only standard skill fields when possible;
- keep Novi-specific metadata optional;
- index scripts/references/assets without enforcing strict structure.

### 4.2 ToolSpec

```python
class ToolSpec(BaseModel):
    id: str
    module: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any] | None = None
    side_effect: bool = False
    risk: Literal["low", "medium", "high", "critical"] = "low"
    policies: list[str] = []
    timeout_seconds: int | None = None
    audit: dict[str, Any] = {}
```

### 4.3 RunSpec

```python
class RunSpec(BaseModel):
    id: str
    type: str
    objective: str
    session_id: str
    skill_refs: list[str] = []
    module_refs: list[str] = []
    status: Literal["created", "running", "blocked", "failed", "completed", "cancelled"]
    created_at: datetime
    updated_at: datetime
```

### 4.4 EventRecord

```python
class EventRecord(BaseModel):
    id: str
    run_id: str | None = None
    session_id: str | None = None
    type: str
    timestamp: datetime
    payload: dict[str, Any]
```

### 4.5 ContextPack

```python
class ContextPack(BaseModel):
    id: str
    session_id: str
    run_id: str | None = None
    active_skill_ids: list[str]
    model_profile: str
    token_budget: int | None = None
    sections: list[dict[str, Any]]
    artifact_refs: list[str] = []
    memory_refs: list[str] = []
```

### 4.6 MemoryCandidate

```python
class MemoryCandidate(BaseModel):
    id: str
    type: Literal["project", "session", "episodic", "procedural"]
    subject: str
    claim: str
    evidence: dict[str, Any]
    confidence: Literal["low", "medium", "high"] = "medium"
    scope: str | None = None
    status: Literal["proposed", "accepted", "rejected"] = "proposed"
```

---

## 5. Agent Kernel Adapter Interface

Do not couple Novi directly to DeepAgents, Pi, Pydantic AI, or Codex.

Define a small adapter interface:

```python
class AgentKernel(Protocol):
    async def run(self, request: AgentRunRequest) -> AsyncIterator[AgentEvent]:
        ...

    async def cancel(self, run_id: str) -> None:
        ...

    async def resume(self, run_id: str, request: AgentRunRequest) -> AsyncIterator[AgentEvent]:
        ...
```

`AgentRunRequest` should contain:

```text
session_id
run_id
context_pack
tools available through Novi ToolRuntime
active skills
model profile
workspace path
```

`AgentEvent` should normalize events from different kernels:

```text
message.delta
message.completed
tool.requested
tool.result
artifact.created
plan.updated
error
run.completed
```

This lets Novi use DeepAgents now and still support Pi or other kernels later.

---

## 6. DeepAgents Kernel Integration

### 6.1 What DeepAgents should handle

Use DeepAgents for:

- multi-step reasoning loop;
- planning and task decomposition;
- subagents within a run;
- filesystem working memory;
- LangGraph state/checkpoint;
- long-running research or experiment workflows.

### 6.2 What Novi must still own

Novi must still own:

- skill registry;
- context pack compilation;
- long-term memory;
- tool policy;
- run ledger;
- artifact indexing;
- approvals;
- final audit trail.

### 6.3 Tool wrapping pattern

DeepAgents tools should be wrappers around Novi ToolRuntime.

```text
DeepAgents tool call
  → Novi ToolRuntime.request_tool_call()
  → schema validation
  → policy check
  → approval if required
  → actual module implementation
  → result normalization
  → event log
  → DeepAgents tool result
```

Do not pass high-risk native tools directly to DeepAgents.

### 6.4 Filesystem working memory

DeepAgents filesystem should be treated as run-local working memory.

Promotion rules:

```text
working file → artifact only after ArtifactStore registers it
working note → memory only after MemoryCandidate review
```

### 6.5 Checkpoints

Use LangGraph SQLite checkpointing for run execution state.

Keep separate:

```text
LangGraph checkpoint = execution recovery state
Novi RunLedger     = audit and experiment history
```

---

## 7. Pi Kernel Integration Later

Pi is useful for interactive local coding-agent-like sessions and OpenClaw-style embedded runtime.

Recommended use:

```text
PiKernel
  - interactive chat sessions
  - coding-like workflows
  - extension experiments
  - local control-plane UX
```

Boundary:

```text
Pi session state is execution state, not Novi source of truth.
```

When integrating Pi:

- wrap Pi tool calls through Novi ToolRuntime;
- translate Pi events to Novi EventRecord;
- keep SKILL.md loading in Novi, not Pi;
- keep memory writes in Novi MemoryCandidate flow;
- avoid storing authoritative platform state inside Pi session files only.

---

## 8. Tooling Modules Worth Reusing

### 8.1 Agent and workflow

| Tool | Use in Novi |
|---|---|
| DeepAgents | Default research/experiment agent kernel |
| LangGraph | checkpoint, stateful workflows, pause/resume |
| Pi Agent Core | optional interactive/coding-like kernel |
| Pydantic AI | optional typed-agent adapter or structured-output helper |
| Agno | production runtime/control-plane reference |
| OpenHands SDK | external coding worker |
| Codex / Claude Code | external implementation/refactor worker |
| smolagents | minimal code-agent reference |

### 8.2 CLI / TUI

| Tool | Use in Novi |
|---|---|
| Typer | CLI command framework |
| Rich | terminal panels, tables, progress, logs |
| Textual | full TUI control plane |
| prompt-toolkit | interactive command input |
| questionary | prompts, choices, confirmations |

### 8.3 Storage and indexing

| Tool | Use in Novi |
|---|---|
| SQLite | local metadata index |
| SQLAlchemy / SQLModel | optional ORM layer |
| JSONL | append-only event and tool-call logs |
| filesystem | local-first workspace state |
| Postgres | future multi-project/multi-user backend |
| pgvector / Qdrant | future memory/artifact retrieval |

### 8.4 Search and document processing

| Tool | Use in Novi |
|---|---|
| Tavily | quick hosted search for research skill |
| SearXNG | self-hosted metasearch later |
| Crawl4AI | crawler/fetcher for LLM-ready pages |
| httpx | HTTP fetch |
| markdownify / trafilatura | HTML to text/markdown extraction |
| pymupdf / pypdf | PDF parsing |
| LlamaIndex | RAG/document module later |
| Haystack | deterministic document pipeline later |

### 8.5 MCP and external tools

| Tool | Use in Novi |
|---|---|
| langchain-mcp-adapters | MCP client integration for DeepAgents/LangGraph |
| official MCP SDKs | later direct MCP client/server support |
| mcporter-like bridges | optional non-native MCP bridge pattern |

### 8.6 Channels

| Tool | Use in Novi |
|---|---|
| FastAPI | webhook server and future API |
| aiohttp | async channel/webhook support |
| python-telegram-bot | Telegram adapter |
| discord.py | Discord adapter |
| slack-sdk | Slack adapter |
| Pipecat | future voice/multimodal channel |

### 8.7 Sandbox and execution

| Tool | Use in Novi |
|---|---|
| Docker SDK / subprocess wrapper | sandboxed shell execution |
| Playwright | browser automation module |
| OpenHands SDK | coding sandbox worker |
| E2B / Daytona / Modal | optional remote sandbox later |
| nbclient / ipykernel | notebook/python execution module |

### 8.8 Observability

| Tool | Use in Novi |
|---|---|
| LangSmith | natural fit with LangGraph/DeepAgents |
| Langfuse | open LLM tracing and prompt/eval management |
| Phoenix | tracing/evals for LLM/RAG workflows |
| OpenTelemetry | common tracing abstraction |
| Rerun | future robotics/multimodal visual logs |
| Prometheus/Grafana | system metrics later |

---

## 9. TUI Control Plane Design

Use Textual after CLI basics work.

Initial screens:

```text
SessionScreen
  - current session summary
  - active skills
  - recent runs

RunScreen
  - event timeline
  - tool calls
  - artifacts
  - run summary

ApprovalScreen
  - pending tool approvals
  - memory candidates
  - risky actions

SkillScreen
  - installed skills
  - active skill context
  - skill resources

MemoryScreen
  - proposed memories
  - accepted memories
  - rejected/stale memories
```

Textual widgets:

```text
RunTimeline
ToolCallTable
ArtifactTree
SkillList
ContextPackViewer
MemoryCandidatePanel
ApprovalModal
```

Start with Rich-only CLI output. Move to Textual once the event model is stable.

---

## 10. Context Pack Implementation

Context packing should be deterministic and inspectable.

Build order:

```text
1. platform/system rules
2. project summary
3. session summary
4. active skill instructions
5. run objective and current state
6. recent relevant messages
7. retrieved memory
8. selected artifacts
9. tool manifest summary
10. output contract
```

ContextPack should be saved for each major model call:

```text
.novi/sessions/<session_id>/context_packs/<ctx_id>.json
```

This enables:

- audit;
- reproduction;
- debugging hallucinations;
- comparing kernels;
- regression tests.

Do not rely on raw chat history as the only context source.

---

## 11. Run Ledger Implementation

Use append-only JSONL first.

```text
.novi/runs/run_001/
  run.yaml
  events.jsonl
  tool_calls.jsonl
  artifacts/
  summary.md
```

Every important step emits an event:

```text
RunCreated
ContextPackBuilt
SkillActivated
KernelStarted
MessageDelta
ToolRequested
ToolPolicyChecked
ToolApproved
ToolRejected
ToolExecuted
ArtifactCreated
MemoryCandidateProposed
RunCompleted
RunFailed
RunSummarized
```

Maintain SQLite indexes:

```text
runs
sessions
events
tool_calls
artifacts
memory_candidates
skills
```

The filesystem remains the canonical local artifact store; SQLite is an index.

---

## 12. Policy Gate Implementation

Start simple. Avoid building a full policy language immediately.

V0 policy checks:

```text
schema_valid
side_effect_requires_audit
high_risk_requires_approval
shell_requires_sandbox
filesystem_write_requires_workspace
external_network_requires_allowed_tool
memory_write_requires_evidence
```

Policy result:

```python
class PolicyDecision(BaseModel):
    allowed: bool
    requires_approval: bool = False
    reasons: list[str] = []
    redactions: list[str] = []
    metadata: dict[str, Any] = {}
```

ToolRuntime should block execution unless PolicyGate returns allowed or approved.

---

## 13. Memory Candidate Flow

Memory is not automatic append-to-notes.

Implementation flow:

```text
Run completes
→ Orchestrator proposes memory candidates
→ Auditor reviews evidence
→ user accepts/rejects through CLI/TUI
→ committed memory written to memory store
```

V0 storage:

```text
.novi/memory/project.md
.novi/memory/episodic.jsonl
.novi/memory/procedural.jsonl
.novi/memory/candidates/*.yaml
```

Every committed memory should include:

```text
claim
scope
confidence
evidence refs
source run refs
created_at
updated_at
```

---

## 14. Channel Adapter Implementation

Do not build a full gateway at first.

Channel adapter interface:

```python
class ChannelAdapter(Protocol):
    async def receive(self) -> AsyncIterator[ChannelMessage]: ...
    async def send(self, message: ChannelReply) -> None: ...
```

V0 channels:

```text
webhook
telegram
```

Supported commands:

```text
/novi ask ...
/novi status
/novi inspect <run_id>
/novi approve <approval_id>
/novi run research ...
```

Do not allow high-risk actions directly from IM.

---

## 15. Testing Strategy

### 15.1 Unit tests

Cover:

```text
SKILL.md parsing
SkillRegistry indexing
ContextPack building
ToolSpec validation
PolicyGate decisions
RunLedger append/read
MemoryCandidate validation
ArtifactStore hashing/indexing
```

### 15.2 Golden tests

Save expected context packs for fixed sessions:

```text
tests/golden/context_pack_research_001.json
```

This catches accidental prompt/context regressions.

### 15.3 Fake kernel tests

Implement `SimpleKernel` that emits deterministic events.

Use it to test Novi Core without calling real models.

### 15.4 Tool sandbox tests

Test:

```text
shell timeout
workspace escape prevention
write permission checks
approval required behavior
artifact capture
```

### 15.5 Integration tests

Start with:

```text
novi init
novi skill list
novi run research "test objective"
novi run inspect <run_id>
novi memory review
```

---

## 16. Build Milestones

### Milestone 0: repository skeleton

Deliver:

```text
pyproject
src/novi
basic CLI
.novi init
Pydantic models
filesystem storage
```

### Milestone 1: skills and sessions

Deliver:

```text
SKILL.md loader
SkillRegistry
SessionManager
session summary file
skill activation
```

### Milestone 2: run ledger and artifacts

Deliver:

```text
RunManager
EventRecord append/read
ArtifactStore
tool_call records
run inspect CLI
```

### Milestone 3: tool runtime

Deliver:

```text
ToolRegistry
ToolRuntime
PolicyGate
filesystem.read
filesystem.write_draft
web.fetch
search.query
shell.run_sandboxed
```

### Milestone 4: DeepAgents kernel

Deliver:

```text
DeepAgentsKernel
ContextPack → DeepAgents prompt/input
DeepAgents tool wrapper → Novi ToolRuntime
event bridge → Novi RunLedger
SQLite checkpoint
```

### Milestone 5: TUI alpha

Deliver:

```text
Textual app
Session screen
Run timeline
Tool call table
Approval panel
```

### Milestone 6: memory candidate flow

Deliver:

```text
memory proposal
memory review
accept/reject
committed memory store
```

### Milestone 7: channel adapter

Deliver:

```text
webhook or Telegram adapter
status/inspect/approve commands
```

### Milestone 8: optional kernel spikes

Deliver:

```text
PiKernel spike
Codex/OpenHands worker spike
MCP client spike
```

---

## 17. Recommended First Demo

First working demo should not involve robotics, training, or MCP.

Target:

```text
novi init
novi skill list
novi run research "Find and summarize recent ideas around skill learning for physical AI"
novi run inspect <run_id>
novi memory review
```

The run should show:

```text
skill activation
context pack generated
tool calls logged
artifacts captured
run summary created
memory candidate proposed
```

Once this loop works, add:

```text
experiment.design skill
code.maintain skill
PiKernel spike
Telegram adapter
MCP client
ROS/training/sim stubs
```

---

## 18. Practical Decision Summary

Recommended immediate choices:

```text
Core: Python
Agent kernel: DeepAgents + LangGraph
CLI: Typer
Terminal UI: Rich first, Textual next
Checkpoint: langgraph-checkpoint-sqlite
Storage: filesystem + SQLite
Search: Tavily first, SearXNG/Crawl4AI later
MCP: langchain-mcp-adapters later
Channels: webhook/Telegram only
Coding worker: Codex/OpenHands later
Pi: second kernel spike, not v0 default
```

Do not build yet:

```text
full plugin marketplace
full OpenClaw-style gateway
multi-agent organization layer
robot-first runtime
automatic long-term memory
full MCP server
production web dashboard
complex policy language
```

Core architectural boundary:

```text
DeepAgents/Pi can execute agent loops.
Novi must own skills, sessions, context, tools, runs, memory, artifacts, policies, and control-plane state.
```

