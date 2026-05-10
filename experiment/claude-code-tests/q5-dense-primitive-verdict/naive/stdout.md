Done. The answer has been saved to `answer.md` and printed above. Here's the summary:

---

**1. Has the pipeline produced a dense, control-useful visual primitive field?**
**No — partially.** Split result: coarse image-level coverage **passes**, key-aware dense primitive coverage **fails**.

**2. Evidence:** Survivors are very precise (0.9998 GT precision), broadly distributed at 8×8 cell level (0.9083 cell coverage), with no near-zero-disparity collapse. But only 77.5% of 40 keys have an accurate landmark (needs 100%), and only 70% of keys reach local density threshold (needs 90%).

**3. Do not conclude:** The system has a dense surface field, the model is useless, Q5 validates downstream control capabilities, training had no effect, r=4 is the bottleneck, or disparity/depth artifacts caused the failure.

**4. Next diagnostic question: Q6** — "Why do the current keyboard correspondences fail to become key-aware dense?" This decomposes the missing density into causal categories (search window, GT visibility, pairwise matching errors, later consistency filter rejection). Q7 then generalizes to a weakly textured cube.
