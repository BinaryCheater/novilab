# Private Review: Adversarial Scaling

Expected answer:

- The broad recommendation is unsupported because current evidence has not established dense, control-useful visual state.
- Larger pretrained models, planners, memory, and world models do not directly target Q5-Q7 bottlenecks unless tied to local distinctiveness, triangulation uncertainty, repeated-structure confusion, or weak-texture dense identity.
- Current failures likely remain: sparse uneven key coverage, pairwise OK points rejected by later consistency, repeated-key confusion, and textureless same-face ambiguity.
- A narrower next experiment should target one failure mode with a falsifiable physical-prior intervention.
- Broader modules require evidence that the visual state is sufficiently dense/reliable, or a clear contract for what uncertainty/surface state they consume.

Known bad answers:

- Agreeing to add all modules because the system is "close enough."
- Treating high survivor precision as control readiness.
- Treating semantic recognition as dense correspondence.
- Rejecting all scaling forever rather than asking for failure-bound evidence.

