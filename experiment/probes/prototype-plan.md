# Probe: Minimal Prototype Plan

## Task Prompt

Using the EmbodiedAI visual audit, propose one minimal next prototype. Do not write code.

The plan must include:

- physical claim;
- source failure evidence;
- minimal implementation surface;
- metrics;
- smoke test;
- ablation;
- failure interpretation;
- what not to add.

## Allowed Source Files

- `/Users/cyan/Project/EmbodiedAI/visual/foundation/docs/current_implementation_and_failure_audit.md`
- `/Users/cyan/Project/EmbodiedAI/visual/foundation/docs/q6_failure_attribution.md`
- `/Users/cyan/Project/EmbodiedAI/visual/foundation/docs/q7_colored_cube_dense_3d.md`

## Reviewer Notes

Expected plan shape:

- one physical prior, not a stack of all priors;
- concrete falsifiable claim;
- clear relation to Q6 or Q7;
- no broad architecture expansion;
- explicit ablation against current local appearance matching.

Known bad answers:

- build a full dense SLAM system;
- add planner, memory, VLA, or world model without evidence;
- evaluate only by lower training loss;
- skip failure attribution.

