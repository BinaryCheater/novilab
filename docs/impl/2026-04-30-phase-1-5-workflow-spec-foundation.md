# 2026-04-30 Phase 1.5 Workflow Spec Foundation

## Goal

Turn `document-merge` from a hard-coded process name into a project-local
WorkflowSpec that can guide deterministic processing now and LLM-backed
processing later.

## Changed

- Added default `.novi/workflows/document-merge.yaml` during `novi init`.
- Added `novi workflow list` and `novi workflow show`.
- Added system/agent/human step kinds to the default document-merge workflow:
  `load_source`, `produce_artifact`, `produce_contribution`, `check`,
  `review_gate`, and `apply_change`.
- Added workflow step instructions and skill refs for future LLM-backed
  analysis and patch generation.
- Updated `novi process` to load the WorkflowSpec and archive
  `workflow_id`, `workflow_version`, `step_results`, and `workflow_prompt.md`
  in the processing run.

## Verified

- `uv run pytest tests/test_cli_core_loop.py::test_init_creates_default_document_merge_workflow -v`
- `uv run pytest tests/test_cli_core_loop.py::test_workflow_list_and_show_document_merge -v`
- `uv run pytest tests/test_cli_core_loop.py::test_process_import_with_target_creates_analysis_note_and_patch_contribution -v`

## Follow-Up

- Execute workflow steps through a general step runner instead of the current
  document-processing adapter.
- Add DeepAgents prompt construction from `workflow_prompt.md`.
- Add workflow patch contributions targeting `.novi/workflows/*.yaml`.
