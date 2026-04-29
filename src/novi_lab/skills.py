from pathlib import Path

import yaml

from .store import novi_dir


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
