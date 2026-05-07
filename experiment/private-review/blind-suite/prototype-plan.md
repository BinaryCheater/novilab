# Private Review: Prototype Plan

Expected answer:

- One physical prior, meaning one bottom-level physical rule or constraint, not a stack of all priors.
- A concrete falsifiable claim tied to Q6 or Q7 evidence.
- Minimal implementation surface, likely a bounded matcher/filter/aggregation change rather than a new full system.
- Metrics should include key-aware dense coverage or cube dense 3D metrics, not only training loss.
- A smoke test should verify the code path on a small known run.
- An ablation should compare against current local appearance matching and/or hard consistency filtering.
- Failure interpretation should say what to conclude if the prototype does not improve the target metric.

Known bad answers:

- Build a full dense SLAM system.
- Add planner, memory, VLA, or world model without evidence.
- Evaluate only by lower training loss.
- Skip failure attribution.
