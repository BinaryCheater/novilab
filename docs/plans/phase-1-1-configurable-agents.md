# Phase 1.1 Configurable Agents Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build project-local agent definitions and simple sequential multi-agent runs that preserve Novi-owned run, artifact, memory, and audit records.

**Architecture:** Add a focused `agents.py` module for agent defaults, loading, creation, and snapshots. Extend the existing filesystem store and argparse CLI without introducing a framework dependency. Update the deterministic runner so selected agents execute as sequential recorded steps.

**Tech Stack:** Python 3.9+, argparse, PyYAML, pytest, local filesystem records under `.novi/`.

---

## File Structure

- `src/novi_lab/agents.py`: agent defaults, validation, loading, listing, creation, and snapshot helpers.
- `src/novi_lab/store.py`: initialize `.novi/agents/` and default agent records.
- `src/novi_lab/cli.py`: add `agent` commands and `run start --agent`.
- `src/novi_lab/runner.py`: accept selected agent ids, snapshot definitions, and write per-agent step artifacts/events.
- `tests/test_cli_core_loop.py`: end-to-end CLI tests for agent commands and selected multi-agent run records.
- `docs/impl/2026-04-29-phase-1-1-configurable-agents.md`: implementation decision record.

## Task 1: Agent Definitions

**Files:**
- Create: `src/novi_lab/agents.py`
- Modify: `src/novi_lab/store.py`
- Test: `tests/test_cli_core_loop.py`

- [ ] **Step 1: Write the failing test**

Add `test_init_creates_default_agent_definitions`:

```python
def test_init_creates_default_agent_definitions(tmp_path):
    result = run_cli(tmp_path, "init")

    assert result.returncode == 0, result.stderr
    agent_dir = tmp_path / ".novi" / "agents"
    assert (agent_dir / "agent_orchestrator.yaml").exists()
    assert (agent_dir / "agent_auditor.yaml").exists()
    assert "role: orchestrator" in (agent_dir / "agent_orchestrator.yaml").read_text()
    assert "role: auditor" in (agent_dir / "agent_auditor.yaml").read_text()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest tests/test_cli_core_loop.py::test_init_creates_default_agent_definitions -v`

Expected: FAIL because `.novi/agents/defaults` are not created yet.

- [ ] **Step 3: Implement minimal agent defaults**

Create `agents.py` with `default_agents()` and `write_default_agents(root)`. Modify `init_workspace()` to create `.novi/agents/` and write the default orchestrator/auditor definitions if missing.

- [ ] **Step 4: Run test to verify it passes**

Run: `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest tests/test_cli_core_loop.py::test_init_creates_default_agent_definitions -v`

Expected: PASS.

## Task 2: Agent CLI

**Files:**
- Modify: `src/novi_lab/agents.py`
- Modify: `src/novi_lab/cli.py`
- Test: `tests/test_cli_core_loop.py`

- [ ] **Step 1: Write the failing test**

Add `test_agent_create_list_and_show`:

```python
def test_agent_create_list_and_show(tmp_path):
    run_cli(tmp_path, "init")

    create_result = run_cli(tmp_path, "agent", "create", "agent_researcher", "--role", "researcher")
    list_result = run_cli(tmp_path, "agent", "list")
    show_result = run_cli(tmp_path, "agent", "show", "agent_researcher")

    assert create_result.returncode == 0, create_result.stderr
    assert "agent_researcher" in create_result.stdout
    assert list_result.returncode == 0, list_result.stderr
    assert "agent_orchestrator" in list_result.stdout
    assert "agent_researcher" in list_result.stdout
    assert show_result.returncode == 0, show_result.stderr
    assert "Role: researcher" in show_result.stdout
    assert "Tool scope:" in show_result.stdout
```

- [ ] **Step 2: Run test to verify it fails**

Run: `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest tests/test_cli_core_loop.py::test_agent_create_list_and_show -v`

Expected: FAIL because the `agent` command does not exist.

- [ ] **Step 3: Implement CLI and store helpers**

Add `create_agent`, `list_agents`, and `load_agent` helpers. Add argparse handlers for `novi agent create/list/show`.

- [ ] **Step 4: Run test to verify it passes**

Run: `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest tests/test_cli_core_loop.py::test_agent_create_list_and_show -v`

Expected: PASS.

## Task 3: Sequential Multi-Agent Run Records

**Files:**
- Modify: `src/novi_lab/runner.py`
- Modify: `src/novi_lab/cli.py`
- Test: `tests/test_cli_core_loop.py`

- [ ] **Step 1: Write the failing test**

Add `test_run_start_with_selected_agents_records_sequential_steps`:

```python
def test_run_start_with_selected_agents_records_sequential_steps(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "agent", "create", "agent_researcher", "--role", "researcher")
    run_cli(tmp_path, "session", "create", "agent run")

    result = run_cli(
        tmp_path,
        "run",
        "start",
        "research",
        "compare two planning approaches",
        "--agent",
        "agent_researcher",
        "--agent",
        "agent_auditor",
    )

    assert result.returncode == 0, result.stderr
    run_id = parse_id(result.stdout, "run_")
    run_dir = tmp_path / ".novi" / "runs" / run_id
    run_text = (run_dir / "run.yaml").read_text()
    events_text = (run_dir / "events.jsonl").read_text()
    artifacts = list((run_dir / "artifacts").glob("*-agent-step.md"))

    assert "agent_researcher" in run_text
    assert "agent_auditor" in run_text
    assert "AgentStepCompleted" in events_text
    assert len(artifacts) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest tests/test_cli_core_loop.py::test_run_start_with_selected_agents_records_sequential_steps -v`

Expected: FAIL because `run start` does not accept `--agent` and does not write step artifacts.

- [ ] **Step 3: Implement selected agent snapshots and step artifacts**

Load selected agent definitions before starting a run. Pass them to the runner. In the runner, snapshot each agent into `participants`, write one deterministic step artifact per agent, append `AgentStepCompleted` events, and keep the existing summary/tool/memory behavior.

- [ ] **Step 4: Run test to verify it passes**

Run: `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest tests/test_cli_core_loop.py::test_run_start_with_selected_agents_records_sequential_steps -v`

Expected: PASS.

## Final Verification

- [ ] Run `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest -v`.
- [ ] Run a smoke test in a temporary directory:

```bash
UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli init
UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli agent create agent_researcher --role researcher
UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli agent list
UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli session create "agent run"
UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli run start research "compare two planning approaches" --agent agent_researcher --agent agent_auditor
UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli run inspect <run_id>
```

- [ ] Commit docs and implementation at functional checkpoints.
