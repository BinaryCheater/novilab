# Roadmap Draft

Status: Draft

This roadmap is a development-check draft, not a delivery commitment. It shows how Novi can grow from a local core loop into research, multi-human project collaboration, cowork, memory, UI, MCP, and physical-AI modules.

Each phase can be used as a development checklist:

- `Entry check`: conditions that should hold before starting the phase.
- `Build check`: capabilities to implement or validate.
- `Acceptance check`: signals that the phase is usable.
- `Defer`: items intentionally left out of the phase.

## Roadmap Principles

Proposal:

- Establish Novi's own state and audit boundaries before integrating complex external frameworks.
- Make work inspectable before making it autonomous.
- Start local-first before remote/team collaboration.
- Support clear human participants, permissions, and attribution before more complex worker collaboration.
- Record and approve before expanding tool permissions.
- Keep modules replaceable before choosing providers.

## Phase 0: Spec Convergence

Goal: make product boundaries, feature surface, and technical candidates clear enough to start the smallest core.

Entry check:

- [ ] Bootstrap and technical tooling background docs have been read.
- [ ] Novi is confirmed not to be robot-first, multi-agent-first, or a Codex replacement.
- [ ] Novi core is confirmed to own sessions, runs, tools, artifacts, memory flow, policy, and audit.

Build check:

- [ ] `architecture.md` describes core concepts and boundaries.
- [ ] `tooling-and-modules.md` describes candidate modules, external projects, and integration boundaries.
- [ ] `features.md` lists core/early/next/later features.
- [ ] `roadmap.md` works as a development checklist.
- [ ] `open-questions.md` collects unresolved decisions.
- [ ] English and Chinese specs are roughly aligned.

Acceptance check:

- [ ] Novi's one-sentence positioning can be explained.
- [ ] The v0 reasons for not depending on ROS/MCP/Web dashboard/complex multi-agent graph can be explained.
- [ ] Codex/Claude/OpenHands can be explained as workers, not Novi source of truth.
- [ ] Multiple human project participants and agent participants can be distinguished.

Defer:

- [ ] No concrete file layout.
- [ ] No detailed data models.
- [ ] No memory internals.
- [ ] No full CLI command set.
- [ ] No delivery dates.

## Phase 1: Local Core Loop

Goal: create, execute, record, and inspect one local run without depending on a complex external agent framework.

Entry check:

- [ ] Phase 0 boundaries are acceptable.
- [ ] Local-first is the starting point.
- [ ] CLI is the first control surface.
- [ ] Simple Kernel or an equivalent fallback exists.

Build check:

- [ ] Project init creates a local Novi workspace.
- [ ] Skill registry discovers and lists `SKILL.md`.
- [ ] Sessions can be created, opened, listed, and summarized.
- [ ] Runs can be created, updated, completed, and failed.
- [ ] Run ledger records append-only events.
- [ ] Tool call log is separate from general events.
- [ ] Artifact store registers local outputs.
- [ ] Tool registry lists local tools.
- [ ] Policy/approval can at least express require approval / blocked.
- [ ] Context pack can be generated and saved.
- [ ] CLI can inspect project/session/run/tool/artifact.
- [ ] Simple Kernel can emit deterministic run events.

Acceptance check:

- [ ] User can run the minimum loop: init, skill list, session create, run start, run inspect.
- [ ] A run's objective, status, events, tool calls, and artifacts can be viewed.
- [ ] User can explain what happened, why, and where outputs live.
- [ ] High-risk or unauthorized tools cannot bypass policy.
- [ ] Core records can be validated without a real LLM.

Defer:

- [ ] No real robot integration.
- [ ] No full memory system.
- [ ] No TUI/Web.
- [ ] DeepAgents/LangGraph integration not required yet.
- [ ] No complex permission matrix.

## Phase 2: Research And Deep Research

Goal: make Novi useful for real research tasks that produce traceable sources, evidence tables, reports, and artifacts.

Entry check:

- [ ] Phase 1 run ledger, artifact store, and tool runtime are usable.
- [ ] Search/web/pdf/browser risk boundaries are in the tooling spec.
- [ ] First search approach is chosen: hosted provider, self-hosted provider, or stub.

Build check:

- [ ] `search.query` returns candidate sources and saves a search result artifact.
- [ ] `web.fetch` saves HTML/text artifacts.
- [ ] `pdf.parse` or document parser extracts paper/report text.
- [ ] `source.extract` extracts metadata, citation, claim, or quote.
- [ ] Research run can generate an evidence table.
- [ ] Research run can generate a synthesis report.
- [ ] Important report claims link to source artifacts.
- [ ] DeepAgents/LangGraph kernel adapter can be integrated as the serious kernel candidate.
- [ ] DeepAgents tools are wrapped through Novi Tool Runtime.
- [ ] Browser automation entry criteria are clear even if not implemented.

Acceptance check:

- [ ] User can start a research/deep-research run.
- [ ] Run produces sources, evidence table, report, and artifacts.
- [ ] Provider replacement remains possible.
- [ ] Important pages/PDFs/browser results can be inspected later.
- [ ] Deep research is not an external black box; output enters Novi audit/artifact flow.

Defer:

- [ ] Full browser automation not required.
- [ ] Research conclusions are not automatically written to memory.
- [ ] No multi-user collaboration UI required.
- [ ] Paid/login/high-frequency crawling policies are not fully solved, only bounded.

## Phase 3: Project Collaboration And Cowork

Goal: support multiple human participants in one project and assign scoped work to human participants or external workers.

Entry check:

- [ ] Sessions/runs/artifacts can express owner/reviewer concepts.
- [ ] Events can record actor attribution.
- [ ] Basic policy/approval states exist.
- [ ] Codex/Claude/OpenHands collaboration is confirmed as skills plus worker adapters.

Build check:

- [ ] Project participants can be added, listed, disabled, or marked inactive.
- [ ] Participant has identity, display name, and role.
- [ ] Project/session/run/artifact/memory candidate can record owner/reviewer.
- [ ] Comments can attach to run, artifact, tool call, memory candidate, assignment.
- [ ] Review state supports pending/requested_changes/approved/rejected.
- [ ] Approval is attributable to a specific human participant.
- [ ] Cowork assignment can be created, listed, inspected, accepted, and rejected.
- [ ] Assignment has assignee, task, context scope, status, and result refs.
- [ ] Human review/approval flow works.
- [ ] Coding worker adapter boundaries are clear: context, workspace/tool scope, diff/log capture.
- [ ] Worker output can be registered as artifact/event/comment/decision.
- [ ] External worker session/log is not Novi source of truth.

Acceptance check:

- [ ] A project can have multiple identifiable human participants.
- [ ] Different participants can own different review/approval responsibilities.
- [ ] User can see who created, approved, commented on, accepted, or rejected an action.
- [ ] User can assign review/coding/research subtasks and inspect results.
- [ ] Codex/Claude/OpenHands output can be reviewed instead of automatically becoming fact.

Defer:

- [ ] No full organization/team management.
- [ ] No SSO.
- [ ] No complex realtime collaborative editing.
- [ ] No full notification system, only notification event/interface boundary.
- [ ] No agent-to-agent chat as a core product surface.

## Phase 4: Memory Review

Goal: build the evidence-based memory loop so durable knowledge is reviewable, traceable, and correctable.

Entry check:

- [ ] Run/artifact/source refs are stable.
- [ ] Comments/review state/actor attribution have a basic shape.
- [ ] Memory types and write rules have been discussed separately.

Build check:

- [ ] Agent/kernel/worker can propose memory candidates.
- [ ] Memory candidate includes claim, scope, confidence, evidence refs.
- [ ] Memory review queue can list pending candidates.
- [ ] Human participant can accept/reject/request changes.
- [ ] Accepted memory writes to project/session/episodic/procedural store.
- [ ] Rejected/superseded memory keeps decision record.
- [ ] Memory search can retrieve accepted memory.
- [ ] Memory references evidence instead of copying large artifacts.
- [ ] Memory writes enter run/session audit.

Acceptance check:

- [ ] Agents cannot directly write long-term memory.
- [ ] Each durable memory traces back to evidence/run/artifact.
- [ ] Users can review, accept, reject, and revise memory.
- [ ] Stale or superseded memory does not silently overwrite evidence.

Defer:

- [ ] Vector retrieval not required initially.
- [ ] No complex knowledge graph.
- [ ] No automatic long-term memory.
- [ ] No cross-project global memory merge.

## Phase 5: Stronger Control Surfaces

Goal: improve operation and visibility for approvals, reviews, cowork, and artifacts after CLI stabilizes.

Entry check:

- [ ] CLI inspect can explain core state.
- [ ] Run events/tool calls/artifacts/comments/review state are stable.
- [ ] Highest-friction operations are known.

Build check:

- [ ] TUI or enhanced CLI can show run timeline.
- [ ] Tool call table is viewable.
- [ ] Approval queue is viewable.
- [ ] Cowork assignments are viewable.
- [ ] Comments/review state are viewable.
- [ ] Artifact tree is browsable.
- [ ] Memory candidates are viewable.
- [ ] Web/API boundary is clear: surface, not duplicated core state.
- [ ] Channel adapter boundary is clear: ask/status/inspect/approve/enqueue.

Acceptance check:

- [ ] User does not need raw JSONL to understand current state.
- [ ] Approvals, comments, and cowork assignments have one clear entry point.
- [ ] UI and CLI actions enter the same core API/audit path.
- [ ] IM/channel does not directly execute high-risk actions.

Defer:

- [ ] No full production dashboard.
- [ ] No complex team permission admin.
- [ ] No multi-tenancy.
- [ ] No mobile UX.

## Phase 6: External Ecosystem

Goal: connect Novi to more tool ecosystems while preserving policy, audit, and source-of-truth boundaries.

Entry check:

- [ ] Tool Runtime and Policy Gate are stable.
- [ ] Module boundary is stable.
- [ ] External tool output can become artifact/event records.

Build check:

- [ ] MCP client can map external tools/resources into Novi.
- [ ] MCP calls go through Novi policy, approval, and audit.
- [ ] Coding worker category is replaceable.
- [ ] Observability records traces, latency, LLM/tool metadata.
- [ ] Traces do not replace run ledger.
- [ ] Plugin/module packaging boundary is clear.
- [ ] MCP server entry decision is made.

Acceptance check:

- [ ] External tools/resources can be called safely through Novi.
- [ ] External worker/provider can be replaced.
- [ ] Debug data is enough to locate model, tool, context, or policy issues.
- [ ] Novi source of truth remains core records.

Defer:

- [ ] No full plugin marketplace.
- [ ] No full MCP server unless API/records are stable.
- [ ] Langfuse/LangSmith/Phoenix are not treated as run ledger.

## Phase 7: Physical-AI Modules

Goal: integrate physical-AI modules after core audit, permissions, cowork, research, and artifact capabilities stabilize.

Entry check:

- [ ] High-risk tool policy is usable.
- [ ] Approval/preflight/audit is usable.
- [ ] Artifact store can handle logs, configs, metrics, videos, and similar outputs.
- [ ] Simulation/training/dataset/evaluation/ROS ordering has been chosen.

Build check:

- [ ] Simulation module records scene/config/result artifacts.
- [ ] Training module records job, metrics, checkpoints, budget.
- [ ] Dataset module records hash, lineage, version.
- [ ] Evaluation module records metrics/report.
- [ ] Multimodal logging can register video, trajectory, Rerun/rosbag artifacts.
- [ ] ROS module exists only as an adapter.
- [ ] Real robot action requires allowlist, preflight, approval, strong audit.
- [ ] Sim-first or dry-run-first policy is clear.

Acceptance check:

- [ ] Sim/training/dataset/eval can run as Novi modules.
- [ ] Real robot actions cannot bypass policy.
- [ ] ROS is not Novi's base layer.
- [ ] Physical-AI outputs can be referenced by artifacts, memory, and audit.

Defer:

- [ ] No fleet robotics control.
- [ ] No robot-first runtime.
- [ ] No unapproved real robot execution.
- [ ] No replacement for a full experiment platform.

## Cross-Phase Development Checks

Review these every time a capability is added:

- [ ] Does the new capability enter Novi Tool Runtime or an equivalent controlled boundary?
- [ ] Are actor, time, input, output, and policy decision recorded?
- [ ] Is it inspectable?
- [ ] Is it replayable or at least explainable?
- [ ] Does it produce an artifact or event?
- [ ] Could it write memory? If yes, does it only produce a candidate?
- [ ] Does it introduce a new permission?
- [ ] Does it introduce an external source of truth? If yes, is it demoted to adapter?
- [ ] Does it preserve local-first operation?
- [ ] Does it make a provider/framework hard to replace?

## Open Decisions

Open:

1. Should multiple human project participants come before or after research/deep-research?
2. Should memory review be discussed in parallel with cowork, or after research runs stabilize?
3. Should browser automation enter Phase 2, or wait until after stronger control surfaces?
4. Should coding worker be the first real worker adapter, or should human review/approval come first?
5. What order should simulation, training, dataset, evaluation, and ROS take within Physical-AI?
