The answer has been saved to `answer.md` and the concise version printed to stdout.

**Summary of findings:**

The Q5 evidence shows a **split result**: the pipeline achieves high-precision (99.98%), broadly distributed (90.8% cell coverage) correspondences with no near-zero-disparity collapse — but these correspondences are **not dense enough at the object-part level**. Only 77.5% of keyboard keys have at least one accurate survivor (need 100%), and only 70% of keys reach the local density threshold (need 90%). 

The failure is structural, not a matter of model capacity — Q6 shows that 85.9% of key-surface candidates are already pairwise-OK before the consistency filter, but 68% of those are rejected due to triangulation amplification of subpixel errors. The next step should target this specific failure mode with a physical-prior intervention (motion-conditioned matching or depth-uncertainty-aware filtering), not larger models or more data.
