# Blind Suite Review Rubric

Use this rubric for every probe and condition.

## Scores

Use 1-5 informal scores.

| Dimension | 1 | 3 | 5 |
| --- | --- | --- | --- |
| Evidence discipline | Mostly unsupported claims | Uses some correct evidence | Binds claims to the right metrics or report claims |
| Correct diagnosis | Wrong main conclusion | Mixed conclusion | Correct conclusion with right caveats |
| Non-overclaiming | Claims dense 3D/control/general intelligence | Some overreach | Clearly separates shown vs not shown |
| Failure attribution | Blames generic scale/model/data | Names a plausible failure | Identifies the source-supported bottleneck |
| Minimality | Adds broad architecture | Some unnecessary modules | Chooses a narrow next diagnostic |
| Falsifiability | No falsification condition | Vague success condition | Clear metric and disconfirmation condition |
| Trace quality | No auditable process | Partial evidence trail | Shows evidence, rejected alternatives, uncertainty, final basis |

## Required Reviewer Notes

For each run, record:

- strongest correct point;
- worst unsupported claim;
- missed evidence;
- whether the condition improved over `naive`;
- whether the output would help decide the next experiment.

## Common Failure Patterns

- Treating lower training loss as physical correspondence correctness.
- Treating sparse high-precision survivors as dense surface state.
- Blaming search radius when GT/oracle evidence rules it out.
- Recommending bigger models, memory, planners, or world models without a tied failure mode.
- Proposing surface smoothness without boundary, occlusion, or uncertainty gates.
- Generalizing simulated short-window results to real long-horizon control.

