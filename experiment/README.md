# Experiment Workspace

This folder is for fast exploratory experiments around EmbodiedAI visual research workflows.

The current goal is not to build a paper-grade benchmark and not to prove that Novi is better than Claude Code. The goal is to use real EmbodiedAI visual experiment records to test:

- whether agents understand physical-prior research materials;
- which prompts, skills, and workflow gates improve research judgment;
- which parts Claude Code already handles well without Novi;
- which Novi product capabilities are missing for this style of work.

## Source Materials

Primary external source repository:

```text
/Users/cyan/Project/EmbodiedAI
```

Important source areas:

- `/Users/cyan/Project/EmbodiedAI/README.md`
- `/Users/cyan/Project/EmbodiedAI/visual/doc/spatial_learning_starting_point.md`
- `/Users/cyan/Project/EmbodiedAI/visual/doc/visual_foundation_meeting_catchup_cn.md`
- `/Users/cyan/Project/EmbodiedAI/visual/foundation/docs/index.md`
- `/Users/cyan/Project/EmbodiedAI/visual/foundation/docs/current_implementation_and_failure_audit.md`
- `/Users/cyan/Project/EmbodiedAI/visual/foundation/reports/`

Treat the EmbodiedAI repository as read-only unless the user explicitly asks to edit it.

## Folder Layout

- `probes/`: reusable test tasks extracted from EmbodiedAI visual records.
- `prompts/`: prompt variants used in Codex or Claude Code comparisons.
- `skills/`: draft skill/SOP materials for research-method injection.
- `runs/`: raw run records from Codex, Claude Code, and Novi workflow probes.
- `analysis/`: cross-run analysis, prompt/skill deltas, and product gaps.
- `templates/`: run and analysis templates.
- `claude-code-tests/`: clean Claude Code test folders containing only public task instructions and output templates.

## Current Experiment Stance

Use small, repeatable probes rather than a large harness. Human review is the evaluator in this phase. Automatic scoring can come later only after the useful judgment dimensions are clear.
