# Private Review: Q5 Dense Primitive Verdict

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

