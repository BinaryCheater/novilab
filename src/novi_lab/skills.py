from pathlib import Path

import yaml

from .store import novi_dir


DEFAULT_PROJECT_SKILLS = {
    "topic.research": """---
name: topic.research
description: Frame a research topic into evidence needs, hypotheses, and concrete next actions.
---

# Topic Research

Use the topic, accepted knowledge, imported documents, prior runs, and available tools to
produce an actionable research frame.

Prefer writing `/topic-brief.md` with:

- topic definition and scope;
- current known facts;
- important unknowns;
- testable hypotheses;
- evidence needed next;
- links to run, artifact, or source identifiers when Novi provides them.

Do not claim durable knowledge directly. Put proposed knowledge, skill, or workflow changes
in `/proposals.md` for review.
""",
    "document.evidence": """---
name: document.evidence
description: Extract topic-relevant claims, evidence, assumptions, mechanisms, and uncertainty from documents or notes.
---

# Document Evidence

Treat documents, notes, and experiment logs as evidence sources. Prefer writing
`/evidence-map.md` with rows or bullets for:

- claim;
- evidence or observation;
- source reference supplied by Novi;
- assumption;
- mechanism;
- uncertainty;
- relevance to the active topic;
- what would falsify or weaken the claim.

Keep summaries short. Optimize for reusable evidence and traceable uncertainty.
""",
    "experiment.iterate": """---
name: experiment.iterate
description: Turn current evidence and hypotheses into the next minimal experiment iteration.
---

# Experiment Iterate

Design the next useful experiment iteration from the topic, evidence map, hypotheses,
and prior run outputs.

Prefer writing:

- `/hypotheses.md` for ranked hypotheses and expected observations;
- `/experiment-plan.md` for the smallest next experiment, variables, controls, measurements, and stop criteria;
- `/iteration-log.md` for the proposed trial record template and how results should be interpreted.

Assume real hardware or simulation tools may be unavailable unless Novi explicitly exposes
them. In that case, propose the next test and observation schema rather than pretending it ran.
""",
    "physics.prior.extract": """---
name: physics.prior.extract
description: Extract reviewable implicit physical prior candidates from documents, experiments, and failures.
---

# Physics Prior Extract

Identify implicit physical priors that emerged from documents, experiment plans,
observations, failures, or repeated reasoning patterns.

Prefer writing `/physical-priors.md`. Each prior candidate should include:

- prior statement;
- physical mechanism or intuition;
- supporting evidence with Novi source references;
- applicability boundary;
- counterexample or failure mode;
- confidence;
- next validation step;
- whether it should become accepted knowledge, stay tentative, or drive another experiment.

Do not write durable memory directly. Put reviewable changes in `/proposals.md`.
""",
    "document.curate": """---
name: document.curate
description: Analyze imported documents into reviewable analysis notes with source links and merge guidance.
---

# Document Curate

Read imported documents as raw evidence. Produce an analysis note that:

- summarizes the useful ideas;
- separates clear claims from ambiguous notes;
- records source references supplied by Novi;
- identifies possible target documents;
- does not modify accepted documents directly.
""",
    "document.merge": """---
name: document.merge
description: Propose reviewable Markdown document patches from imported material and analysis notes.
---

# Document Merge

Use the imported document, analysis note, and explicit target document to draft
a proposed target document. Preserve existing useful content, add source links
or provenance markers, and do not silently overwrite accepted material.

When running through Novi, return:

- `/analysis_note.md` for the analysis note;
- `/proposed.md` for the complete proposed target document when a target is provided.
""",
}


def write_default_project_skills(root):
    project_root = novi_dir(root) / "skills"
    project_root.mkdir(parents=True, exist_ok=True)
    for skill_id, text in DEFAULT_PROJECT_SKILLS.items():
        path = project_root / skill_id / "SKILL.md"
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")


def _skill_from_file(path, source):
    text = Path(path).read_text(encoding="utf-8")
    metadata = {}
    body = text
    if text.startswith("---"):
        _, frontmatter, body = text.split("---", 2)
        metadata = yaml.safe_load(frontmatter) or {}
    skill_id = metadata.get("id") or Path(path).parent.name
    description = metadata.get("description")
    if not description:
        paragraphs = [line.strip() for line in body.splitlines() if line.strip() and not line.startswith("#")]
        description = paragraphs[0] if paragraphs else ""
    return {
        "id": skill_id,
        "name": metadata.get("name", skill_id),
        "description": description,
        "body": body.strip(),
        "path": str(Path(path)),
        "source": source,
    }


def discover_skills(root):
    package_root = Path(__file__).parent / "builtin_skills"
    skills = {}
    for path in sorted(package_root.glob("*/SKILL.md")):
        spec = _skill_from_file(path, "builtin")
        skills[spec["id"]] = spec

    project_root = novi_dir(root) / "skills"
    for path in sorted(project_root.glob("*/SKILL.md")):
        spec = _skill_from_file(path, "project")
        skills[spec["id"]] = spec
    return [skills[key] for key in sorted(skills)]
