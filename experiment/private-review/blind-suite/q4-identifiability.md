# Private Review: Q4 Correspondence Identifiability

Expected answer:

- Reliable local correspondence requires representational discriminability, temporal stability, local spatial distinctiveness, and conditional matching success.
- Temporal stability is mostly adequate in the short windows.
- Local spatial distinctiveness and coverage are central bottlenecks.
- Trainability, reconstruction, or lower loss do not automatically imply physical correspondence correctness.
- Later experiments should preserve the condition decomposition rather than treating feature quality as one scalar.

Known bad answers:

- "The feature extractor is enough because a top-1 number is high."
- "Temporal instability is the main failure when the evidence points elsewhere."
- "Reconstruction quality proves correspondence."
- "Use any larger pretrained model without testing local distinctiveness and coverage."

