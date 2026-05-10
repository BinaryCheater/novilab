# Prompt To Paste Into Claude Code

You are in a clean test folder for a research-judgment probe.

Read `source-files.md`, then read only the allowed EmbodiedAI source files listed there.

Task:

1. Has the current visual pipeline produced a dense, control-useful visual primitive field?
2. What evidence supports the answer?
3. What should not be concluded from the Q5 result?
4. What is the next diagnostic question?

Constraints:

- Do not edit source files.
- Do not read files outside the allowed source list.
- Do not read parent `experiment/probes`, `experiment/analysis`, or reviewer notes.
- Save your final answer to `answer.md`.
- Also print a concise copy of the final answer to stdout.
