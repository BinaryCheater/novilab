from pathlib import Path

import yaml

from .store import novi_dir


DEFAULT_PROJECT_SKILLS = {
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
