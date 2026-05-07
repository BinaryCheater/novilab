# Private Review: Q6 Failure Attribution

Expected answer:

- Search exclusion is not the main cause: GT is visible and inside the search window; oracle can succeed.
- Many missing dense points are pairwise OK but later fail the consistency filter.
- Small frame0-to-frame1 errors can be amplified by triangulation and later reprojection.
- First-pair wrong subsets are dominated by repeated-key confusion, especially edge/corner structures.
- Good next directions include uncertainty-aware triangulation, motion-conditioned matching, and handling repeated structures.

Known bad answers:

- "Increase match radius."
- "The geometry code is broken."
- "The model is too small, so use a bigger model" without failure-mode evidence.
- "The later matcher is always wrong" despite evidence that later visual matches may follow GT better than predicted reprojection.

