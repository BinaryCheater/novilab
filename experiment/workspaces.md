# Isolated Test Workspaces

Date: 2026-05-07

This file records the isolated worktrees used for quick agent workflow probes.

## Worktree Layout

The main planning workspace remains:

```text
/Users/cyan/Project/novilab
```

Isolated test workspaces:

| Condition | Path | Branch | Intended Use |
| --- | --- | --- | --- |
| Claude Code naive | `/Users/cyan/Project/novilab/.worktrees/claude-naive` | `experiment-claude-naive` | Run Claude Code with only the probe task and allowed source files. |
| Claude Code physical-prior prompt | `/Users/cyan/Project/novilab/.worktrees/claude-physical-prior` | `experiment-claude-physical-prior` | Run Claude Code with the physical-prior research prompt. |
| Codex naive | `/Users/cyan/Project/novilab/.worktrees/codex-naive` | `experiment-codex-naive` | Run Codex with only the probe task and allowed source files. |
| Codex physical-prior prompt | `/Users/cyan/Project/novilab/.worktrees/codex-physical-prior` | `experiment-codex-physical-prior` | Run Codex with the physical-prior research prompt. |

The `.worktrees/` directory is ignored by Git. Each workspace has its own branch, so agent edits, scratch files, and run records do not collide.

## How To Run The First Test

Use one probe first, preferably:

```text
experiment/probes/q5-dense-primitive-verdict.md
```

For each condition:

1. Open the corresponding worktree directory.
2. Start the target agent there.
3. Give it the probe task.
4. Save the raw output in that worktree under:

```text
experiment/runs/2026-05-07/q5-dense-primitive-verdict/<condition>.md
```

5. Commit or leave the branch dirty depending on whether you want to preserve the raw run in Git.
6. Copy or summarize the reviewed result back into the main planning workspace analysis file:

```text
experiment/analysis/2026-05-07-q5-dense-primitive-verdict.md
```

## Prompt Inputs

Naive conditions should use only:

```text
Read experiment/probes/q5-dense-primitive-verdict.md and answer the task.
Use only the allowed source files listed in the probe.
Do not edit source files.
Save your answer to experiment/runs/2026-05-07/q5-dense-primitive-verdict/<condition>.md using experiment/templates/run-record.md.
```

Physical-prior prompt conditions should prepend:

```text
experiment/prompts/physical-prior-research-prompt.md
```

Then run the same probe task.

## Recommended First Batch

Run only four conditions first:

- `claude-naive`
- `claude-physical-prior`
- `codex-naive`
- `codex-physical-prior`

Do not run the skill/SOP or Novi workflow conditions until the first probe format is validated.

## Review Procedure

After all four outputs exist:

1. Read each output side by side.
2. Fill one analysis record from:

```text
experiment/templates/analysis-record.md
```

3. Focus on behavior differences:

- Did the agent cite the right evidence?
- Did it overclaim dense/control success?
- Did it blame the wrong failure mode?
- Did the guided prompt improve minimality?
- Did either agent already do well without extra workflow?
- What workflow gate or artifact would have helped?

## Cleanup

When a test branch is no longer useful:

```bash
git worktree remove /Users/cyan/Project/novilab/.worktrees/<name>
git branch -D <branch-name>
```

Only remove branches after useful run records have been copied or committed.

