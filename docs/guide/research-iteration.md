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

## Run From A Topic

```bash
novi task "从接触先验角度分析这些材料，设计下一轮最小实验，并抽取隐含物理先验" \
  --workflow research-iteration \
  --kernel deepagents \
  --steps 2
```

The first step frames the topic and maps evidence. The second step proposes the next
experiment iteration and extracts physical prior candidates.

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

Review any proposed patches before continuing:

```bash
novi review --task task_... --check --agent
novi accept --reviewed --task task_...
novi task continue task_... --workflow research-iteration --kernel deepagents --steps 2
```

## Inspect Results

```bash
novi trace latest
novi output latest
novi artifact list
```

Use the exported `physical-priors.md` as a candidate list, not as accepted durable memory.
Accept only evidence-backed updates through the review path.

