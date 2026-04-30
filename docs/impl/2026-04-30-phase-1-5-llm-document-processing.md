# 2026-04-30 Phase 1.5 LLM Document Processing

## Goal

Make the document processing workflow usable with an LLM-backed DeepAgents
kernel, while preserving Novi's review and patch boundaries.

## Changed

- Added default project-local `document.curate` and `document.merge` skills.
- Extended `novi process --kernel deepagents` to call DeepAgents.
- Built a processing prompt from WorkflowSpec, document skills, source refs,
  imported content, and target document content.
- Defined the LLM output protocol:
  - preferred virtual files: `/analysis_note.md` and `/proposed.md`;
  - fallback JSON: `analysis_markdown` and `proposed_markdown`.
- Archived DeepAgents messages, model call records, response text, and
  `processing_prompt.md` in the processing run.
- Converted LLM analysis into an analysis note artifact and LLM proposed target
  content into a `document_patch` contribution.

## Verified

- `uv run pytest tests/test_cli_core_loop.py::test_skill_list_shows_builtin_skills -v`
- `uv run pytest tests/test_cli_core_loop.py::test_process_deepagents_generates_analysis_note_and_patch_from_files -v`
- `uv run pytest tests/test_cli_core_loop.py::test_process_deepagents_accepts_json_output_protocol -v`

## Follow-Up

- Test against a real configured OpenAI-compatible provider.
- Improve prompt/skill wording after manual use.
- Add merge/review agent support for conflicted patch contributions.
