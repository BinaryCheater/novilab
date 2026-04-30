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
- Added `novi tool expose <tool_id> <agent_id>` to configure project-local
  tool routing.
- Enforced final tool availability as both agent `tool_scope` and ToolSpec
  `expose_to` routing.
- Filtered compiled kernel bindings so DeepAgents wrappers only receive tools
  available to the selected agent.
- Added Rich as the first terminal presentation dependency.
- Added `novi ps` as an operator overview for active session, session list,
  recent runs, and pending review counts.
- Rendered `session list` and `run list` as Rich tables.
- Added `latest` support to `run inspect`.
- Added `novi review` as a unified pending-review overview.
- Added `novi import <path>` for local file knowledge imports, creating an
  artifact record and pending contribution record.
- Added `novi contribution list`, `novi contribution inspect`, and
  `novi contribution reject`.
- Updated Phase 1.5 roadmap language around layered knowledge, mid-term
  session memory, and agent authority levels.

## Verified

- `uv run pytest tests/test_cli_core_loop.py::test_agent_profile_v2_records_authority_and_binding_hints -v`
- `uv run pytest tests/test_cli_core_loop.py::test_run_archives_compiled_kernel_bindings -v`
- `uv run pytest tests/test_cli_core_loop.py::test_tool_specs_show_expose_to_routing_metadata -v`
- `uv run pytest tests/test_cli_core_loop.py::test_tool_expose_updates_routing_metadata -v`
- `uv run pytest tests/test_cli_core_loop.py::test_tool_call_requires_agent_scope_and_exposure -v`
- `uv run pytest tests/test_cli_core_loop.py::test_kernel_binding_filters_unexposed_tools -v`
- `uv run pytest tests/test_cli_core_loop.py::test_ps_lists_active_session_recent_runs_and_pending_memory -v`
- `uv run pytest tests/test_cli_core_loop.py::test_session_and_run_lists_use_operator_tables -v`
- `uv run pytest tests/test_cli_core_loop.py::test_run_inspect_accepts_latest_alias -v`
- `uv run pytest tests/test_cli_core_loop.py::test_import_creates_artifact_and_contribution_record -v`
- `uv run pytest tests/test_cli_core_loop.py::test_contribution_list_inspect_and_reject -v`
- `uv run pytest tests/test_cli_core_loop.py::test_ps_and_review_include_pending_contributions -v`
- `uv run pytest -q` passed with 38 tests.
