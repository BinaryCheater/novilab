# Probe: Q4 Interpretation

## Task Prompt

Read the allowed source files and explain what Q4 teaches about local feature correspondence.

Answer:

1. What conditions make local correspondence identifiable?
2. Which condition appears to be the main bottleneck?
3. Why is trainability or reconstruction quality not the same as physical correspondence correctness?
4. What should the next experiment preserve from Q4?

## Allowed Source Files

- `/Users/cyan/Project/EmbodiedAI/visual/foundation/docs/q4_simple_model_trainability.md`
- `/Users/cyan/Project/EmbodiedAI/visual/foundation/docs/q4a_representational_discriminability.md`
- `/Users/cyan/Project/EmbodiedAI/visual/foundation/docs/q4b_temporal_feature_stability.md`
- `/Users/cyan/Project/EmbodiedAI/visual/foundation/docs/q4c_local_spatial_distinctiveness.md`
- `/Users/cyan/Project/EmbodiedAI/visual/foundation/docs/q4d_conditional_correspondence_identifiability.md`
- `/Users/cyan/Project/EmbodiedAI/visual/doc/visual_foundation_meeting_catchup_cn.md`

## Reviewer Notes

Expected answer:

- Reliable local correspondence requires representational discriminability, temporal feature stability, local spatial distinctiveness, and conditional matching success.
- Temporal stability is mostly adequate in the current short windows.
- Local spatial distinctiveness and coverage are the bottlenecks.
- Reprojection loss decrease, feature reconstruction, or trainability do not automatically imply dense physical identity.
- Q4 gives a condition decomposition that should be preserved in later priors.

Known bad answers:

- "The feature extractor is enough because Q4d top-1 is high."
- "Temporal instability is the main failure."
- "Reconstruction quality proves correspondence."
- "Use any larger pretrained model without testing local distinctiveness and coverage."

