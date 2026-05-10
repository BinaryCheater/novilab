# Probe: Q7 Generalization

## Task Prompt

Read the allowed source files and answer:

1. Does the colored-cube result show that keyboard failure was only a repeated-key artifact?
2. What are the dominant cube failure modes?
3. What does Q7 imply about local appearance descriptors and dense point identity?
4. What next physical priors are justified?

## Allowed Source Files

- `/Users/cyan/Project/EmbodiedAI/visual/foundation/docs/q7_colored_cube_dense_3d.md`
- `/Users/cyan/Project/EmbodiedAI/visual/foundation/reports/q7_colored_cube_dense_3d.json`
- `/Users/cyan/Project/EmbodiedAI/visual/foundation/docs/current_implementation_and_failure_audit.md`

## Reviewer Notes

Expected answer:

- Q7 shows the issue is not only keyboard repetition.
- The pipeline also fails on a non-planar weakly textured object.
- Dominant failures include same-face textureless ambiguity and same-face edge sliding.
- Non-planar geometry and face-level color are not enough to create dense point identity.
- Next priors should include motion-conditioned matching, depth uncertainty, surface-aware aggregation, boundary preservation, and active parallax.

Known bad answers:

- "Use semantic object recognition."
- "The cube is solved because face landmark coverage is high."
- "More epochs should solve dense correspondence."
- "Add surface smoothness" without boundary or occlusion gates.

