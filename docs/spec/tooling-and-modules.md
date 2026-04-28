# Tooling And Modules Spec

Status: Draft

This spec discusses candidate tools and module boundaries. It is not an implementation plan, file layout, data model, or milestone schedule.

## Purpose

Proposal:

Novi should be built as a platform core with replaceable execution kernels and optional modules.

The platform core should own:

- skills;
- sessions;
- runs;
- context;
- tool registry and policy;
- artifacts;
- memory flow;
- approvals;
- audit state.

External tools and frameworks should provide execution or integration capability, but should not become the source of truth for Novi state.

## Selection Principles

Proposal:

Choose tools that:

- fit local-first research, coding, training, simulation, and physical-AI workflows;
- can be wrapped behind Novi-owned interfaces;
- support inspection, approval, audit, and replay;
- do not force Novi into a single vendor, model, framework, or runtime;
- can start simple and be replaced later.

Avoid tools that require Novi to give up ownership of sessions, runs, memory, artifacts, permissions, or policy.

## Core Language Direction

Proposal:

Python should be the first core runtime because the expected domains include research, ML, robotics, simulation, training, scientific Python, ROS, and local automation.

TypeScript can still be useful later for:

- web control plane;
- browser-heavy modules;
- Pi or other TypeScript-native agent kernels;
- frontend tooling.

This is a runtime preference, not a permanent product constraint.

## Agent Kernel Candidates

Proposal:

Novi should define an adapter boundary for agent kernels. A kernel may execute a run, stream events, request tools, pause for approval, and resume work. It should not own Novi records.

### DeepAgents + LangGraph

Recommended candidate for the first serious research/experiment kernel.

Useful for:

- complex multi-step tasks;
- planning and task decomposition;
- context management through working files;
- subagents for context isolation;
- human-in-the-loop approval flows;
- durable execution and resume through LangGraph;
- model-provider flexibility.

Boundary:

- DeepAgents subagents are execution-level helpers, not automatically Novi platform agents.
- DeepAgents tools should be wrappers around Novi Tool Runtime.
- DeepAgents memory or filesystem state should not directly become Novi long-term memory or artifacts without Novi review/registration.

### Simple Kernel

Recommended as a minimal fallback and test kernel.

Useful for:

- running the core loop without external agent frameworks;
- deterministic tests;
- validating sessions, runs, tool policy, artifacts, and inspection;
- avoiding early lock-in.

### Pi Agent Core

Potential later spike for interactive local coding-agent-like workflows.

Useful for:

- local interactive agent experience;
- embedded coding-style sessions;
- TypeScript-side experiments.

Boundary:

- treat Pi session state as execution state, not Novi source of truth;
- route tool calls through Novi Tool Runtime;
- do not make Pi the default foundation before it proves stable for Novi's needs.

### Codex, Claude Code, OpenHands

Treat as external coding workers rather than Novi's core runtime.

Useful for:

- implementation tasks;
- refactors;
- code review;
- tests and patch generation.

Boundary:

- Novi creates and audits a coding run;
- the worker produces diffs, logs, and artifacts;
- Novi records the result, policy decisions, and memory candidates.

## Tool And Module Groups

Proposal:

Modules should expose tools, resources, observations, artifacts, and policies. The first module discussions should focus on boundaries rather than implementation details.

### Local Project Modules

Candidate modules:

- filesystem;
- git;
- shell sandbox;
- python execution;
- notebook execution.

These are important because they support local-first work and coding/research workflows. They also carry real risk, so they should be policy-gated.

### Research Modules

Candidate modules:

- search;
- web fetch;
- browser automation;
- PDF/document parsing;
- citation and source extraction.

Hosted search can be useful early, but self-hosted or replaceable search should remain possible.

### MCP Modules

MCP should be treated as an external tool/resource adapter, not the foundation of Novi.

Early direction:

- add MCP client later when the core tool runtime is stable;
- wrap MCP tools through Novi policy, approval, and audit;
- consider MCP server support only after Novi records and APIs are stable.

### Coding Worker Modules

Candidate workers:

- Codex;
- Claude Code;
- OpenHands.

These should be modeled as external workers that operate inside a Novi run, not as replacements for Novi control-plane state.

### Physical-AI Modules

Candidate modules:

- ROS;
- simulation;
- training;
- dataset;
- evaluation;
- Rerun or multimodal logging.

These should stay modular. Novi should not become robot-first or make ROS the base layer.

## Deferred Areas

Deferred:

- detailed file structure;
- concrete data models;
- milestone plan;
- memory system design;
- TUI design;
- chat channel integration;
- plugin marketplace;
- full MCP server;
- robotics execution policy.

These areas are real, but they should be specified separately.

## Open Questions

Open:

1. Should DeepAgents + LangGraph be the first real kernel, with Simple Kernel as the initial validation path?
2. Which local project modules are required before the first useful demo?
3. Should hosted search be accepted for early research runs, or should search start as a stub/local adapter?
4. How should Codex/Claude/OpenHands workers be represented: module, tool, kernel, or worker category?
5. Which physical-AI module should be discussed first: simulation, training, dataset, ROS, or evaluation?
