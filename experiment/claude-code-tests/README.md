# Claude Code Test Folders

These folders are the clean entry points for Claude Code tests.

Do not start Claude Code from the repository root for the first comparison. Start it from one of the condition folders below so the visible local context is minimal.

First probe:

```text
q5-dense-primitive-verdict/
  naive/
  physical-prior/
```

Each condition folder contains only:

- `prompt-to-paste.md`: exact prompt to paste into Claude Code;
- `source-files.md`: the external EmbodiedAI files Claude is allowed to read;
- `answer.md`: output target.
- `run.sh`: non-interactive Claude Code command for this condition.

Reviewer notes are not included in these folders.

## First Run

Naive:

```bash
cd /Users/cyan/Project/novilab/experiment/claude-code-tests/q5-dense-primitive-verdict/naive
claude
```

Then paste `prompt-to-paste.md`.

Offline command:

```bash
/Users/cyan/Project/novilab/experiment/claude-code-tests/q5-dense-primitive-verdict/naive/run.sh
```

Physical-prior prompt:

```bash
cd /Users/cyan/Project/novilab/experiment/claude-code-tests/q5-dense-primitive-verdict/physical-prior
claude
```

Then paste `prompt-to-paste.md`.

Offline command:

```bash
/Users/cyan/Project/novilab/experiment/claude-code-tests/q5-dense-primitive-verdict/physical-prior/run.sh
```
