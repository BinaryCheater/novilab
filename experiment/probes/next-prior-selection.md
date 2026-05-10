# Probe: Next Prior Selection

## Task Prompt

Read the current audit and propose the next physical prior to test.

Answer:

1. Which current failure does the prior target?
2. What is the minimal claim?
3. What prototype would test the claim?
4. What would falsify the claim?
5. Which tempting modules should not be added yet?

## Allowed Source Files

- `/Users/cyan/Project/EmbodiedAI/visual/foundation/docs/current_implementation_and_failure_audit.md`
- `/Users/cyan/Project/EmbodiedAI/visual/foundation/docs/index.md`
- `/Users/cyan/Project/EmbodiedAI/visual/doc/visual_foundation_meeting_catchup_cn.md`

## Reviewer Notes

Good answers should bind each proposed prior to a failure mode.

Strong candidates:

- motion-conditioned matching with inverse-depth uncertainty;
- multi-scale feature fields with boundary-localization checks;
- boundary-gated surface aggregation;
- active parallax for uncertainty reduction.

Known bad answers:

- "Add a large vision foundation model" without an explicit failure target.
- "Add memory" before defining what state must persist.
- "Add surface smoothness" without boundary preservation.
- "Use active observation" without a controlled parallax falsification test.

