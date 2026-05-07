# Blind Progressive Research-Judgment Suite

This suite tests whether an agent can make evidence-bound research judgments from
EmbodiedAI visual foundation materials without seeing reviewer notes or downstream
answer summaries.

The suite is deliberately harder than the original Q5-only test:

- it uses a gradual sequence from geometry sanity checks to prototype planning;
- source sets are minimal and probe-specific;
- reviewer notes live outside the public probe folders;
- runs execute from a temporary clean working directory;
- each run must preserve both `answer.md` and `trace.md`.

## Blindness Contract

Public material:

- `experiment/blind-suite/probes/<probe>/public/task.md`
- `experiment/blind-suite/probes/<probe>/public/source-files.md`
- `experiment/blind-suite/conditions/<condition>.md`

Hidden material:

- `experiment/private-review/blind-suite/<probe>.md`

Do not place expected answers, known bad answers, reviewer notes, or analysis in
the public probe folders. Do not include catch-up summary documents in a source
set unless the probe is explicitly about synthesizing those summaries.

## Conditions

| Condition | Purpose |
| --- | --- |
| `naive` | Task-only baseline. |
| `physical-prior` | Adds physical-prior research discipline without giving answers. |
| `structured-trace` | Adds a fixed audit-trace format without physical-prior hints. |

## Probe Order

1. `q1-motion-structure`
2. `q2-geometry-closure`
3. `q3-physical-identity`
4. `q4-identifiability`
5. `q5-dense-verdict`
6. `q6-failure-attribution`
7. `q7-generalization`
8. `next-prior-selection`
9. `prototype-plan`
10. `adversarial-scaling`

## Run One Probe

Prepare only:

```bash
experiment/blind-suite/scripts/run-one.sh q5-dense-verdict naive --prepare-only
```

Run Claude Code:

```bash
experiment/blind-suite/scripts/run-one.sh q5-dense-verdict naive
experiment/blind-suite/scripts/run-one.sh q5-dense-verdict physical-prior
experiment/blind-suite/scripts/run-one.sh q5-dense-verdict structured-trace
```

Run the full matrix:

```bash
experiment/blind-suite/scripts/run-matrix.sh
```

Prepare the full matrix without invoking Claude:

```bash
experiment/blind-suite/scripts/run-matrix.sh --prepare-only
```

Each run creates a temporary clean workdir under `${TMPDIR:-/tmp}` and copies the
record back to:

```text
experiment/blind-suite/runs/<run-id>/<probe>/<condition>/
```

The record contains:

- `prompt-to-paste.md`
- `source-files.md`
- `answer.md`
- `trace.md`
- `stdout.md`
- `metadata.md`

## Review

Review the output against the matching hidden key in:

```text
experiment/private-review/blind-suite/<probe>.md
```

Score each run with `experiment/blind-suite/rubric.md`.
