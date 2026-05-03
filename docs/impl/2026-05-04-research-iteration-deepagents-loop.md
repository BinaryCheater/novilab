# Research Iteration DeepAgents Loop

Goal: make Novi useful as a topic-driven research executor once an API-backed DeepAgents model is configured.

Architecture:

- Reuse DeepAgents for model execution, planning behavior, tool-call orchestration, and virtual working files.
- Keep Novi focused on skill/workflow protocol, run records, artifact export, review gates, and accepted knowledge.
- Avoid building new research tools in Novi unless they are thin, auditable wrappers around local policy boundaries.

Immediate implementation:

1. Add project-default skills for topic research, document evidence extraction, experiment iteration, and physical prior extraction.
2. Add a `research-iteration` workflow that moves from topic framing to evidence mapping, experiment planning, prior extraction, and review.
3. Ensure workflow step skill references are injected into run records and prompt packs so DeepAgents receives the right instructions.
4. Strengthen the workflow step output protocol with expected Markdown working files:
   - `topic-brief.md`
   - `evidence-map.md`
   - `hypotheses.md`
   - `experiment-plan.md`
   - `iteration-log.md`
   - `physical-priors.md`
   - `next-actions.md`
   - `proposals.md`
5. Add tests that prove the new workflow, skills, prompt context, and DeepAgents file artifact export work without a real API.

Explicit reuse boundary:

- DeepAgents owns model reasoning, virtual file production, and its native agent loop.
- Novi wraps only the tools it must audit and policy-check.
- Novi does not reimplement browser/search/PDF/tool ecosystems in this pass.
- External research tools can later be exposed through DeepAgents or thin Novi wrappers when audit policy requires it.

