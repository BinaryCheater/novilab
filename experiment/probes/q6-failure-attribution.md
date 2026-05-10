# Probe: Q6 Failure Attribution

## Task Prompt

Read the allowed source files and diagnose why the keyboard correspondences fail to become key-aware dense.

Answer:

1. What is not the main cause?
2. What are the main failure modes?
3. What evidence distinguishes first-pair matching failure from later 3D consistency failure?
4. What next prior or diagnostic is justified by the evidence?

## Allowed Source Files

- `/Users/cyan/Project/EmbodiedAI/visual/foundation/docs/q6_failure_attribution.md`
- `/Users/cyan/Project/EmbodiedAI/visual/foundation/reports/q6_failure_attribution.json`
- `/Users/cyan/Project/EmbodiedAI/visual/doc/visual_foundation_meeting_catchup_cn.md`

## Reviewer Notes

Expected answer:

- Search exclusion is not the main cause: GT is visible and inside the search window; oracle can succeed.
- Many missing dense points are pairwise OK but later fail the consistency filter.
- Small frame0-to-frame1 errors can be amplified by triangulation and later reprojection.
- First-frame wrong subset is dominated by other-key confusion, especially repeated edge/corner structures.
- Good next directions include uncertainty-aware triangulation, motion-conditioned matching, and better handling of repeated structures.

Known bad answers:

- "Increase match radius."
- "The geometry code is broken."
- "The model is too small, so use a bigger model" without failure-mode evidence.
- "The later matcher is always wrong" despite evidence that later visual matches may follow GT better than the predicted reprojection.

