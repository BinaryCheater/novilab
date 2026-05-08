# Novi Lab

Novi Lab is a local-first, skill-first control plane for research work. It keeps sessions, runs, workflows, tools, artifacts, memory proposals, model calls, and review decisions in inspectable project-local records.

Novi is not a replacement for Codex, Claude Code, DeepAgents, or other execution agents. Those systems can be used as workers or kernels. Novi owns the project state, audit trail, workflow records, tool policy, and review boundary.

## Start Here

- [Chinese README](README.zh.md)
- [User Guide](docs/guide/README.md)
- [Quick Start](docs/guide/quick-start.md)
- [Core Concepts](docs/guide/concepts.md)
- [CLI Reference](docs/guide/cli.md)
- [Workflow Model](docs/guide/workflows.md)
- [Research Loop](docs/guide/research-loop.md)
- [Research Iteration](docs/guide/research-iteration.md)
- [Document Ingest](docs/guide/document-ingest.md)
- [Review And Artifacts](docs/guide/review-and-artifacts.md)
- [Configuration](docs/guide/configuration.md)
- [YAML Configuration](docs/guide/yaml-config.md)
- [Troubleshooting](docs/guide/troubleshooting.md)

## Current Shape

The current prototype can:

- initialize a local `.novi/` workspace;
- configure OpenAI-compatible chat models and LiteLLM proxy gateways;
- run session-aware `ask`, `run`, and `task` commands;
- execute through a deterministic local kernel or optional DeepAgents kernel;
- archive prompt packs, model messages, model calls, tool calls, traces, and artifacts;
- run resumable task workflows with step contracts and expected outputs;
- expose thin auditable tools (filesystem, shell, web, git, artifact);
- scaffold experiment directories (`novi experiment init`);
- inject nonblocking human guidance via `task note` and `task amend`;
- watch live run progress with `novi watch --follow`;
- ingest documents into reviewable proposals;
- review, check, and accept document patch contributions.

The most useful current loop is:

```bash
novi init
novi configure model siliconflow --model "..." --api-key "..."
novi task "research objective" --workflow research-iteration --kernel deepagents --rounds 1
novi trace latest
novi output latest
novi artifact list
```

## Documentation Map

- `docs/guide/`: user-facing explanation and operating docs.
- `docs/spec/`: accepted English working specs.
- `docs/spec_zh/`: Chinese specs kept aligned with the English specs.
- `docs/plans/`: implementation plans for specific development slices.
- `docs/impl/`: implementation notes and development records.

The root README is an orientation document. It should not be used as a development log.

## Development

Use `uv` for the Python environment:

```bash
uv sync --extra dev --extra deepagents
uv run --extra dev pytest
```

During development, prefer the console script entrypoint:

```bash
uv run --extra dev --extra deepagents novi --help
```

## Repository Policy

- Do not push directly to remote `main`.
- Changes intended for `main` should go through a pull request.
- Keep user-facing docs in `docs/guide/`.
- Keep development notes in `docs/impl/`.
- Keep specs in `docs/spec/` and `docs/spec_zh/` aligned when a spec change is explicitly approved.
