# 2026-05-01 CLI Convergence Mainline

## Context

The current product direction has four practical user modes:

- ingest collaborator/user documents into an ordinary Markdown knowledge library;
- run skill-driven research agents against sessions, runs, tools, artifacts, and accepted knowledge;
- let agents reflect on workflow/skill/document organization and propose changes;
- keep humans focused on goals, conversations, top-level files, and review decisions rather than low-level contribution ids.

The CLI must therefore expose a simple mainline while keeping inspectable lower-level records.

## Current Mainline

Primary commands:

```text
novi init
novi configure model ...
novi ingest docs... --hint "..."
novi task "..."
novi review --check
novi accept latest
novi accept all
novi trace latest
novi output latest
```

Lower-level commands remain available for debugging and audit:

```text
novi contribution inspect/check/accept ...
novi run inspect/prompt/output/trace ...
novi artifact show ...
novi workflow show ...
```

## Implemented In This Step

- Added top-level `novi accept latest|all|<contribution_id>`.
- Added `novi review --check` to run patch applicability checks while reviewing pending contributions.
- Added `novi task "..."` as the first research task entrypoint. It creates a session if needed, starts a research run, appends session messages, and prints next inspection commands.
- Added `novi trace [latest|run_id]` and `novi output [latest|run_id]` as top-level aliases.
- Promoted task into a durable object under `.novi/tasks/task_.../task.yaml`.
- Added default `research-loop` and `reflection-loop` WorkflowSpecs.
- Added `novi task list`, `novi task inspect <task_id>`, `novi task continue <task_id>`, and `novi task close <task_id>`.
- Added `--task task_...` to `ingest`/`process` so document processing runs can attach to an existing task.
- Added task-scoped review gates: `novi task continue <task_id>` blocks when pending task contributions exist, while `novi review --task <task_id> --check` and `novi accept all --task <task_id>` operate on that task's queue.

## Still Open

- Agent reviewer: a reviewer agent should be able to pre-check proposals and mark which are safe for automatic acceptance.
- Batch policy: `accept all --task` is scoped, but still trusts the human command. A future policy layer should distinguish safe patch batches from knowledge imports or risky changes.
- Task loop: `novi task continue` can append runs to a task, but it is still manually invoked. It should grow into a policy-controlled loop with checkpoints, generated artifacts, follow-up ingest, and reflection proposals.
- Tool-use library integration: ingest currently gives a bounded library context in the prompt. Later it should expose controlled search/read tools over `.novi/knowledge`.
- TUI/WebUI: not yet appropriate as a source of truth, but the CLI now exposes the stable surfaces that a TUI can wrap first: task, ingest, review, accept, trace, output.
