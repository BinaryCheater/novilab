# Source And Result Intake Boundary

This note records the lightweight boundary for papers, PDFs, web pages, and experiment
results in the research iteration loop.

## Decision

Keep source and result intake flexible. Do not introduce a large scientific knowledge
schema before real tasks prove it is needed.

Novi should treat PDFs, papers, web pages, notes, datasets, logs, and experiment results
as source artifacts first. DeepAgents and skills can analyze them into Markdown working
files. Reviewable knowledge changes remain explicit proposals.

## PDF And Paper Handling

Use skills and external commands instead of building a Novi-native PDF pipeline.

Preferred behavior:

- Preserve the original PDF or paper file as an artifact.
- Let an agent use available tools to extract text or structure, such as `pdftotext`,
  PyMuPDF, Docling, Marker, OCR, or a future project-local PDF skill.
- Store extracted text, summaries, figures, and citation notes as generated artifacts.
- Feed the extracted material into `document.evidence` and `research-iteration`.

Novi should only add thin wrappers when policy, artifact capture, or repeatability needs
it.

## Web Handling

Web search is not foundational for the current loop.

Preferred behavior:

- Use Tavily or another search API only when broad discovery is needed.
- Use `curl` or a browser/computer-use skill for specific known URLs.
- Store fetched pages, cleaned text, screenshots, or browser notes as artifacts.
- Keep source URLs in Markdown evidence, not in a separate hand-maintained graph.

## Experiment Result Intake

Experiment results should enter as a flexible result packet, not a rigid database row.

Minimal packet:

- a Markdown result note;
- links or paths to raw data, logs, plots, videos, configs, and scripts;
- a short natural-language description of what was tried;
- observed outcomes;
- anomalies or failure modes;
- affected hypotheses, priors, or next experiments when known.

Optional front matter is allowed only for high-value fields:

```yaml
---
type: experiment_result
title:
status: draft
topic:
artifacts:
tags:
---
```

The body carries the reasoning. If structure is unclear, leave it in natural language and
let the LLM extract useful claims, observations, and interpretations during the next run.

## Prior Contributions

Do not rush to a complex physical-prior schema.

For now:

- `physical-priors.md` is the primary working artifact.
- `proposals.md` records suggested accepted-knowledge updates.
- Human review decides what becomes accepted knowledge.

Only add structured prior contributions after repeated runs show that Markdown review is
too loose.

## Tool And Execution Boundary

Simulation, training, SSH, local scripts, and environment setup should be handled through
DeepAgents tools and skills where possible.

Novi should not rebuild simulators, trainers, package managers, or remote execution
systems. Novi only needs enough boundary control to record:

- what command/tool was used;
- where it ran;
- inputs and outputs;
- logs and produced artifacts;
- whether the result is reviewable evidence.

