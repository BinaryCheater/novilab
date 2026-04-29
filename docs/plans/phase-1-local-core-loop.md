# Phase 1 Local Core Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first local-first Novi CLI loop that initializes `.novi/`, discovers skills, creates sessions, starts deterministic runs, inspects records, and lists memory candidates.

**Architecture:** Use a small Python package with a filesystem-backed store and explicit CLI command handlers. Records are readable YAML or JSONL-compatible JSON lines, and the deterministic runner writes inspectable events, artifacts, context packs, tool calls, summaries, and memory candidates without a real LLM or network.

**Tech Stack:** Python 3.9+, uv-managed environment, standard library, PyYAML for YAML, pytest for tests.

---

## File Structure

- `pyproject.toml`: package metadata, console script, pytest configuration.
- `src/novi_lab/__init__.py`: package version.
- `src/novi_lab/ids.py`: stable prefixed ID generation.
- `src/novi_lab/store.py`: filesystem layout, YAML/JSONL helpers, artifact hashing.
- `src/novi_lab/skills.py`: built-in and project-local `SKILL.md` discovery.
- `src/novi_lab/runner.py`: deterministic local run writer.
- `src/novi_lab/cli.py`: `novi` command parser and command handlers.
- `src/novi_lab/builtin_skills/research.review/SKILL.md`: built-in research skill.
- `src/novi_lab/builtin_skills/run.audit/SKILL.md`: built-in audit skill.
- `src/novi_lab/builtin_skills/memory.curate/SKILL.md`: built-in memory skill.
- `tests/test_cli_core_loop.py`: end-to-end CLI behavior tests.

## Task 1: Project Skeleton And `novi init`

**Files:**
- Create: `pyproject.toml`
- Create: `src/novi_lab/__init__.py`
- Create: `src/novi_lab/ids.py`
- Create: `src/novi_lab/store.py`
- Create: `src/novi_lab/cli.py`
- Test: `tests/test_cli_core_loop.py`

- [ ] **Step 1: Write failing tests**

```python
def test_init_creates_local_workspace(tmp_path):
    result = run_cli(tmp_path, "init")
    assert result.returncode == 0
    assert (tmp_path / ".novi" / "novi.yaml").exists()
    assert (tmp_path / ".novi" / "sessions").is_dir()
    assert (tmp_path / ".novi" / "runs").is_dir()
    assert "initialized" in result.stdout
```

- [ ] **Step 2: Verify red**

Run: `uv run pytest tests/test_cli_core_loop.py::test_init_creates_local_workspace -v`

Expected: FAIL because the `novi_lab` package and CLI do not exist yet.

- [ ] **Step 3: Implement minimal package, store, and CLI init**

Create package metadata, a console script, and `init_workspace()` that writes `.novi/novi.yaml`, `.novi/specs/project.yaml`, `.novi/specs/policies.yaml`, `.novi/sessions/`, `.novi/runs/`, `.novi/memory/candidates/`, `.novi/artifacts/`, `.novi/approvals/`, and `.novi/skills/`.

- [ ] **Step 4: Verify green**

Run: `uv run pytest tests/test_cli_core_loop.py::test_init_creates_local_workspace -v`

Expected: PASS.

## Task 2: Skill Discovery

**Files:**
- Create: `src/novi_lab/skills.py`
- Create: `src/novi_lab/builtin_skills/research.review/SKILL.md`
- Create: `src/novi_lab/builtin_skills/run.audit/SKILL.md`
- Create: `src/novi_lab/builtin_skills/memory.curate/SKILL.md`
- Modify: `src/novi_lab/cli.py`
- Test: `tests/test_cli_core_loop.py`

- [ ] **Step 1: Write failing tests**

```python
def test_skill_list_shows_builtin_skills(tmp_path):
    run_cli(tmp_path, "init")
    result = run_cli(tmp_path, "skill", "list")
    assert result.returncode == 0
    assert "research.review" in result.stdout
    assert "run.audit" in result.stdout
    assert "memory.curate" in result.stdout
```

- [ ] **Step 2: Verify red**

Run: `uv run pytest tests/test_cli_core_loop.py::test_skill_list_shows_builtin_skills -v`

Expected: FAIL because `novi skill list` is not implemented.

- [ ] **Step 3: Implement discovery**

Discover built-ins from package resources and project-local skills from `.novi/skills/`, derive ids from folder names, and show source plus description.

- [ ] **Step 4: Verify green**

Run: `uv run pytest tests/test_cli_core_loop.py::test_skill_list_shows_builtin_skills -v`

Expected: PASS.

## Task 3: Sessions

**Files:**
- Modify: `src/novi_lab/store.py`
- Modify: `src/novi_lab/cli.py`
- Test: `tests/test_cli_core_loop.py`

- [ ] **Step 1: Write failing tests**

```python
def test_session_create_writes_session_records(tmp_path):
    run_cli(tmp_path, "init")
    result = run_cli(tmp_path, "session", "create", "physical-ai literature scan")
    assert result.returncode == 0
    session_id = parse_id(result.stdout, "sess_")
    session_dir = tmp_path / ".novi" / "sessions" / session_id
    assert (session_dir / "session.yaml").exists()
    assert (session_dir / "summary.md").exists()
    assert (session_dir / "messages.jsonl").exists()
```

- [ ] **Step 2: Verify red**

Run: `uv run pytest tests/test_cli_core_loop.py::test_session_create_writes_session_records -v`

Expected: FAIL because session commands are not implemented.

- [ ] **Step 3: Implement create/list/open/inspect basics**

Create `session.yaml`, `summary.md`, `messages.jsonl`, update `.novi/novi.yaml` with `active_session_id`, and list sessions by reading session records.

- [ ] **Step 4: Verify green**

Run: `uv run pytest tests/test_cli_core_loop.py::test_session_create_writes_session_records -v`

Expected: PASS.

## Task 4: Deterministic Run Loop

**Files:**
- Create: `src/novi_lab/runner.py`
- Modify: `src/novi_lab/store.py`
- Modify: `src/novi_lab/cli.py`
- Test: `tests/test_cli_core_loop.py`

- [ ] **Step 1: Write failing tests**

```python
def test_run_start_creates_auditable_deterministic_records(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "physical-ai literature scan")
    result = run_cli(tmp_path, "run", "start", "research", "summarize recent work")
    assert result.returncode == 0
    run_id = parse_id(result.stdout, "run_")
    run_dir = tmp_path / ".novi" / "runs" / run_id
    assert (run_dir / "run.yaml").exists()
    assert (run_dir / "events.jsonl").read_text().count("\n") >= 5
    assert (run_dir / "tool_calls.jsonl").exists()
    assert (run_dir / "summary.md").exists()
    assert list((run_dir / "artifacts").glob("*.md"))
```

- [ ] **Step 2: Verify red**

Run: `uv run pytest tests/test_cli_core_loop.py::test_run_start_creates_auditable_deterministic_records -v`

Expected: FAIL because run creation and the runner are not implemented.

- [ ] **Step 3: Implement deterministic runner**

Create run records under `.novi/runs/<run_id>/`, append events, write a context pack artifact, write a deterministic research note artifact, write a read-only `search_stub.query` tool call record, propose one memory candidate, and mark the run completed.

- [ ] **Step 4: Verify green**

Run: `uv run pytest tests/test_cli_core_loop.py::test_run_start_creates_auditable_deterministic_records -v`

Expected: PASS.

## Task 5: Inspect And Memory Review

**Files:**
- Modify: `src/novi_lab/cli.py`
- Modify: `src/novi_lab/store.py`
- Test: `tests/test_cli_core_loop.py`

- [ ] **Step 1: Write failing tests**

```python
def test_run_inspect_and_memory_review_explain_outputs(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "physical-ai literature scan")
    run_result = run_cli(tmp_path, "run", "start", "research", "summarize recent work")
    run_id = parse_id(run_result.stdout, "run_")
    inspect_result = run_cli(tmp_path, "run", "inspect", run_id)
    assert inspect_result.returncode == 0
    assert "completed" in inspect_result.stdout
    assert "search_stub.query" in inspect_result.stdout
    review_result = run_cli(tmp_path, "memory", "review")
    assert review_result.returncode == 0
    assert "proposed" in review_result.stdout
```

- [ ] **Step 2: Verify red**

Run: `uv run pytest tests/test_cli_core_loop.py::test_run_inspect_and_memory_review_explain_outputs -v`

Expected: FAIL because inspect and memory review output are incomplete.

- [ ] **Step 3: Implement inspect/review**

Show run objective, status, participants, context pack ids, tool calls, artifacts, memory candidates, and summary. List pending memory candidates from `.novi/memory/candidates/`.

- [ ] **Step 4: Verify green**

Run: `uv run pytest tests/test_cli_core_loop.py::test_run_inspect_and_memory_review_explain_outputs -v`

Expected: PASS.

## Final Verification

- [ ] Run `uv run pytest -v`.
- [ ] Run `uv run python -m novi_lab.cli init` in a temporary directory.
- [ ] Run `uv run python -m novi_lab.cli skill list`.
- [ ] Run `uv run python -m novi_lab.cli session create "physical-ai literature scan"`.
- [ ] Run `uv run python -m novi_lab.cli run start research "summarize recent work on physical AI skill learning"`.
- [ ] Run `uv run python -m novi_lab.cli run inspect <run_id>`.
- [ ] Run `uv run python -m novi_lab.cli memory review`.
- [ ] Add a lightweight implementation checkpoint under `docs/impl/YYYY-MM-DD-phase-1-first-code.md`.
- [ ] Commit the plan separately from code when practical, then commit the working code checkpoint.

## Deferred

- Real LLM calls.
- Real network search.
- ROS, simulation, training, browser automation, MCP, web dashboard, TUI, plugin distribution, cowork assignments, and full team permissions.
