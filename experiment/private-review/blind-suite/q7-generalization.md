# Private Review: Q7 Generalization

Expected answer:

- Q7 shows the issue is not only keyboard repetition.
- The pipeline also fails on a non-planar weakly textured object.
- Dominant failures include same-face textureless ambiguity and same-face edge sliding.
- Non-planar geometry and face-level color are not enough to create dense point identity.
- Justified priors include motion-conditioned matching, depth uncertainty, surface-aware aggregation, boundary preservation, and active parallax, but the answer should bind them to specific failures.

Known bad answers:

- "Use semantic object recognition."
- "The cube is solved because face landmark coverage is high."
- "More epochs should solve dense correspondence."
- "Add surface smoothness" without boundary or occlusion gates.

