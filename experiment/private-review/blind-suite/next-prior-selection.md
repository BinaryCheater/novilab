# Private Review: Next Prior Selection

Expected answer:

- The answer should choose exactly one next prior and bind it to a source failure.
- Strong candidates include motion-conditioned matching with inverse-depth uncertainty, depth-uncertainty-aware filtering, boundary-gated surface aggregation, or active parallax.
- The minimal claim must be narrower than "solve visual intelligence."
- The prototype must include a falsification condition and an ablation against current local appearance matching or hard consistency filtering.
- It should explicitly defer planners, memory, world models, and broad VLA stacks until dense, reliable visual state is better characterized.

Known bad answers:

- "Add a large vision foundation model" without an explicit failure target.
- "Add memory" before defining what state must persist.
- "Add surface smoothness" without boundary preservation.
- "Use active observation" without a controlled parallax falsification test.
- Proposing all priors at once.

