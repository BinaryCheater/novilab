# Exploration Spec

Status: Exploration

This document records design investigation rather than accepted implementation
scope. The exploration target is the future capability set itself:
configurable multi-agent work, workflow construction and iteration,
multi-user collaboration and content merge, direct agent guidance, and
scientific memory. It also keeps the EvoScientist/DeepAgents comparison as
reference material for implementation choices.

The central design proposition is:

```text
How can Novi build configurable multi-agent execution, self-iterating workflows,
multi-user collaboration, and reliable scientific memory together without
losing control of scope, state, or audit?
```

The purpose is to keep the larger product thesis visible while Phase 1 remains
local-first and inspectable.

## Exploration Scope

Open:

This document is not only about implementing several features at once. It is
about understanding what these features should mean in Novi.

The explored feature areas are:

1. Configurable multi-agent work: agent profiles, prompts, tool sets,
   permissions, model profiles, output schemas, interfaces, kernel bindings,
   and per-run participant snapshots.
2. Workflow construction and iteration: generated plans, workflow records,
   success signals, executable steps, reflection, workflow patches, and
   accepted revisions.
3. Multi-user collaboration and content merge: project participants, imported
   knowledge, comments, review, contribution records, merge decisions, and
   attribution.
4. Direct agent work and user guidance: allowing a user to work directly in a
   DeepAgents-like session while still bringing meaningful outputs back through
   Novi artifacts, contributions, memory candidates, or workflow patches.
5. Reliable scientific memory: durable knowledge that supports discovery by
   tracking claims, procedures, hypotheses, evidence, negative results,
   contradictions, confidence, review, and supersession.

The implementation question is downstream of this exploration:

```text
Which objects and flows are real Novi concepts, and which can remain adapters,
kernel-local state, artifacts, or temporary implementation scaffolding?
```

## Background

Novi's current accepted direction is a skill-first, session-aware control plane.
Novi owns sessions, runs, tools, artifacts, memory candidates, policies, context
packs, and audit records. External systems such as DeepAgents, LangGraph, MCP,
Codex, Claude Code, browser tools, search providers, training systems, and ROS
are adapters or modules.

The emerging question is whether Novi should stay a thin local run ledger around
external agent frameworks, or become a broader research operating layer where
agents, humans, workflows, imported knowledge, memory, and scientific evidence
co-evolve.

The user intent appears to be the broader layer:

- configurable multi-agent work: prompts, tool sets, permissions, model
  profiles, interfaces, and scopes should be easy to define and revise;
- automatic workflow construction and iteration: agents should generate,
  execute, evaluate, and patch workflows rather than only respond once;
- multi-user collaboration and content merge: users should be able to import
  knowledge, guide agents, review outputs, work directly with DeepAgents-like
  surfaces, and merge results into shared project state;
- reliable self-iterating scientific memory: durable memory should support
  scientific discovery, not just personalization or chat continuity.

Clarification:

Novi should not encode domain-specific research concepts such as "physical
priors" as core framework objects. Domain concepts belong in project skills and
the Markdown document library. Novi's responsibility is to preserve provenance,
run the relevant skills through scoped agents or workers, record artifacts and
proposed changes, require review before shared state changes, and make accepted
records available to later runs.

## Functional Exploration

### Configurable Multi-Agent Work

Open:

The desired capability is not merely "multiple agents can talk." Novi needs a
configuration and execution model where agents are useful because they separate
real boundaries:

- responsibility: planner, researcher, coder, auditor, reviewer, operator,
  simulator, trainer, or domain specialist;
- prompt and instruction set: stable system prompt, active skills, task
  protocol, output constraints, and review criteria;
- tool set: visible tools, callable tools, executable tools, and tools that
  require approval;
- permission scope: read, write, shell, network, external side effect, physical
  world, memory proposal, memory acceptance, workflow patch, or review;
- context scope: project spec, session summary, imported knowledge, artifacts,
  accepted memory, recent messages, current workflow, or selected run records;
- model profile: different providers, models, reasoning effort, cost limits, or
  latency preferences;
- interface: CLI, TUI, web, channel, direct DeepAgents session, worker adapter,
  or headless run;
- output contract: report, evidence table, patch, review decision, memory
  candidate, workflow patch, code diff, metrics, or audit note.

Design tension:

If agent profiles become too weak, Novi users will fall back to editing
DeepAgents YAML, prompts, or raw tool lists outside Novi. If they become too
strong too early, Novi turns into a full multi-agent framework before the run
ledger, memory, and workflow layers are proven.

Current working direction:

Novi should define project-local agent profiles as platform records, then
compile them into the selected execution kernel. A DeepAgents subagent is one
possible compiled form, not the source record.

### Workflow Construction And Iteration

Open:

The desired capability is an agent-assisted workflow loop, not a static
checklist. Novi should help a user move from objective to workflow, from
workflow to execution, from execution to evidence, and from evidence to a
reviewable workflow update.

A workflow may need:

- objective and scope;
- assumptions and open questions;
- stages or steps;
- agent assignment per step;
- required tools and permissions;
- expected artifacts;
- success signals and stop criteria;
- iteration triggers;
- resource estimates and preflight checks;
- reflection outputs;
- workflow patches and accepted revisions.

Design tension:

EvoScientist shows that prompt-driven workflows can be highly effective and
flexible. Novi still needs record-shaped workflow state when workflow evolution
must be reviewed, replayed, compared, or used as future context.

Current working direction:

Workflow should start as lightweight records or artifacts promoted through
review. Do not build a heavy workflow engine first. The first requirement is
that workflow creation, execution, reflection, and patching are inspectable.

### Skill-Driven Document Processing And Patch Merge

Open:

A core user flow is that a human collaborator imports a document, note, log, or
direct agent-session export whose contents may be clear, partial, or
ambiguous. The user should not have to hand-write a patch. Instead, Novi should
record the import as raw material, then allow a scoped agent to process it with
the selected skills and produce reviewable outputs.

The first useful processing loop is:

```text
import document
-> preserve raw artifact and import contribution
-> process with a selected skill/workflow and scoped agent
-> write an analysis note artifact
-> optionally produce one or more document patch contributions
-> review/check the patch
-> accept applies the patch, reject preserves history, conflict blocks merge
-> later runs consume accepted document state and trace its provenance
```

The patch is an agent or worker output format, not the primary human input. A
human may provide direct guidance and choose the target document. A provided
target is a hard constraint. The normal route is for the agent to use the
import, user hint, and provided library context to generate an analysis note
and zero, one, or multiple patch candidates for review.

Current working direction:

- If a target document is provided, the processing run may create a patch
  contribution against that target.
- If no target document is provided, the processing run may propose merges into
  existing documents, new documents, or questions for a human based on the
  provided library context.
- Patch targets are initially limited to the Markdown knowledge/document
  library, workflow records, and project-local skills.
- Accepted specs, source code, tests, and project configuration are out of
  scope for this patch path.
- Agent-generated patches must carry source refs from the import, run, analysis
  artifact, accepted knowledge, or worker bundle. Human-authored changes can be
  more permissive, but must still be attributable.
- Accepting a patch performs a dry-run/check first, applies only if the target
  scope and patch are valid, and records changed files and merge metadata.
- If patch application fails, Novi does not modify target files; it marks the
  contribution as conflicted and may assign it to a merge/review agent to
  propose a revised patch or review recommendation.

This keeps domain research content in skills and documents while making the
merge path auditable.

### Multi-User Collaboration And Content Merge

Open:

The desired capability is not only channels or chat access. Novi needs a way
for multiple humans and agents to contribute to shared project state without
silently overwriting accepted knowledge, workflows, summaries, or memory.

Collaboration may include:

- importing papers, notes, datasets, logs, code, experiment results, or direct
  agent-session exports;
- assigning review or analysis to humans, agents, or external workers;
- commenting on runs, artifacts, tool calls, memory candidates, and workflow
  patches;
- accepting, rejecting, or requesting changes;
- merging selected contributions into project state;
- preserving rejected contributions as audit history;
- attributing actions to a human, agent, worker, or system process.

Design tension:

Building realtime collaborative editing, full team admin, notifications, and
fine-grained permissions too early would derail the local-first core. But
without a contribution and merge model, multi-user work becomes an unstructured
chat transcript.

Current working direction:

Start with contribution records and review decisions, not realtime editing. The
merge unit can be coarse at first: imported artifact, extracted claim, memory
candidate, workflow patch, skill patch, or run summary patch.

For document-library and skill evolution, the preferred merge unit is a patch
contribution. Agents may propose patches to documents, workflows, or
project-local skills, but accepted files are updated only after review and a
successful patch check.

### Direct Agent Work And User Guidance

Open:

The desired capability includes users working directly with a DeepAgents-like
agent surface and giving it guidance to iterate. Novi should not prevent direct
agent use, but it should define how direct work affects shared project state.

Important cases:

- user starts a direct agent session for exploratory thinking;
- user gives high-level guidance and lets the agent iterate;
- agent asks the user for clarification or checkpoint decisions;
- direct session generates files, notes, reports, plans, or code;
- user wants to import some outputs into Novi;
- user wants to discard or archive the rest.

Design tension:

If Novi forces every interaction through rigid run commands, it may lose the
fluidity that makes DeepAgents useful. If Novi lets direct agent state become
project state automatically, audit and merge boundaries disappear.

Current working direction:

Treat direct agent sessions as execution workspaces. Import their outputs into
Novi as artifacts and contributions, then review/merge the pieces that should
affect accepted project state.

### Reliable Scientific Memory

Open:

The desired capability is not simply persistent chat memory. Scientific memory
must help future runs make better research decisions while remaining
evidence-based, reviewable, and correctable.

Memory may need to represent:

- preferences and constraints;
- procedural lessons;
- known promising directions;
- known failed directions;
- hypotheses;
- claims;
- experimental setup;
- result summaries;
- negative results;
- contradictions;
- replications or failed replications;
- artifact links;
- confidence and scope;
- supersession history.

Design tension:

Markdown memory is easy to inspect and edit, but weak for contradiction,
supersession, retrieval, and evidence tracking. A full knowledge graph is
powerful but likely too heavy before the basic review loop is proven.

Current working direction:

Start with evidence-backed memory candidates and accepted memory records. The
minimum durable unit should be a claim or procedure with type, scope, evidence
refs, confidence, review decision, and supersession state. Markdown can remain
the readable surface, but the underlying record should preserve provenance.

Domain-specific scientific constructs should not all become Novi object types.
When a project wants to maintain a topic such as physical priors, it can do so
through skill-defined methods and Markdown documents that summarize, link, and
revise the relevant knowledge. Novi should track the documents, patches,
artifacts, review decisions, memory candidates, and lineage around that work.

### Layered Knowledge And Memory Boundaries

Open:

Novi should distinguish a project knowledge base from agent/session memory.

The project knowledge base may start as a layered Markdown vault with backlinks,
where different layers have different trust and review semantics:

1. Raw inputs: source files, links, excerpts, notes, logs, paper snippets, and
   imported direct-session exports. These are factual inputs or references, not
   accepted conclusions.
2. Analysis notes: agent or human analysis derived from raw inputs, with links
   back to source artifacts or excerpts.
3. Accepted conclusions: reviewed claims, procedures, negative results,
   hypotheses, experiment summaries, and decisions.
4. Indexes and syntheses: directory pages, topic maps, literature summaries,
   workflow summaries, and project-level overview documents.

The Markdown vault should support human-readable `[[links]]`, but links alone
are not enough for scientific reliability. Accepted conclusion pages should
preserve provenance, evidence refs, review status, confidence, and supersession
metadata when applicable.

The long-term scientific memory system may eventually be delegated to a
specialized external project or memory manager. Novi should therefore treat the
vault as an adapter boundary:

- Novi can import from it into context packs.
- Novi can propose updates to it as reviewable contributions.
- A memory manager agent or external memory project may maintain structure,
  backlinks, summaries, and retrieval indexes.
- Novi Core should still record which memory or knowledge pages affected a run.

### Memory Types

Open:

Novi should separate at least three memory-like systems:

1. Project knowledge base:
   A layered Markdown vault containing raw inputs, excerpts, analysis,
   accepted conclusions, indexes, and syntheses. It is project-readable and may
   be maintained by humans, agents, or a separate memory manager.
2. Agent/session mid-term memory:
   File-backed working memory for an ongoing agent session or long run. Its
   purpose is to avoid context overflow by summarizing intermediate state,
   decisions, open questions, and scratch work. It is useful execution state,
   but not accepted project knowledge.
3. Long-term agent improvement memory:
   Memory about workflows, prompts, skills, agent behavior, evaluation results,
   and process improvements. This may be managed by a specialized agent that
   proposes workflow patches, prompt patches, skill patches, or memory-vault
   updates. It should not silently mutate accepted workflows, prompts, or
   skills.

Novi should record when any of these memory systems influence a run, but only
reviewed project knowledge, accepted workflow revisions, accepted skill changes,
or accepted memory contributions should become durable project state.

### Agent Levels And Authority

Open:

Not every agent should be treated as the same kind of participant.

Novi should distinguish:

1. User-level agents:
   Agents that operate as high-level collaborators with the user. They may help
   plan, review, summarize, question assumptions, propose workflow changes,
   propose memory updates, or coordinate executor agents. They can propose
   changes to project state, but still cannot bypass review rules.
2. Reviewer or auditor agents:
   Agents that inspect evidence, traces, workflow patches, memory candidates,
   tool calls, and contributions. They may recommend accept/reject/request
   changes, but v0/v1 should not let them unilaterally commit high-impact
   project state without an explicit policy decision.
3. Executor agents:
   Agents that perform bounded steps under a declared tool scope, context scope,
   permission scope, and output contract. They are not peers of the user; they
   are scoped workers. Their outputs enter Novi as artifacts, tool calls, step
   results, or contribution candidates.

This distinction matters for UX and policy. A user-level agent may appear in a
session as a collaborator, while an executor agent should usually be visible as
a run participant or workflow step assignee. Both must still be represented in
run records when they affect execution or state.

## What EvoScientist Actually Builds On DeepAgents

Observation:

EvoScientist is not just a prompt around DeepAgents. Its public code shows an
application stack around `deepagents.create_deep_agent`:

- `subagent.yaml` defines role-specific subagents such as planner, researcher,
  code, debug, data-analysis, and writing agents.
- The main agent factory assembles model configuration, DeepAgents backends,
  middleware, MCP tools, subagents, skills, and system prompt.
- A `CompositeBackend` routes workspace files, skills, and memories into
  different virtual paths.
- Custom sandbox backends add path validation, command validation, and safer
  shell behavior.
- Middleware handles memory injection/extraction, context editing, tool
  selection, tool errors, and agent-initiated user questions.
- MCP integration supports tool allowlists and `expose_to` routing so a server's
  tools can be routed to the main agent or selected subagents.
- Sessions use LangGraph SQLite checkpoints with pruning.
- Channel adapters route messages from multiple chat platforms through a shared
  message bus with allowlists, deduplication, mention gating, per-chat locks,
  and outbound formatting.

Interpretation:

EvoScientist is a DeepAgents-native scientific assistant product. DeepAgents and
LangGraph remain the execution and checkpointing substrate; EvoScientist adds
opinionated scientific roles, workflow prompts, middleware, memory files,
channels, and skill management.

## Reference Comparison

Observation:

The comparison below is reference material for Novi design. It is not a claim
that Novi must implement everything EvoScientist implements, or that
EvoScientist should be treated as the target architecture.

| Area | DeepAgents | EvoScientist | Novi implication |
|---|---|---|---|
| Execution loop | Provides model/tool loop, planning, filesystem working memory, subagents, interrupts, and LangGraph-based state | Uses `create_deep_agent` as the central assembly point | Reuse as kernel; do not duplicate the loop unless Novi needs a boundary DeepAgents cannot expose |
| Agent configuration | Supports subagent definitions with prompts, tools, models, permissions, and middleware | Externalizes fixed scientific roles in `subagent.yaml` | Define Novi `AgentProfile` first, then compile into DeepAgents subagents or other worker bindings |
| Tool exposure | Tools are passed into the agent and can be permission-gated | Adds MCP allowlists and `expose_to` routing by target agent | Adopt allowlist/routing ideas, but every external tool should become or wrap a Novi ToolSpec with risk and policy |
| Filesystem | DeepAgents filesystem is natural working memory | Routes workspace, skills, and memories through `CompositeBackend`; custom sandbox protects paths and commands | Treat kernel files as working state; only reviewed exports become Novi artifacts or accepted project state |
| Workflow | Supports todo/planning patterns and subagent task delegation | Encodes scientific lifecycle in prompts, skills, planner reflection, and report templates | Keep prompt-driven flexibility, but promote workflows and patches to inspectable records when they affect future work |
| Context management | Provides summarization/context editing middleware | Adds context editing and tool selection middleware tuned for scientific sessions | Use middleware inside kernel adapter; keep Novi `ContextPack` as the inspectable source boundary |
| Memory | Supports persistent memory patterns and backend storage | Injects and extracts Markdown memory for user profile, preferences, and experiment conclusions | Useful pattern, but Novi memory must be reviewable, evidence-backed, and contradiction-aware |
| Human input | Supports human-in-the-loop interrupts | Adds `ask_user` for research clarification and recovery decisions | Good adapter pattern; Novi should record questions, answers, approvals, and resulting state changes |
| Channels | Not a collaboration system by itself | Provides many channel adapters, allowlists, group mention handling, message bus, and per-chat locks | Channels are useful surfaces, but not a substitute for project participants, contributions, and merge decisions |
| Sessions | Uses LangGraph threads/checkpoints | Stores sessions in SQLite checkpoints and prunes old snapshots | Link checkpoints for execution recovery; preserve Novi run ledger as source of truth |
| Scientific reliability | Provides mechanisms, not scientific epistemology | Adds scientific prompts, skills, rigor checklists, and memory evolution triggers | Novi needs explicit evidence, claims, negative results, review, and supersession records |

## Coverage By Desired Feature

Observation:

The user's desired capabilities map to existing systems unevenly:

| Desired capability | DeepAgents support | EvoScientist support | Novi gap |
|---|---|---|---|
| Configurable multi-agent prompts/tools/permissions/interfaces | Strong execution primitives | Practical YAML subagents and MCP tool routing | Platform-owned agent profiles, versioning, audit, compile targets |
| Automatic workflow construction and iteration | Todos, planning, subagents, interrupts | Scientific lifecycle prompts, planner reflection JSON, skills | Workflow records, workflow patches, review/merge, next-run context inclusion |
| Multi-user collaboration and content merge | Not a core feature | Multi-channel access, allowlists, group context | Participants, contributions, comments, review, merge decisions, conflict history |
| User knowledge import processed by agents | Possible through files/tools | Possible through workspace and skills | Formal import artifacts, extraction state, candidate generation, review |
| User direct work on DeepAgents-like surface | Native | CLI/TUI/script/channel use | Import direct session outputs without bypassing Novi review |
| User guidance for autonomous iteration | Interrupts and long-running state | `ask_user`, human-on-the-loop prompt posture, workflow reflection | Recorded guidance, decisions, workflow patches, and accepted/rejected state changes |
| Reliable self-iterating scientific memory | Memory primitives | Markdown EvoMemory and memory-evolution skills | Evidence-backed claim/procedure records, contradictions, negative results, supersession |

## DeepAgents And EvoScientist Coverage

### Configurable Multi-Agent

Decision candidate:

DeepAgents provides useful primitives for subagents, tools, model selection,
permissions, and human-in-the-loop interrupts. EvoScientist proves that a
practical scientific agent can externalize subagent definitions into YAML and
inject MCP tools per agent.

Gap for Novi:

EvoScientist's subagents are execution helpers. Novi needs platform agent
profiles that can be audited, versioned, scoped, reviewed, and compiled into
DeepAgents subagents or other kernels. A Novi agent should remain a run
participant when it represents a distinct responsibility, permission boundary,
tool set, context scope, execution environment, output schema, or audit identity.

### Workflow Construction And Iteration

Decision candidate:

EvoScientist implements workflow mostly through system prompts, skills, todos,
planner-agent reflection, and report templates. This is effective for a
scientific assistant because it lets the model adapt flexibly.

Gap for Novi:

Novi needs workflows as records, not only as prompt text or `/todos.md`. A
workflow should be generated, executed, evaluated, and revised through explicit
objects:

```text
WorkflowSpec
  -> WorkflowRun
  -> StepRun
  -> Reflection
  -> WorkflowPatch
  -> ReviewDecision
```

Agents may propose workflow patches, but Novi should record what changed, why,
what evidence motivated the change, and who accepted it.

### Multi-User Collaboration And Content Merge

Observation:

DeepAgents itself is not a multi-user collaboration system. EvoScientist has
multi-channel messaging, allowlists, group context, and per-chat locks. That is
useful for access and communication, but it is not the same as project-level
identity, ownership, review, merge, conflict handling, and audit attribution.

Gap for Novi:

Novi should treat user-provided knowledge, agent output, worker output, review
comments, and merge decisions as contributions to project state. The first
collaboration layer should not be realtime collaborative editing. It should be a
mergeable contribution ledger:

```text
Contribution
  = actor
  + source
  + target object
  + proposed change
  + evidence refs
  + review state
  + merge decision
```

This supports multiple humans, imported documents, direct DeepAgents sessions,
Codex/Claude/OpenHands worker outputs, and agent-generated revisions without
making any external channel or worker the source of truth.

### User Guidance And Direct Agent Work

Observation:

DeepAgents supports long-running sessions, interrupts, and direct agent
interaction. EvoScientist exposes direct CLI/TUI use, single-shot mode, scripts,
channels, `ask_user`, and session resume.

Gap for Novi:

Novi should allow direct DeepAgents-like work, but direct work must still return
through Novi boundaries when it is meant to affect project state. A useful split:

- interactive execution state belongs to the kernel;
- accepted project state belongs to Novi;
- anything imported from a direct agent session becomes artifacts,
  contributions, memory candidates, workflow patches, or skill patches.

### Scientific Memory

Observation:

DeepAgents has memory primitives and backend storage. EvoScientist adds memory
middleware that injects memory into prompts and extracts user profile,
preferences, learned preferences, and experiment conclusions into Markdown.

Gap for Novi:

That is not enough for reliable scientific discovery memory. Novi needs memory
that can distinguish:

- user/project preferences;
- procedural know-how;
- research claims;
- hypotheses;
- experimental results;
- negative results;
- contradictions;
- superseded findings;
- reusable workflows;
- evidence artifacts.

The durable unit should not simply be "remembered text." It should be a
reviewable claim or procedure with evidence, provenance, confidence, scope,
status, and supersession history.

## Novi's Different Bet

Proposal:

Novi should not compete with DeepAgents as an execution harness. It should
compile Novi-owned state into DeepAgents-compatible execution when useful, then
bring outputs back into Novi-owned records.

The boundary should be:

```text
Novi Core
  owns AgentProfile, WorkflowSpec, RunLedger, ToolRuntime, ArtifactStore,
  ContributionLedger, MemoryReview, Policy, ContextPack

DeepAgents/LangGraph
  executes model/tool loops, subagent tasks, filesystem working memory,
  interrupts, streaming, checkpoints, and summarization
```

DeepAgents checkpoints are execution recovery state, not Novi's run ledger.
DeepAgents filesystem is working memory, not Novi's artifact store. DeepAgents
memory may help execution, but cannot directly commit Novi long-term memory.

## Integrated Exploration Proposition

Open:

The earlier narrow validation slice was:

```text
import knowledge
-> run agent
-> produce evidence-backed memory candidates and workflow patch
-> user review/merge
-> next run consumes accepted records
```

The user believes this is too narrow because the foundational features are
mutually dependent. Multi-agent configuration, workflow iteration,
collaboration, and scientific memory are not independent later layers; they
shape each other.

Reframed proposition:

Novi should validate all four foundations together, but with one thin,
inspectable capability in each foundation:

1. Agent profiles: one configurable primary agent plus one reviewer/auditor or
   specialist, with prompts, tools, permissions, model profile, and output
   schema recorded.
2. Workflow records: one generated workflow with steps, success signals,
   iteration triggers, and a patch mechanism.
3. Contribution ledger: one imported knowledge contribution and one user or
   reviewer decision that can merge or reject agent-produced changes.
4. Scientific memory: one accepted or rejected evidence-backed claim/procedure
   generated from the run.

The scope is broader than a single import-memory loop, but still controlled
because every part is shallow, recorded, and inspectable.

## Control Rules To Avoid Scope Collapse

Decision candidate:

The integrated exploration should proceed only if these invariants hold:

- Every autonomous action belongs to a run or assignment.
- Every meaningful output becomes an artifact, contribution, workflow patch,
  memory candidate, tool call, model call, or event.
- Agents cannot directly mutate accepted project memory, accepted workflow
  versions, or shared knowledge stores.
- Agent-generated workflow changes are patches, not silent edits.
- User imports become artifacts plus extracted candidates, not direct memory.
- Direct DeepAgents sessions can produce contributions, but they do not become
  Novi source of truth without review.
- Multi-user collaboration starts with identity, comments, review, and merge
  decisions, not realtime editing.
- Tool calls from DeepAgents, MCP, browser, shell, workers, or channels pass
  through Novi ToolRuntime or an explicitly equivalent policy/audit boundary.
- Scientific memory references evidence artifacts and records confidence,
  scope, review status, and supersession.
- LangGraph checkpoints can be linked from runs, but never replace run records.

## Proposed Exploration Loop

Proposal:

An integrated exploration run should eventually look like this:

```text
1. User imports knowledge, notes, paper snippets, prior experiment logs, or
   direct guidance.
2. Novi records the import as an artifact and contribution.
3. Novi selects or compiles agent profiles into the execution kernel.
4. Agent creates or updates a WorkflowSpec.
5. Agent executes one or more workflow steps through Novi-scoped tools.
6. Agent may ask the user for clarification or propose workflow changes.
7. Agent produces artifacts, claim candidates, memory candidates, and workflow
   patches.
8. Reviewer/user accepts, rejects, or requests changes.
9. Accepted memory and workflow revisions become available to the next run.
10. `novi run inspect` can explain the whole path.
```

This loop keeps the larger ambition intact while forcing every state transition
through inspectable records.

## Candidate New Objects

Open:

These objects may be needed beyond the current v0 data model:

- `AgentProfile`: project-local agent definition with prompt refs, tool scope,
  permission scope, model profile, interface mode, output schema, and policies.
- `KernelAgentBinding`: compiled representation of an agent for DeepAgents,
  LangGraph, Codex, Claude Code, or another kernel/worker.
- `WorkflowSpec`: versioned workflow with steps, success signals, agent
  assignments, required artifacts, tool requirements, and iteration triggers.
- `WorkflowPatch`: proposed change to a workflow, with reason, evidence refs,
  proposer, and review state.
- `Contribution`: imported or generated change proposal against project state.
- `KnowledgeImport`: source artifact plus extraction state for user-provided
  documents, notes, logs, or direct agent-session exports.
- `KnowledgeVault`: an external or local layered Markdown knowledge base with
  backlinks, raw inputs, analysis notes, accepted conclusions, indexes, and
  syntheses.
- `KnowledgeLayer`: raw input, excerpt, analysis, accepted conclusion, index,
  or synthesis.
- `SessionMemory`: file-backed mid-term memory for a long-running agent session
  or workflow execution.
- `MemoryManager`: an agent or external system that proposes updates to the
  knowledge vault, workflows, prompts, or skills without silently committing
  them.
- `AgentAuthorityLevel`: collaborator, reviewer/auditor, or executor.
- `ClaimCandidate`: scientific claim extracted from evidence before it becomes
  memory.
- `MemoryRecord`: accepted durable memory or knowledge contribution with type,
  layer, evidence refs, scope, confidence, review decision, backlinks, and
  supersession history. It may be stored in Novi directly or in an external
  Markdown knowledge vault adapter.

These should not all be implemented at once. The exploration track should first
test whether their boundaries are real and whether existing `RunSpec`,
`ArtifactRecord`, `MemoryCandidate`, and `EventRecord` can absorb some of them.

## Roadmap Implication

Proposal:

Do not force a strictly serial roadmap where research, collaboration, and memory
arrive as isolated phases. After Phase 1, add an integrated exploration track
that advances configurable agents, workflow iteration, contribution review, and
scientific memory together through one controlled loop.

This does not mean building the full platform at once. It means each phase
should preserve the common loop:

```text
agent/workflow/collaboration/memory are advanced together,
but each only crosses one small, inspectable boundary at a time.
```

## Open Questions

Open:

1. Which object should be the primary user-facing container for autonomous work:
   session, run, workflow, or assignment?
2. Should workflow versions be global project objects, session-scoped objects,
   or artifacts promoted through review?
3. How should a direct DeepAgents session be imported: full transcript,
   artifacts only, generated contribution bundle, or all three?
4. What is the minimum scientific memory schema that can represent negative
   results and contradictions without becoming a full knowledge graph too early?
5. What merge model is enough for Phase 2 exploration: append-only review
   decisions, patch files, git-backed diffs, or object-level merge records?
6. Which DeepAgents built-ins should be enabled first once Novi can audit them:
   filesystem write/edit, todo management, subagent `task`, shell execute, or
   memory?
7. What is the smallest evaluation that would show Novi is supporting real
   scientific discovery rather than just organizing agent transcripts?
