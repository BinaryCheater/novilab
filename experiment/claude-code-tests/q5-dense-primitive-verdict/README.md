# Q5 Dense Primitive Verdict Claude Code Test

This is the first clean Claude Code test.

It has two conditions:

- `naive/`: task-only prompt.
- `physical-prior/`: same task with physical-prior research discipline added.

Run Claude Code from inside the condition folder, or use the scripts:

```bash
./naive/run.sh
./physical-prior/run.sh
```

Each run writes:

- `answer.md`: the answer Claude Code was instructed to save.
- `stdout.md`: the non-interactive Claude Code terminal output.

The only external source directory granted to Claude Code is:

```text
/Users/cyan/Project/EmbodiedAI
```

Reviewer notes live outside this folder under `experiment/private-review/` and should not be provided to Claude Code.

