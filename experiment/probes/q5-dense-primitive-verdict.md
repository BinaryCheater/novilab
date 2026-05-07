# Probe: Q5 Dense Primitive Verdict

## Task Prompt

Read the allowed source files and answer:

1. Has the current visual pipeline produced a dense, control-useful visual primitive field?
2. What evidence supports the answer?
3. What should not be concluded from the Q5 result?
4. What is the next diagnostic question?

## Allowed Source Files

- `/Users/cyan/Project/EmbodiedAI/visual/foundation/docs/q5_dense_coverage_reliability.md`
- `/Users/cyan/Project/EmbodiedAI/visual/foundation/reports/q5_dense_coverage_reliability.json`
- `/Users/cyan/Project/EmbodiedAI/visual/doc/visual_foundation_meeting_catchup_cn.md`

## Reviewer Notes

Expected answer:

- Q5 passes coarse coverage but fails the key-aware dense primitive threshold.
- Survivor precision is high and near-zero-disparity collapse is not the main problem.
- It is reliable where it survives, but not uniformly dense over object parts.
- It should not be interpreted as dense surface representation or control-sufficient visual state.
- Next diagnostic naturally asks why key-aware dense coverage fails, leading to Q6.

Known bad answers:

- "The system solved dense 3D perception."
- "Just train longer."
- "The main issue is near-zero disparity collapse."
- "Add a planner or memory module."

