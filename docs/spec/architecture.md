# Architecture Spec

Status: Draft

## Positioning

Proposal:

Novi Lab is a skill-first, session-aware control plane. It coordinates research, coding, experiments, simulation, training, memory, artifacts, audit, and optional physical-AI integrations.

Novi is not primarily:

- a multi-agent framework;
- a robot runtime;
- a ROS wrapper;
- an OpenClaw clone;
- a Codex or Claude Code replacement.

This does not mean Novi is single-agent. Novi should be multi-agent-capable when different agents are useful for different purposes, permissions, tool sets, context scopes, execution environments, or audit requirements.

## Core System

Proposal:

```text
Novi Core
  = sessions
  + skills
  + tools
  + runs
  + memory
  + artifacts
  + policies
  + context
```

External systems are modules or adapters:

```text
ROS
Isaac Sim
LeRobot
Codex
Claude Code
MCP servers
search/browser services
training systems
IM channels
observability tools
```

## Core Responsibilities

Novi Core owns:

- session state;
- run creation and inspection;
- skill loading and activation;
- context pack generation;
- tool registry and execution lifecycle;
- policy checks and approvals;
- event logs and run ledgers;
- artifact records;
- memory candidates and review state.

Modules provide:

- tools;
- resources;
- observations;
- artifact types;
- policy contributions;
- optional hooks.

## Primary Concepts

### Skill

A reusable workflow package. A skill may contain instructions, examples, schemas, references, scripts, assets, policies, evals, and hooks.

Novi should remain compatible with the common `SKILL.md` convention and should not require Novi-specific metadata for a skill to load.

### Session

A long-lived working context. A session is not only chat history. It contains active goals, selected skills, summaries, runs, artifacts, memory candidates, approvals, and channel bindings.

### Run

One auditable execution inside a session. Runs are the primary unit of execution, replay, evidence, and inspection.

### Tool

A callable capability exposed by a module. Visibility, callability, executability, automation, and memory-write permission are separate concerns.

### Memory

Reviewable knowledge derived from evidence. Long-term memory should be proposed, checked, and accepted rather than directly written by the main agent.

### Artifact

A durable output or evidence item produced or referenced by a run. Memory should point to artifacts instead of embedding large content.

## Multi-Agent Support

Proposal:

Novi should support multiple agents as participants in a session or run, without making multi-agent orchestration the product center.

Agent boundaries are justified when they separate:

- purpose or responsibility;
- model profile;
- context scope;
- tool scope;
- permission scope;
- execution environment;
- output schema;
- safety or audit requirements.

An agent is an execution participant, not the top-level unit of work. The top-level units remain sessions and runs.

Each run should be able to record:

- which agents participated;
- what role each agent had;
- what tools each agent could see or call;
- what context each agent received;
- what policy and approval constraints applied;
- which events, tool calls, artifacts, and memory candidates each agent produced.

V0 does not need a complex agent graph or free-form agent-to-agent chat. It should still keep the data model compatible with multiple agents.

## V0 Agents

Proposal:

V0 should assume two initial agent roles conceptually:

- Orchestrator: handles dialogue, skill selection, run planning, tool calls, summaries, and memory candidate proposals.
- Auditor: checks tool calls, memory candidates, run completeness, evidence, and spec drift.

The first implementation may stub or simplify the auditor, but the data model should leave room for agent participants and audit records.

## Context Model

Proposal:

Context should be compiled explicitly. A model call should receive a `ContextPack`, not a blind append of all prior messages.

Recommended context layers:

- global rules;
- project spec;
- session summary;
- current run state;
- active skill instructions;
- relevant memory;
- selected artifacts;
- available tools.

Raw old messages, large logs, and unverified memory should be excluded by default.

## Storage Direction

Proposal:

V0 should be local-first:

- filesystem for sessions, runs, skills, artifacts, and summaries;
- JSONL for append-only events and tool calls;
- Markdown for editable summaries and project memory;
- SQLite optionally for indexes and queryable metadata.

SQLite is useful, but the filesystem records should remain understandable without a database.
