# Phase 1.5 Usable Integrated Research Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first Phase 1.5 slice: richer agent profiles, inspectable kernel bindings, tool routing metadata, and the first records needed for workflow/knowledge review.

**Architecture:** Keep Novi Core as the source of truth. Project-local YAML records define agents, tool routing, workflows, and contributions; DeepAgents receives compiled bindings and Novi-wrapped tools. The first slice stays filesystem-only and deterministic-testable.

**Tech Stack:** Python 3.11+, uv, argparse CLI, PyYAML, JSONL, pytest.

---

## File Structure

- `src/novi_lab/agents.py`: extend project-local agent records and snapshots with authority level, prompt refs, interface mode, and kernel binding hints.
- `src/novi_lab/kernels.py`: expose a pure compile step for DeepAgents bindings and archive the compiled binding under each run.
- `src/novi_lab/tools.py`: add `expose_to` routing metadata to tool specs and enforce it alongside agent tool scope.
- `src/novi_lab/runner.py`: snapshot agent authority fields and attach kernel binding refs to run records.
- `src/novi_lab/cli.py`: show authority, prompt refs, kernel binding hints, and compiled binding paths in `agent show`, `run inspect`, and `run trace`.
- `tests/test_cli_core_loop.py`: add focused end-to-end tests for the new records and CLI output.
- `docs/impl/YYYY-MM-DD-phase-1-5-agent-profile-bindings.md`: implementation checkpoint.

## Task 1: AgentProfile v2 Records

**Files:**
- Modify: `src/novi_lab/agents.py`
- Modify: `src/novi_lab/cli.py`
- Test: `tests/test_cli_core_loop.py`

- [ ] **Step 1: Write the failing test**

Add this test to `tests/test_cli_core_loop.py`:

```python
def test_agent_profile_v2_records_authority_and_binding_hints(tmp_path):
    run_cli(tmp_path, "init")

    result = run_cli(tmp_path, "agent", "show", "agent_orchestrator")

    assert result.returncode == 0, result.stderr
    assert "Authority level: collaborator" in result.stdout
    assert "Interface mode: cli" in result.stdout
    assert "Prompt refs:" in result.stdout
    assert "research.review" in result.stdout
    assert "Kernel binding hints:" in result.stdout
    assert "deepagents_subagent" in result.stdout
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests/test_cli_core_loop.py::test_agent_profile_v2_records_authority_and_binding_hints -v
```

Expected: FAIL because current agent records and CLI output do not include these fields.

- [ ] **Step 3: Write minimal implementation**

Update `default_agents()` in `src/novi_lab/agents.py` so default agents include:

```python
"authority_level": "collaborator",
"prompt_refs": ["research.review"],
"interface_mode": "cli",
"kernel_binding_hints": {
    "deepagents": {
        "binding": "deepagents_subagent",
        "interrupt_on": [],
        "backend_routes": ["workspace", "skills"],
    }
},
```

For `agent_auditor`, use:

```python
"authority_level": "reviewer",
"prompt_refs": ["run.audit", "memory.curate"],
"interface_mode": "cli",
"kernel_binding_hints": {
    "deepagents": {
        "binding": "deepagents_subagent",
        "interrupt_on": [],
        "backend_routes": ["workspace", "skills", "run_records"],
    }
},
```

Update `create_agent()` defaults to use:

```python
"authority_level": "executor",
"prompt_refs": [],
"interface_mode": "headless",
"kernel_binding_hints": {
    "deepagents": {
        "binding": "deepagents_subagent",
        "interrupt_on": [],
        "backend_routes": ["workspace"],
    }
},
```

Update `agent_snapshot()` to copy `authority_level`, `prompt_refs`, `interface_mode`, and `kernel_binding_hints`.

Update `cmd_agent_show()` in `src/novi_lab/cli.py` to print:

```python
print(f"Authority level: {agent.get('authority_level', 'executor')}")
print(f"Interface mode: {agent.get('interface_mode', 'headless')}")
print("Prompt refs:")
for prompt_ref in agent.get("prompt_refs", []):
    print(f"- {prompt_ref}")
print("Kernel binding hints:")
for kernel, hints in agent.get("kernel_binding_hints", {}).items():
    print(f"- {kernel}: {hints.get('binding', '-')}")
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
uv run pytest tests/test_cli_core_loop.py::test_agent_profile_v2_records_authority_and_binding_hints -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/novi_lab/agents.py src/novi_lab/cli.py tests/test_cli_core_loop.py
git commit -m "feat: extend agent profile records"
```

## Task 2: Run Snapshots And Compiled Kernel Binding Archive

**Files:**
- Modify: `src/novi_lab/kernels.py`
- Modify: `src/novi_lab/runner.py`
- Modify: `src/novi_lab/cli.py`
- Test: `tests/test_cli_core_loop.py`

- [ ] **Step 1: Write the failing test**

Add this test:

```python
def test_run_archives_compiled_kernel_bindings(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "binding run")

    result = run_cli(tmp_path, "run", "start", "research", "inspect bindings")

    assert result.returncode == 0, result.stderr
    run_id = parse_id(result.stdout, "run_")
    run_dir = tmp_path / ".novi" / "runs" / run_id
    binding_text = (run_dir / "kernel_bindings.jsonl").read_text()
    inspect_result = run_cli(tmp_path, "run", "inspect", run_id)
    trace_result = run_cli(tmp_path, "run", "trace", run_id)

    assert '"agent_id": "agent_orchestrator"' in binding_text
    assert '"authority_level": "collaborator"' in binding_text
    assert '"kernel": "simple"' in binding_text
    assert '"tool_names": ["search_stub_query"]' in binding_text
    assert "Kernel bindings:" in inspect_result.stdout
    assert "agent_orchestrator simple" in inspect_result.stdout
    assert "Kernel bindings:" in trace_result.stdout
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests/test_cli_core_loop.py::test_run_archives_compiled_kernel_bindings -v
```

Expected: FAIL because `kernel_bindings.jsonl` is not written.

- [ ] **Step 3: Write minimal implementation**

Add a pure function to `src/novi_lab/kernels.py`:

```python
def compile_kernel_binding(participant, kernel):
    tool_scope = list(participant.get("tool_scope", []))
    return {
        "agent_id": participant.get("agent_id"),
        "role": participant.get("role"),
        "authority_level": participant.get("authority_level", "executor"),
        "kernel": kernel,
        "binding": participant.get("kernel_binding_hints", {}).get(kernel, {}).get("binding", "direct"),
        "tool_ids": tool_scope,
        "tool_names": [_tool_function_name(tool_id) for tool_id in tool_scope],
        "prompt_refs": list(participant.get("prompt_refs", [])),
        "interrupt_on": participant.get("kernel_binding_hints", {}).get(kernel, {}).get("interrupt_on", []),
        "backend_routes": participant.get("kernel_binding_hints", {}).get(kernel, {}).get("backend_routes", []),
    }
```

In `src/novi_lab/runner.py`, after participants are selected, write one binding per participant:

```python
from .kernels import compile_kernel_binding

binding_ids = []
for participant in participants:
    binding = compile_kernel_binding(participant, kernel)
    binding["run_id"] = run_id
    append_jsonl(run_dir / "kernel_bindings.jsonl", binding)
    binding_ids.append(f"{participant['agent_id']}:{kernel}")
run_record["kernel_binding_ids"] = binding_ids
```

In `src/novi_lab/cli.py`, read `kernel_bindings.jsonl` in `cmd_run_inspect()` and `cmd_run_trace()` and print:

```python
print("Kernel bindings:")
for binding in read_jsonl(run_dir / "kernel_bindings.jsonl"):
    print(f"- {binding.get('agent_id')} {binding.get('kernel')} {binding.get('binding')}")
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
uv run pytest tests/test_cli_core_loop.py::test_run_archives_compiled_kernel_bindings -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/novi_lab/kernels.py src/novi_lab/runner.py src/novi_lab/cli.py tests/test_cli_core_loop.py
git commit -m "feat: archive compiled kernel bindings"
```

## Task 3: Tool Routing Metadata

**Files:**
- Modify: `src/novi_lab/tools.py`
- Modify: `src/novi_lab/cli.py`
- Test: `tests/test_cli_core_loop.py`

- [ ] **Step 1: Write the failing test**

Add this test:

```python
def test_tool_specs_show_expose_to_routing_metadata(tmp_path):
    run_cli(tmp_path, "init")

    result = run_cli(tmp_path, "tool", "show", "search_stub.query")

    assert result.returncode == 0, result.stderr
    assert "Expose to:" in result.stdout
    assert "agent_orchestrator" in result.stdout
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests/test_cli_core_loop.py::test_tool_specs_show_expose_to_routing_metadata -v
```

Expected: FAIL because tool specs do not expose route metadata in CLI output.

- [ ] **Step 3: Write minimal implementation**

In `src/novi_lab/tools.py`, add `expose_to` to built-in read-only tool specs:

```python
"expose_to": ["agent_orchestrator"],
```

For `filesystem.read` and `git.status`, use:

```python
"expose_to": ["agent_orchestrator", "agent_auditor"],
```

Update `cmd_tool_show()` in `src/novi_lab/cli.py`:

```python
print("Expose to:")
for agent_id in tool.get("expose_to", []):
    print(f"- {agent_id}")
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
uv run pytest tests/test_cli_core_loop.py::test_tool_specs_show_expose_to_routing_metadata -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/novi_lab/tools.py src/novi_lab/cli.py tests/test_cli_core_loop.py
git commit -m "feat: show tool routing metadata"
```

## Task 4: Implementation Checkpoint And Full Verification

**Files:**
- Create: `docs/impl/YYYY-MM-DD-phase-1-5-agent-profile-bindings.md`
- Modify: `docs/plans/phase-1-5-usable-integrated-loop.md`

- [ ] **Step 1: Add implementation checkpoint**

Create `docs/impl/YYYY-MM-DD-phase-1-5-agent-profile-bindings.md` with:

```md
# YYYY-MM-DD Phase 1.5 Agent Profile Bindings

## Goal

Start the Phase 1.5 usable integrated research loop by making agent profile
authority, kernel binding, and tool routing inspectable.

## Changed

- Extended project-local agent profiles with authority level, prompt refs,
  interface mode, and kernel binding hints.
- Snapshotted those fields into run participants.
- Archived compiled kernel binding records per run.
- Added tool routing metadata to CLI-visible ToolSpecs.

## Verified

- `uv run pytest tests/test_cli_core_loop.py::test_agent_profile_v2_records_authority_and_binding_hints -v`
- `uv run pytest tests/test_cli_core_loop.py::test_run_archives_compiled_kernel_bindings -v`
- `uv run pytest tests/test_cli_core_loop.py::test_tool_specs_show_expose_to_routing_metadata -v`
- `uv run pytest -q`
```

- [ ] **Step 2: Run full verification**

Run:

```bash
uv run pytest -q
```

Expected: PASS with all tests passing.

- [ ] **Step 3: Commit docs**

```bash
git add docs/plans/phase-1-5-usable-integrated-loop.md docs/impl/YYYY-MM-DD-phase-1-5-agent-profile-bindings.md
git commit -m "docs: record phase 1.5 agent binding plan"
```

## Deferred

- No full workflow engine.
- No direct MCP client implementation.
- No full knowledge-vault manager.
- No automatic memory, workflow, prompt, or skill mutation.
- No unrestricted DeepAgents filesystem, shell, or memory built-ins.
