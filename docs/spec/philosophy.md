# Philosophy Spec

Status: Draft, user-approved addition

This document records the higher-level philosophy that should guide Novi Lab after the Phase 1 prototype. It does not replace the accepted v0 specs by itself. Instead, it explains why future implementation and spec revisions should move from an audit-first control plane toward a feedback-governed research agent system.

## Thesis

Proposal:

Novi Lab should be a local-first research agent operating system that improves a human researcher's ability to explore, test, and refine ideas over time.

The central problem is not how many agents Novi has, whether the topology is a workflow, subagent tree, swarm, or search tree, or whether the runtime is DeepAgents, LangGraph, Codex, Claude Code, or a custom harness. Those are execution topologies and implementation tools.

The deeper problem is:

- language models can mistake coherent explanation for real progress;
- complex research tasks have sparse and delayed rewards;
- an agent system without reliable intermediate feedback tends to optimize activity, polish, and narrative completeness instead of truth, novelty, reproducibility, and decision value.

Therefore, the next Novi architecture should be governed by two hard rules:

1. Confidence must not increase without new external feedback.
2. Long-running autonomy must have explicit rewards, proxy-risk checks, and stop conditions.

Models may generate hypotheses, plans, explanations, code drafts, and candidate interpretations. The harness must decide what counts as evidence, what may enter memory, when beliefs can change, when resources may be spent, when a direction should stop, and when a human or stronger model is required.

## Why This Matters

Proposal:

Research agents fail in a characteristic way: they keep making the story more coherent while losing contact with the world.

This failure can look productive:

- a concept gets a better name;
- a workflow gains more stages;
- agents produce more review notes;
- a report becomes more polished;
- reflection text sounds more careful;
- memory accumulates concise summaries;
- experiments run, but do not answer the decisive question.

None of these is necessarily progress. They are useful only when tied to external feedback or a decision that reduces uncertainty.

Novi should treat scientific and engineering progress as a state transition backed by evidence, not as better prose. The system should distinguish:

- idea: a possible direction;
- hypothesis: a falsifiable claim worth testing;
- belief: a current working judgment with uncertainty;
- evidence: external feedback from sources, code, data, experiment, benchmark, expert input, or observed failure;
- knowledge: a claim admitted into long-term memory under review rules;
- narrative: an explanatory frame that may help organize work but must not be confused with evidence.

## Anti-Coherence

Decision:

Novi should include anti-coherence mechanisms. Their job is to interrupt language self-consistency when it begins to masquerade as truth.

The system should ask at key points:

- Is this direction anchored on a user-provided term that may be wrong?
- Is a new name hiding an old or weak idea?
- Is this taxonomy necessary, or just making the discussion feel systematic?
- Did any external fact force a change in belief?
- Are we answering a question that should instead be rejected or reframed?
- Is the current action reducing uncertainty, or only adding activity?
- Is the agent repeating explanations that have not gained evidence?
- Should the direction be stopped, downgraded, or handed to a human reviewer?

Anti-coherence is not ordinary criticism. A critic can still produce plausible review text. Anti-coherence must be able to change control flow:

- continue;
- seek external feedback;
- run a sanity check;
- downgrade a claim;
- block memory write;
- switch to a stronger model;
- ask the user;
- stop or redirect the task.

## Reward Shaping

Decision:

Complex research has sparse rewards. Novi should define dense intermediate rewards for each workflow so the agent does not optimize activity volume.

Examples of positive reward signals:

- a relevant prior work cluster is found;
- a hypothesis is made falsifiable;
- a baseline is reproduced;
- a sanity run passes;
- a negative result invalidates a bad direction;
- an ablation supports a mechanism;
- multi-seed results are stable;
- an artifact can be traced to the command, data, and code that produced it;
- a claim is downgraded because new feedback contradicted it;
- a direction is stopped before wasting more budget.

Examples of proxy risks:

- confidence increases after only summarization or reflection;
- a report improves stylistically without new evidence;
- experiments run without a decision they can change;
- memory is written from narrative summary rather than evidence;
- an agent repeats the same plan after failure;
- a workflow expands because it looks rigorous, not because each step has decision value.

Workflows should declare both reward signals and proxy risks. The harness should use them for planning, stopping, model routing, and review.

## Harness Above Prompt

Decision:

Prompt instructions are necessary but insufficient. Anything that affects long-term state, confidence, memory, permissions, budget, or irreversible actions must be controlled by the harness.

The model should be responsible for:

- understanding tasks;
- generating candidates;
- local reasoning;
- writing;
- planning proposals;
- interpreting feedback;
- suggesting improvements;
- producing code drafts or coding briefs.

The harness should be responsible for:

- state management;
- context assembly;
- tool execution;
- permission boundaries;
- feedback capture;
- budget scheduling;
- model routing;
- failure recovery;
- memory write rules;
- claim and belief state;
- versioning;
- human checkpoints.

This is the main lesson from mature coding agents such as Claude Code, Codex, Aider, and OpenHands: useful autonomy happens inside a strong harness with files, diffs, shell commands, tests, permissions, user intervention, and task boundaries. Novi should bring the same discipline to research and experiment work.

## Core Objects

Proposal:

Future Novi design should promote the following objects alongside sessions, runs, skills, tools, memory, and artifacts.

### Claim

A statement being considered, tested, supported, weakened, or rejected.

Suggested fields:

- id;
- statement;
- scope;
- status: idea, hypothesis, working_belief, supported, contradicted, abandoned;
- confidence;
- uncertainty;
- evidence_refs;
- counterevidence_refs;
- created_by;
- updated_by;
- last_feedback_at.

### Feedback Event

An external signal that can affect a claim, plan, memory item, or workflow.

Examples:

- paper or source check;
- quote or source extraction;
- code execution result;
- experiment metric;
- benchmark result;
- failed command;
- test output;
- plot or dataset inspection;
- human correction;
- expert review;
- coding delegate result.

### Belief Update

A controlled state transition for a claim.

Rules:

- confidence cannot increase without at least one new feedback event;
- reflection alone can clarify uncertainty but cannot upgrade confidence;
- contradiction should create counterevidence, not be hidden inside summary prose;
- abandoned directions should remain searchable as negative memory when useful.

### Reward Signal

A workflow-local event that says whether a step made real progress, hit a proxy, or should stop.

### Narrative Check

A harness-controlled check that can interrupt current framing and force reframing, evidence gathering, downgrade, or stop.

### Improvement Candidate

A proposed change to an agent prompt, skill, workflow, model route, tool, memory rule, or coding delegate.

It should not be applied directly by the proposing model. It should enter an upgrade workflow.

## Memory Philosophy

Decision:

Memory is not a place to store polished summaries. Memory is a controlled interface between past evidence and future behavior.

Novi should separate memory types:

- hypothesis memory: plausible but unverified ideas;
- evidence memory: source-backed or result-backed facts;
- experiment memory: commands, configs, metrics, failures, and results;
- negative memory: disproven directions, failed tactics, and counterexamples;
- strategy memory: procedures that repeatedly worked under known conditions;
- agent memory: lessons about prompts, tools, model routes, and workflows;
- narrative memory: current framing, useful for orientation but not evidence.

Rules:

- evidence, experiment, negative, and strategy memory may affect future confidence;
- narrative memory may affect context but must not upgrade claims;
- memory writes should cite feedback events or artifacts;
- high-impact memory writes should pass a review gate;
- self-reflection can propose memory but should not directly become knowledge.

## Reflection And Self-Upgrade

Decision:

Agent reflection and self-upgrade should use three layers.

### Prompt Workflow

The prompt can ask the agent to notice possible improvements:

- what worked;
- what failed;
- uncertainty;
- possible memory;
- possible skill;
- possible prompt change;
- possible workflow change;
- possible model-routing change.

This is useful but non-authoritative.

### Hooks

Hooks should reliably trigger reflection candidates from system events:

- run ended;
- tool failed;
- the same failure repeated;
- user corrected an important claim;
- a claim was downgraded;
- a memory write was attempted;
- budget was exceeded;
- workflow stalled;
- coding delegate returned a patch or failure;
- external feedback contradicted the current narrative.

Hooks should create structured triggers, not silently change the agent.

### Explicit Upgrade Workflow

Any long-term change should go through an explicit workflow:

```text
trigger
→ collect evidence
→ diagnose pattern
→ propose change
→ validate on recent cases or a small benchmark
→ accept, reject, or revise
→ versioned write
```

This applies to system prompts, skills, memory, workflow definitions, model routes, tool permissions, and coding delegates.

## Model Routing

Proposal:

Novi should distinguish low-cost, strong, and coding-specialized model roles.

Low-cost models are appropriate for:

- formatting;
- summarization;
- log cleanup;
- source triage;
- first-pass extraction;
- simple classification;
- routine progress notes.

Strong models are appropriate for:

- narrative checks;
- belief updates;
- experiment design;
- failure attribution;
- deciding whether to stop;
- deciding whether memory can be upgraded;
- high-impact planning;
- conflict resolution.

Coding delegates such as Codex, Claude Code, Aider, or OpenHands are appropriate for:

- implementing experiments;
- fixing failing scripts;
- running tests;
- producing diffs;
- reproducing baselines;
- creating executable feedback.

LiteLLM is a good candidate for provider routing, fallback, and cost/performance management. Routing should be tied to decision risk, not only task length.

## Workflow And Topology

Proposal:

Workflow, subagents, swarms, and tree search should be treated as execution topologies.

Use fixed workflows for:

- known research stages;
- review gates;
- memory upgrades;
- belief updates;
- expensive actions;
- experiment lifecycle checkpoints.

Use subagents for:

- context isolation;
- role specialization;
- tool and permission separation;
- model separation;
- long-running task delegation.

Use swarms or broad parallelism for:

- independent literature search;
- candidate idea coverage;
- benchmark comparison;
- parameter or method exploration when tasks do not share state.

Use tree search for:

- code and experiment-space exploration;
- algorithm variants;
- multi-step plans where branch quality can be evaluated.

No topology should be trusted without feedback and reward definitions.

## Coding Delegates

Proposal:

Novi should be able to call mature coding agents rather than rely only on a research agent's own code-writing ability.

The main research agent should own the research question and interpretation. The coding delegate should own scoped implementation work:

- receive a coding brief;
- edit files or produce a patch;
- run commands or tests;
- report changed files, commands, outputs, and failures;
- return artifacts that become feedback events.

The coding delegate should not silently decide the research conclusion. It produces executable contact with the world. Novi then uses the results for belief updates, reward signals, and next-step decisions.

## Related Works

This section analyzes related systems as design evidence, not as templates to copy.

### DATAGEN

DATAGEN uses LangChain and LangGraph for a visible multi-agent data-analysis workflow. Its graph explicitly routes through agents such as hypothesis, process, visualization, code, search, report, quality review, note taking, and refinement.

Practical lesson:

- explicit graphs make workflow structure understandable;
- specialized agents help separate roles;
- quality review can be a node in the process.

Limitation for Novi:

- a visible graph alone does not solve belief calibration;
- quality review can still become language-only critique unless it changes control flow;
- the application is closer to a fixed data-analysis assistant than a feedback-governed research operating system.

Reference: [DATAGEN](https://github.com/starpig1129/DATAGEN)

### EvoScientist

EvoScientist is a DeepAgents-first research assistant. It builds a main DeepAgent with subagents, skills, memory, middleware, backends, LiteLLM-compatible model support, and optional async subagents hosted through `langgraph dev`.

Its research lifecycle is mostly prompt-driven: intake, plan, execute/debug, evaluate/iterate, write, and verify. Long-running subagents such as writing or data analysis can be deployed as LangGraph graphs and called asynchronously.

Practical lesson:

- DeepAgents is useful as a rich agent harness;
- skills and memory are necessary for complex research;
- async subagents are useful for long-running tasks;
- model routing, middleware, and backends are part of the real product, not peripheral details.

Limitation for Novi:

- prompt-driven workflow can still drift;
- memory and self-evolution need hard evidence rules;
- without explicit claim, feedback, reward, and narrative-control objects, a strong AI scientist assistant can still optimize coherent activity.

Reference: [EvoScientist](https://github.com/EvoScientist/EvoScientist)

### Auto-Research Systems

The broader auto-research landscape includes systems such as AI-Scientist, AI-Scientist-v2, RD-Agent, AutoResearchClaw, Agent Laboratory, AI-Researcher, Biomni, DeepScientist, InternAgent, and Karpathy's autoresearch.

Practical lesson:

- end-to-end research systems need literature review, ideation, coding, experiments, analysis, writing, and review;
- many use custom harnesses because research tasks require state, tools, code execution, and domain-specific feedback;
- coding agents are often critical infrastructure for the experiment stage;
- tree search, Docker isolation, git worktrees, benchmark loops, and report generation are recurring patterns.

Limitation for Novi:

- many systems optimize impressive end-to-end production but do not make belief state explicit;
- generated papers, reports, or experiments are not enough unless the system knows which claims were actually supported;
- Novi should learn from their toolchains without copying their product scope.

Reference: [Awesome Auto Research](https://github.com/handsome-rich/Awesome-Auto-Research-Tools)

### Coding Agents

Codex, Claude Code, Aider, OpenHands, and SWE-agent show that language models become more reliable when embedded in a harness with files, shell commands, diffs, tests, permissions, and user intervention.

Practical lesson:

- coding progress is easier to verify than research prose because tests, commands, and diffs provide dense feedback;
- a strong coding delegate can turn claims into executable checks;
- the harness should capture code changes and outputs as feedback events.

Limitation for Novi:

- coding agents do not solve research judgment by themselves;
- a passing test does not prove scientific importance;
- coding delegates should be scoped tools inside the research system, not the owner of research memory or conclusions.

References:

- [Aider](https://github.com/Aider-AI/aider)
- [OpenHands](https://github.com/All-Hands-AI/OpenHands)
- [SWE-agent](https://github.com/SWE-agent/SWE-agent)

### DeepAgents And LangGraph

DeepAgents provides a rich agent harness with planning, filesystem, subagents, skills, memory, permissions, and middleware. LangGraph provides stateful graph execution, checkpoints, interrupts, streaming, and deployed graph support.

Practical lesson:

- DeepAgents is a practical default for autonomous node execution;
- LangGraph is useful for explicit workflows and async/deployed graph execution;
- Novi does not need to choose one exclusively.

Recommended Novi interpretation:

- use DeepAgents for agent autonomy, tools, skills, memory, and subagent delegation;
- use LangGraph where explicit control flow, checkpoints, async jobs, or review gates matter;
- keep belief updates, memory writes, rewards, and irreversible actions above both frameworks in Novi-owned harness logic.

References:

- [DeepAgents documentation](https://docs.langchain.com/oss/python/deepagents/overview)
- [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)

## Product Consequences

Proposal:

Novi should not be merely another AI scientist assistant. It should be a feedback-governed research agent system.

This means:

- sessions and runs remain useful, but their main purpose is research state and feedback, not heavy audit;
- memory remains essential, but memory write rules must be evidence-based;
- skills remain essential, but they should include feedback expectations and failure modes;
- model routing should be explicit and risk-aware;
- coding delegates should be integrated as evidence-generating workers;
- workflow definitions should include rewards and proxy risks;
- agent self-upgrade should be versioned, validated, and reversible;
- narrative checks should be first-class control points.

The resulting system can still help the user do research directly. It also helps the user improve the agent system itself. These are not separate goals: better research agents require better feedback, memory, and upgrade mechanisms.

## Open Questions

Open:

- Which claim ledger schema is minimal enough for Phase 2 without becoming a heavy scientific database?
- Which hooks should be implemented first: run-end, tool-error, memory-write, user-correction, or claim-downgrade?
- Should narrative checks run on every workflow stage or only at gates that affect memory, confidence, budget, or direction?
- How should human feedback be represented: as ordinary feedback events, privileged review events, or both?
- What level of automatic agent self-upgrade is acceptable without explicit user approval?
- How should Codex, Claude Code, Aider, or OpenHands be integrated: shell delegate, MCP tool, or explicit cowork participant?
- Which rewards can be computed automatically, and which require model or human judgment?
