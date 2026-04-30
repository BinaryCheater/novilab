# 2026-04-30 Phase 1.5 Document Processing Patch Loop

## Goal

Implement the first skill-driven document processing loop where an imported
document can be processed into an analysis note and, when a target document is
provided, a reviewable patch contribution.

## Changed

- Added `novi process <contribution_id> --workflow document-merge`.
- Added deterministic document processing for import contributions.
- Added analysis note artifacts for processed imports.
- Added `document_patch` contributions with source refs, patch files, proposed
  content, target metadata, and base hashes.
- Added `novi contribution check` for patch dry-run validation.
- Extended `novi contribution accept` to apply patch contributions after check.
- Added conflict handling when the target changed since patch generation.
- Added `novi contribution request-changes --reason`.
- Restricted patch targets to `.novi/knowledge/`, `.novi/workflows/`, and
  `.novi/skills/`.

## Verified

- `uv run pytest tests/test_cli_core_loop.py::test_process_import_with_target_creates_analysis_note_and_patch_contribution -v`
- `uv run pytest tests/test_cli_core_loop.py::test_contribution_check_and_accept_apply_document_patch -v`
- `uv run pytest tests/test_cli_core_loop.py::test_contribution_accept_marks_conflict_when_target_changed -v`
- `uv run pytest tests/test_cli_core_loop.py::test_process_import_without_target_only_creates_analysis_note -v`
- `uv run pytest tests/test_cli_core_loop.py::test_process_rejects_patch_target_outside_allowed_project_state -v`
- `uv run pytest tests/test_cli_core_loop.py::test_contribution_request_changes_records_reason -v`
- `uv run pytest -q`

## Follow-Up

- Add DeepAgents-backed patch generation after the deterministic record path is
  exercised.
- Add workflow and skill patch examples using the same patch contribution
  machinery.
- Add merge/review agent assignment for conflicted contributions.
