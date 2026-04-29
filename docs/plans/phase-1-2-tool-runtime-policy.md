# Phase 1.2 Tool Runtime And Policy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a minimal Novi-owned tool registry, policy gate, and execution record path for deterministic local tools.

**Architecture:** Create a focused `tools.py` module that owns built-in tool specs, listing/loading, policy decisions, and deterministic execution. Extend the CLI with `novi tool list/show`, initialize `.novi/tools/`, and route the runner's `search_stub.query` through the tool runtime instead of writing tool calls inline.

**Tech Stack:** Python 3.9+, argparse, PyYAML, JSONL records, pytest.

---

## File Structure

- `src/novi_lab/tools.py`: built-in tool registry, project-local tool discovery, policy evaluation, deterministic execution.
- `src/novi_lab/store.py`: initialize `.novi/tools/`.
- `src/novi_lab/cli.py`: add `tool list` and `tool show`.
- `src/novi_lab/runner.py`: call `execute_tool()` and record allowed/blocked tool calls.
- `tests/test_cli_core_loop.py`: CLI and run behavior tests.
- `docs/impl/2026-04-29-phase-1-2-tool-runtime-policy.md`: implementation record.

## Task 1: Tool Registry CLI

**Files:**
- Create: `src/novi_lab/tools.py`
- Modify: `src/novi_lab/store.py`
- Modify: `src/novi_lab/cli.py`
- Test: `tests/test_cli_core_loop.py`

- [ ] **Step 1: Write failing test**

Add `test_tool_list_and_show_builtin_tool`:

```python
def test_tool_list_and_show_builtin_tool(tmp_path):
    run_cli(tmp_path, "init")

    list_result = run_cli(tmp_path, "tool", "list")
    show_result = run_cli(tmp_path, "tool", "show", "search_stub.query")

    assert list_result.returncode == 0, list_result.stderr
    assert "search_stub.query" in list_result.stdout
    assert "read_only" in list_result.stdout
    assert show_result.returncode == 0, show_result.stderr
    assert "Tool: search_stub.query" in show_result.stdout
    assert "Risk: read_only" in show_result.stdout
    assert "Policy: allowed" in show_result.stdout
```

- [ ] **Step 2: Verify red**

Run: `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest tests/test_cli_core_loop.py::test_tool_list_and_show_builtin_tool -v`

Expected: FAIL because the `tool` command does not exist.

- [ ] **Step 3: Implement minimal registry and CLI**

Add `builtin_tools()`, `list_tools(root)`, `load_tool(root, tool_id)`, and CLI handlers for `tool list/show`. Add `.novi/tools/` to workspace initialization.

- [ ] **Step 4: Verify green**

Run: `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest tests/test_cli_core_loop.py::test_tool_list_and_show_builtin_tool -v`

Expected: PASS.

## Task 2: Allowed Tool Runtime

**Files:**
- Modify: `src/novi_lab/tools.py`
- Modify: `src/novi_lab/runner.py`
- Test: `tests/test_cli_core_loop.py`

- [ ] **Step 1: Write failing test**

Add `test_run_records_allowed_tool_runtime_result`:

```python
def test_run_records_allowed_tool_runtime_result(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "tool run")

    result = run_cli(tmp_path, "run", "start", "research", "inspect local tool runtime")

    assert result.returncode == 0, result.stderr
    run_id = parse_id(result.stdout, "run_")
    tool_calls = (tmp_path / ".novi" / "runs" / run_id / "tool_calls.jsonl").read_text()

    assert '"tool_id": "search_stub.query"' in tool_calls
    assert '"policy_result": "allowed"' in tool_calls
    assert '"status": "success"' in tool_calls
    assert '"executor": "novi_tool_runtime"' in tool_calls
```

- [ ] **Step 2: Verify red**

Run: `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest tests/test_cli_core_loop.py::test_run_records_allowed_tool_runtime_result -v`

Expected: FAIL because existing tool calls are still handwritten and have no runtime executor marker.

- [ ] **Step 3: Implement `execute_tool()`**

Implement `execute_tool(root, run_id, agent, tool_id, args)` so it checks tool existence, verifies `tool_id in agent["tool_scope"]`, evaluates policy, executes deterministic `search_stub.query`, and returns a tool call record. Update the runner to append that returned record.

- [ ] **Step 4: Verify green**

Run: `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest tests/test_cli_core_loop.py::test_run_records_allowed_tool_runtime_result -v`

Expected: PASS.

## Task 3: Blocked Tool Scope Records

**Files:**
- Modify: `src/novi_lab/tools.py`
- Modify: `src/novi_lab/runner.py`
- Test: `tests/test_cli_core_loop.py`

- [ ] **Step 1: Write failing test**

Add `test_run_records_blocked_tool_when_agent_lacks_scope`:

```python
def test_run_records_blocked_tool_when_agent_lacks_scope(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "agent", "create", "agent_observer", "--role", "observer")
    run_cli(tmp_path, "session", "create", "blocked tool run")

    result = run_cli(
        tmp_path,
        "run",
        "start",
        "research",
        "attempt scoped search",
        "--agent",
        "agent_observer",
    )

    assert result.returncode == 0, result.stderr
    run_id = parse_id(result.stdout, "run_")
    inspect_result = run_cli(tmp_path, "run", "inspect", run_id)
    tool_calls = (tmp_path / ".novi" / "runs" / run_id / "tool_calls.jsonl").read_text()

    assert '"tool_id": "search_stub.query"' in tool_calls
    assert '"policy_result": "blocked"' in tool_calls
    assert '"status": "blocked"' in tool_calls
    assert "search_stub.query blocked tool_not_in_agent_scope" in inspect_result.stdout
```

- [ ] **Step 2: Verify red**

Run: `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest tests/test_cli_core_loop.py::test_run_records_blocked_tool_when_agent_lacks_scope -v`

Expected: FAIL because missing tool scope is not enforced.

- [ ] **Step 3: Record blocked scope decisions**

Return blocked tool call records when the selected agent lacks tool scope. Include `block_reason: tool_not_in_agent_scope`. Keep the run completed because the deterministic runner records the blocked attempt as evidence.

- [ ] **Step 4: Verify green**

Run: `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest tests/test_cli_core_loop.py::test_run_records_blocked_tool_when_agent_lacks_scope -v`

Expected: PASS.

## Final Verification

- [ ] Run `UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run pytest -v`.
- [ ] Run a temporary-directory smoke test:

```bash
UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli init
UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli tool list
UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli tool show search_stub.query
UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli session create "tool run"
UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli run start research "inspect local tool runtime"
UV_CACHE_DIR=/private/tmp/novilab-uv-cache uv run --project /Users/cyan/Project/novilab python -m novi_lab.cli run inspect <run_id>
```

- [ ] Commit with message `feat: add minimal tool runtime policy`.
