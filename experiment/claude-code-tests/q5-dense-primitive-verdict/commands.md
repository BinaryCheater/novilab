# Commands

Run from the repository root:

```bash
cd /Users/cyan/Project/novilab/experiment/claude-code-tests/q5-dense-primitive-verdict
./naive/run.sh
./physical-prior/run.sh
```

Or run each condition manually:

```bash
cd /Users/cyan/Project/novilab/experiment/claude-code-tests/q5-dense-primitive-verdict/naive
claude --bare --no-session-persistence --add-dir /Users/cyan/Project/EmbodiedAI --permission-mode acceptEdits -p "$(cat prompt-to-paste.md)" | tee stdout.md
```

```bash
cd /Users/cyan/Project/novilab/experiment/claude-code-tests/q5-dense-primitive-verdict/physical-prior
claude --bare --no-session-persistence --add-dir /Users/cyan/Project/EmbodiedAI --permission-mode acceptEdits -p "$(cat prompt-to-paste.md)" | tee stdout.md
```

After both runs, compare:

```bash
diff -u naive/answer.md physical-prior/answer.md
```

Then review against:

```text
/Users/cyan/Project/novilab/experiment/private-review/q5-dense-primitive-verdict-reviewer.md
```

