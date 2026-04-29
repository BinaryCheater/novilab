# 2026-04-30 Phase 1.5 Agent Profile Bindings

## Goal

Start the Phase 1.5 usable integrated research loop by making agent profile
authority, kernel binding, and tool routing inspectable.

## Changed

- Extended project-local agent profiles with authority level, prompt refs,
  interface mode, and kernel binding hints.
- Snapshotted those fields into run participants.
- Archived compiled kernel binding records per run.
- Added tool routing metadata to CLI-visible ToolSpecs.
- Updated Phase 1.5 roadmap language around layered knowledge, mid-term
  session memory, and agent authority levels.

## Verified

- `uv run pytest tests/test_cli_core_loop.py::test_agent_profile_v2_records_authority_and_binding_hints -v`
- `uv run pytest tests/test_cli_core_loop.py::test_run_archives_compiled_kernel_bindings -v`
- `uv run pytest tests/test_cli_core_loop.py::test_tool_specs_show_expose_to_routing_metadata -v`
- `uv run pytest -q` passed with 29 tests.
