# Research Iteration Loop

This loop is for quickly turning a topic, documents, notes, and experiment records into
actionable hypotheses, next experiments, and reviewable physical prior candidates.

## What Novi Owns

Novi owns:

- sessions, tasks, runs, traces, and artifacts;
- skill and workflow instructions;
- reviewable contributions and accepted knowledge;
- thin policy-checked wrappers for tools that must be audited.

## What DeepAgents Owns

DeepAgents owns:

- model execution;
- agent loop behavior;
- virtual working-file creation;
- model-side tool selection and tool-call orchestration.

Novi does not try to rebuild a full research tool ecosystem in this loop. When tools are
needed, prefer exposing existing DeepAgents-compatible tools or adding thin Novi wrappers
only where audit and policy boundaries matter.

## Configure A Model

```bash
novi configure model siliconflow \
  --model "deepseek-ai/DeepSeek-V4-Flash" \
  --api-key "YOUR_API_KEY"
```

Or use any OpenAI-compatible chat provider:

```bash
novi configure model openai-chat \
  --model "MODEL_NAME" \
  --base-url "https://provider.example.com/v1" \
  --api-key "YOUR_API_KEY"
```

Check before running:

```bash
novi doctor model
```

For SiliconCloud, prefer a model whose OpenAI-compatible tool calls are parsed correctly
by LangChain and DeepAgents. `MiniMaxAI/MiniMax-M2.5` has been verified with Novi tool
calls. If a model returns empty responses or `finish_reason=tool_calls` without executable
tool calls, switch models before debugging Novi.

## Run From A Topic

```bash
novi task "从接触先验角度分析这些材料，设计下一轮最小实验，并抽取隐含物理先验" \
  --workflow research-iteration \
  --kernel deepagents \
  --rounds 1
```

One round means one complete research iteration. Internally, the current
`research-iteration` workflow runs two agent steps:

1. `frame_topic`: frame the topic and map evidence.
2. `iterate_and_extract`: propose the next experiment iteration and extract physical
   prior candidates.

`--steps` still exists for internal debugging or partial workflow execution, but day-to-day
research should use `--rounds`.

Expected DeepAgents working files include:

- `topic-brief.md`
- `evidence-map.md`
- `hypotheses.md`
- `experiment-plan.md`
- `iteration-log.md`
- `physical-priors.md`
- `next-actions.md`
- `proposals.md`

Novi exports these files as run artifacts.

## Add Documents Or Experiment Records

```bash
novi ingest notes/contact-prior-notes.md \
  --task task_... \
  --hint "Use this as evidence for the contact-prior research iteration."
```

For PDFs and papers, keep the original file as a source artifact and let a skill or
DeepAgents shell/tool backend extract text with project-local tools such as `pdftotext`,
PyMuPDF, Docling, Marker, or OCR. Novi should not own a custom PDF parser unless a thin
wrapper is needed for repeatability or artifact capture.

For known URLs, use `curl` or a browser/computer-use skill and store the fetched page,
cleaned text, screenshot, or notes as artifacts. Use Tavily or another search API only
when broad web discovery is actually needed.

For experiment results, start with a result packet rather than a rigid schema:

```markdown
---
type: experiment_result
title: Contact-prior trial 001
status: draft
topic: contact-prior
artifacts:
  - data/raw/trial-001.csv
  - plots/trial-001-pressure.png
---

# Contact-prior trial 001

## What Was Tried

Natural-language setup, parameters, and procedure.

## Observations

Raw outcomes, anomalies, failure modes, and notable measurements.

## Interpretation

What this appears to support or weaken, including uncertainty.

## Next Action

The smallest useful follow-up.
```

Leave unclear structure in natural language. The next `research-iteration` run can extract
claims, observations, interpretations, and prior updates from the packet.

Review any proposed patches before continuing:

```bash
novi review --task task_... --check --agent
novi accept --reviewed --task task_...
novi task continue task_... --workflow research-iteration --kernel deepagents --rounds 1
```

## Inspect Results

```bash
novi trace latest
novi output latest
novi artifact list
```

Use the exported `physical-priors.md` as a candidate list, not as accepted durable memory.
Accept only evidence-backed updates through the review path.

Use `novi task inspect task_...` to see the current workflow step, completed steps, and run
IDs. A completed `research-iteration` round should show both `frame_topic` and
`iterate_and_extract` in completed steps and two new run IDs for that round.

Do not convert every prior candidate into a structured record immediately. Use Markdown
review first; add structured prior contributions only after repeated runs show that
Markdown review is too loose.
