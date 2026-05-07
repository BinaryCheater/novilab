# Prompt To Paste Into Claude Code

You are in a clean test folder for a research-judgment probe.

Read `source-files.md`, then read only the allowed EmbodiedAI source files listed there.

Research discipline:

1. Separate what the experiment directly shows from what it does not show.
2. Do not infer dense 3D, control sufficiency, or general embodied intelligence from sparse success.
3. Every proposed next module or method must name the failure mode it targets.
4. Do not recommend larger models, more data, memory, planners, or world models unless the provided evidence specifically supports that need.
5. Prefer physical-prior hypotheses when justified by evidence: motion conditioning, depth uncertainty, surface continuity, boundary/occlusion, active observability, and robot-centric state.
6. A good next step must be falsifiable and include what result would disconfirm it.
7. If evidence is missing, say what is missing instead of filling the gap with speculation.

Task:

1. Has the current visual pipeline produced a dense, control-useful visual primitive field?
2. What evidence supports the answer?
3. What should not be concluded from the Q5 result?
4. What is the next diagnostic question?

Output format:

- Direct answer
- Evidence used
- Unsupported conclusions to avoid
- Next diagnostic question

Constraints:

- Do not edit source files.
- Do not read files outside the allowed source list.
- Do not read parent `experiment/probes`, `experiment/analysis`, or reviewer notes.
- Save your final answer to `answer.md`.
- Also print a concise copy of the final answer to stdout.
