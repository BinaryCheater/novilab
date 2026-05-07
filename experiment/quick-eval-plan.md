# EmbodiedAI Visual Research Workflow Probe Plan

Date: 2026-05-07

## Purpose

Use the EmbodiedAI visual foundation materials as a realistic research-workflow probe. The point is to understand how agents behave when asked to interpret evidence, diagnose failures, choose next physical priors, and propose minimal prototype plans.

This is a product and method calibration exercise:

- validate Novi features and gaps;
- improve prompts and skills;
- compare with Claude Code directly;
- test whether physical-prior research discipline can be injected into agent workflows.

## Non-Goals

- No paper-grade benchmark claim.
- No public leaderboard.
- No automatic large-scale scoring in the first pass.
- No claim that Novi outperforms Claude Code.
- No automatic edits to `/Users/cyan/Project/EmbodiedAI`.
- No cross-task self-improving skill updates during a comparison batch.

## Comparison Conditions

Run each selected probe under a small number of controlled Claude Code conditions first:

| ID | Condition | Purpose |
| --- | --- | --- |
| A | Claude Code naive | Establish raw baseline behavior. |
| B | Claude Code with physical-prior prompt | Test whether a better prompt is already enough. |
| C | Claude Code with draft skill/SOP | Test reusable research-method injection after A/B are understood. |
| D | Novi workflow probe | Test whether external staged records and gates add value after Claude Code behavior is understood. |

For the first pass, run only A and B. Codex is not part of the current comparison.

## Probe Set

Start with six probes:

1. Q4 interpretation: identify when local features support correspondence.
2. Q5 dense primitive verdict: distinguish coarse coverage from key-aware dense success.
3. Q6 failure attribution: explain non-dense keyboard failure without blaming search radius.
4. Q7 generalization: explain weakly textured cube failure and what it says about local descriptors.
5. Next-prior selection: choose the minimal next physical prior from current audit evidence.
6. Prototype plan: propose a falsifiable next implementation plan without coding.

## Evaluation Dimensions

Human reviewers should score or annotate:

- evidence use: does the output cite the right metrics or report claims?
- non-overclaiming: does it avoid saying the system solved dense 3D or control?
- failure attribution: does it identify the right physical bottleneck?
- minimality: does it avoid adding unsupported machinery?
- next-step quality: is the proposed experiment falsifiable?
- prompt/skill dependence: what improved only after guidance?
- product gap: what Novi feature would have helped?

## First Batch Procedure

1. Select one clean test folder under `claude-code-tests/`.
2. Start Claude Code from that folder, not from the repository root.
3. Paste the folder's `prompt-to-paste.md`.
4. Let Claude save its result to the local `answer.md`.
5. Copy the completed answer into `runs/YYYY-MM-DD/<probe-id>/<condition-id>.md` if you want a central record.
6. Summarize differences in `analysis/YYYY-MM-DD-<probe-id>.md`.
7. Update prompt and skill notes only after the batch is complete.

## Expected Learning

The first useful outcome is a map of agent failure patterns:

- overclaiming sparse landmarks as dense visual primitives;
- treating reprojection loss decrease as physical correctness;
- blaming search radius despite Q6 evidence;
- recommending larger models without binding to failure modes;
- missing the distinction between appearance matching and physical identity;
- proposing surface smoothness without boundary/occlusion gates;
- ignoring active observability and uncertainty.

These patterns should drive prompt, skill, workflow, and Novi product changes.
