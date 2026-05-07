# Private Review: Q2 Geometry Closure

Expected answer:

- Q2 validates projection, backprojection, triangulation, and reprojection closure under ideal or controlled geometry.
- A passing Q2 increases confidence that later failures are not simply broken projection math.
- It does not prove robustness when image matching is noisy.
- Small pairwise visual errors can still be amplified by triangulation under small baselines.

Known bad answers:

- "Q2 means visual matching is solved."
- "Q2 proves the learned representation is physically correct."
- "Triangulation can no longer be a bottleneck."
- "Control can now use the geometry directly."

