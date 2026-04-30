# 2026-04-30 Phase 1.5 Knowledge Review Loop

## Goal

Close the first local knowledge review loop so imported material can be
inspected, accepted, written to a layered Markdown knowledge vault, included in
later run context, and traced from a later run.

## Changed

- Added artifact list/show CLI commands for imported and run-local artifacts.
- Added contribution accept, writing accepted imports into `.novi/knowledge/`.
- Added raw and accepted knowledge vault layers plus `knowledge/index.jsonl`.
- Added knowledge list/show CLI commands for accepted records.
- Included accepted knowledge refs in new run context packs.
- Included accepted knowledge content in prompt archives and system prompts.
- Added accepted knowledge lineage output to `novi run trace`.
- Added memory list/show CLI commands for review decisions and evidence.

## Verified

- `uv run pytest tests/test_cli_core_loop.py::test_artifact_list_and_show_imported_artifact -v`
- `uv run pytest tests/test_cli_core_loop.py::test_contribution_accept_writes_reviewed_knowledge_record -v`
- `uv run pytest tests/test_cli_core_loop.py::test_run_context_includes_accepted_knowledge -v`
- `uv run pytest tests/test_cli_core_loop.py::test_run_trace_explains_accepted_knowledge_lineage -v`
- `uv run pytest tests/test_cli_core_loop.py::test_knowledge_list_and_show_accepted_record -v`
- `uv run pytest tests/test_cli_core_loop.py::test_memory_list_and_show_include_review_decisions_and_evidence -v`
- `uv run pytest -q`

## Follow-Up

- Workflow patch records and approval queues are still placeholders.
- Contribution request-changes is still not implemented.
- Accepted memory should be folded into context with the same lineage treatment
  as accepted knowledge.
