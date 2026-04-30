import json
import shutil
from difflib import unified_diff
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import yaml

from .ids import new_id


WORKSPACE = ".novi"


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def novi_dir(root):
    return Path(root) / WORKSPACE


def require_workspace(root):
    path = novi_dir(root)
    if not path.exists():
        raise RuntimeError("Novi workspace not initialized. Run `novi init` first.")
    return path


def read_yaml(path, default=None):
    if not Path(path).exists():
        return default
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or default


def write_yaml(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)


def append_jsonl(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(data, sort_keys=True) + "\n")


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def append_session_message(root, session_id, role, content, run_id=None):
    session = load_session(root, session_id)
    if not session:
        raise RuntimeError(f"Session not found: {session_id}")
    message = {
        "id": new_id("msg"),
        "session_id": session_id,
        "run_id": run_id,
        "role": role,
        "content": content,
        "created_at": utc_now(),
    }
    append_jsonl(session["message_log_path"], message)
    return message


def session_messages(root, session_id, limit=None):
    session = load_session(root, session_id)
    if not session:
        raise RuntimeError(f"Session not found: {session_id}")
    messages = read_jsonl(session["message_log_path"])
    if limit is None:
        return messages
    return messages[-limit:]


def content_hash(path):
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def init_workspace(root):
    base = novi_dir(root)
    for relative in [
        "specs",
        "sessions",
        "runs",
        "memory/candidates",
        "artifacts",
        "artifacts/imports",
        "contributions",
        "knowledge",
        "knowledge/raw",
        "knowledge/accepted",
        "knowledge/analysis",
        "knowledge/topics",
        "knowledge/syntheses",
        "workflows",
        "approvals",
        "skills",
        "agents",
        "tools",
    ]:
        (base / relative).mkdir(parents=True, exist_ok=True)

    now = utc_now()
    config_path = base / "novi.yaml"
    if not config_path.exists():
        write_yaml(
            config_path,
            {
                "version": 1,
                "workspace": str(Path(root).resolve()),
                "created_at": now,
                "updated_at": now,
                "active_session_id": None,
            },
        )
    write_yaml(
        base / "specs" / "project.yaml",
        {"name": Path(root).resolve().name, "created_at": now},
    )
    write_yaml(
        base / "specs" / "policies.yaml",
        {
            "tool_defaults": {
                "read_only": "allowed",
                "write_local": "workspace_only",
                "shell": "approval_required",
                "network": "disabled",
                "external_side_effect": "disabled",
                "physical_world": "disabled",
            }
        },
    )
    for memory_file in ["project.md", "procedural.jsonl", "episodic.jsonl"]:
        path = base / "memory" / memory_file
        if not path.exists():
            path.write_text("" if path.suffix == ".jsonl" else "# Project Memory\n", encoding="utf-8")
    from .agents import write_default_agents
    from .workflows import write_default_workflows

    write_default_agents(root)
    write_default_workflows(root)
    return base


def project_config(root):
    base = require_workspace(root)
    return read_yaml(base / "novi.yaml", {})


def update_project_config(root, **updates):
    base = require_workspace(root)
    config_path = base / "novi.yaml"
    config = read_yaml(config_path, {})
    config.update(updates)
    config["updated_at"] = utc_now()
    write_yaml(config_path, config)
    return config


def create_session(root, title):
    base = require_workspace(root)
    now = utc_now()
    session_id = new_id("sess")
    session_dir = base / "sessions" / session_id
    session_dir.mkdir(parents=True)
    record = {
        "id": session_id,
        "title": title,
        "workspace": str(Path(root).resolve()),
        "status": "active",
        "created_at": now,
        "updated_at": now,
        "active_skills": [],
        "active_agents": ["agent_orchestrator", "agent_auditor"],
        "current_run_id": None,
        "run_ids": [],
        "summary_path": str(session_dir / "summary.md"),
        "message_log_path": str(session_dir / "messages.jsonl"),
    }
    write_yaml(session_dir / "session.yaml", record)
    (session_dir / "summary.md").write_text(f"# {title}\n\nNo runs yet.\n", encoding="utf-8")
    (session_dir / "messages.jsonl").write_text("", encoding="utf-8")
    update_project_config(root, active_session_id=session_id)
    return record


def session_dir(root, session_id):
    return require_workspace(root) / "sessions" / session_id


def load_session(root, session_id):
    return read_yaml(session_dir(root, session_id) / "session.yaml", {})


def save_session(root, session):
    session["updated_at"] = utc_now()
    write_yaml(session_dir(root, session["id"]) / "session.yaml", session)


def active_session(root):
    session_id = project_config(root).get("active_session_id")
    if not session_id:
        raise RuntimeError("No active session. Run `novi session create <title>` first.")
    return load_session(root, session_id)


def list_sessions(root):
    base = require_workspace(root)
    sessions = []
    for path in sorted((base / "sessions").glob("*/session.yaml")):
        sessions.append(read_yaml(path, {}))
    return sessions


def create_run_dir(root, run_id):
    path = require_workspace(root) / "runs" / run_id
    (path / "artifacts").mkdir(parents=True, exist_ok=True)
    (path / "events.jsonl").write_text("", encoding="utf-8")
    (path / "tool_calls.jsonl").write_text("", encoding="utf-8")
    return path


def load_run(root, run_id):
    return read_yaml(require_workspace(root) / "runs" / run_id / "run.yaml", {})


def list_artifacts(root):
    base = require_workspace(root)
    artifacts = []
    for path in sorted((base / "artifacts").glob("*.yaml")):
        artifacts.append(read_yaml(path, {}))
    for path in sorted((base / "runs").glob("*/artifacts/*.yaml")):
        artifacts.append(read_yaml(path, {}))
    return artifacts


def load_artifact(root, artifact_id):
    base = require_workspace(root)
    paths = [base / "artifacts" / f"{artifact_id}.yaml", *sorted((base / "runs").glob(f"*/artifacts/{artifact_id}.yaml"))]
    for path in paths:
        artifact = read_yaml(path, None)
        if artifact:
            return artifact
    raise RuntimeError(f"Artifact not found: {artifact_id}")


def accepted_knowledge(root):
    base = require_workspace(root)
    records = []
    for record in read_jsonl(base / "knowledge" / "index.jsonl"):
        accepted_path = Path(record.get("accepted_path", ""))
        record = dict(record)
        record["content"] = accepted_path.read_text(encoding="utf-8") if accepted_path.exists() else ""
        records.append(record)
    return records


def load_accepted_knowledge(root, knowledge_id):
    for record in accepted_knowledge(root):
        if record.get("id") == knowledge_id:
            return record
    raise RuntimeError(f"Accepted knowledge not found: {knowledge_id}")


def import_knowledge_file(root, source):
    base = require_workspace(root)
    source_path = Path(source)
    if not source_path.is_file():
        raise RuntimeError(f"Import source not found or not a file: {source}")
    now = utc_now()
    artifact_id = new_id("art")
    contribution_id = new_id("contrib")
    artifact_copy = base / "artifacts" / "imports" / f"{artifact_id}-{source_path.name}"
    artifact_copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, artifact_copy)
    artifact = {
        "id": artifact_id,
        "type": "knowledge_import",
        "path": str(artifact_copy),
        "source_path": str(source_path.resolve()),
        "created_at": now,
        "hash": content_hash(artifact_copy),
        "hash_algorithm": "sha256",
        "mime_type": "text/markdown" if source_path.suffix.lower() == ".md" else "application/octet-stream",
        "size_bytes": artifact_copy.stat().st_size,
    }
    write_yaml(base / "artifacts" / f"{artifact_id}.yaml", artifact)
    contribution = {
        "id": contribution_id,
        "type": "knowledge_import",
        "status": "pending",
        "title": source_path.name,
        "source": str(source_path.resolve()),
        "target": "knowledge_vault",
        "artifact_id": artifact_id,
        "created_at": now,
        "updated_at": now,
        "review_state": "pending",
    }
    write_yaml(base / "contributions" / f"{contribution_id}.yaml", contribution)
    return contribution, artifact


def list_contributions(root):
    base = require_workspace(root)
    contributions = []
    for path in sorted((base / "contributions").glob("*.yaml")):
        contributions.append(read_yaml(path, {}))
    return contributions


def load_contribution(root, contribution_id):
    path = require_workspace(root) / "contributions" / f"{contribution_id}.yaml"
    contribution = read_yaml(path, None)
    if not contribution:
        raise RuntimeError(f"Contribution not found: {contribution_id}")
    return contribution, path


def _is_relative_to(path, parent):
    try:
        Path(path).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False


def target_type_for_path(root, target):
    base = require_workspace(root)
    target_path = Path(target).resolve()
    allowed = {
        "knowledge": base / "knowledge",
        "workflow": base / "workflows",
        "skill": base / "skills",
    }
    for target_type, parent in allowed.items():
        if _is_relative_to(target_path, parent):
            return target_type
    raise RuntimeError("Patch target must be under .novi/knowledge, .novi/workflows, or .novi/skills.")


def _relative_to_root(root, path):
    return str(Path(path).resolve().relative_to(Path(root).resolve()))


def _text_hash(text):
    return sha256(text.encode("utf-8")).hexdigest()


def _write_patch_file(path, target_relative_path, before, after):
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    patch = "".join(
        unified_diff(
            before_lines,
            after_lines,
            fromfile=f"a/{target_relative_path}",
            tofile=f"b/{target_relative_path}",
        )
    )
    Path(path).write_text(patch, encoding="utf-8")


def create_document_patch_contribution(
    root,
    title,
    target,
    proposed_content,
    source_refs,
    source_actor="agent",
    rationale=None,
):
    base = require_workspace(root)
    target_path = Path(target).resolve()
    target_type = target_type_for_path(root, target_path)
    target_relative_path = _relative_to_root(root, target_path)
    before = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
    contribution_id = new_id("contrib")
    contribution_dir = base / "contributions" / contribution_id
    contribution_dir.mkdir(parents=True, exist_ok=True)
    patch_path = contribution_dir / "proposed.patch"
    proposed_path = contribution_dir / "proposed.md"
    rationale_path = contribution_dir / "rationale.md"
    _write_patch_file(patch_path, target_relative_path, before, proposed_content)
    proposed_path.write_text(proposed_content, encoding="utf-8")
    if rationale:
        rationale_path.write_text(rationale, encoding="utf-8")
    now = utc_now()
    contribution = {
        "id": contribution_id,
        "type": "document_patch",
        "status": "pending",
        "review_state": "pending",
        "title": title,
        "target": target_relative_path,
        "target_type": target_type,
        "target_path": str(target_path),
        "target_base_hash": _text_hash(before),
        "target_exists": target_path.exists(),
        "patch_path": str(patch_path),
        "proposed_content_path": str(proposed_path),
        "rationale_path": str(rationale_path) if rationale else None,
        "source_actor": source_actor,
        "source_refs": source_refs,
        "created_at": now,
        "updated_at": now,
    }
    write_yaml(base / "contributions" / f"{contribution_id}.yaml", contribution)
    return contribution


def check_patch_contribution(root, contribution_id, write_result=True):
    contribution, path = load_contribution(root, contribution_id)
    if contribution.get("type") != "document_patch":
        raise RuntimeError(f"Contribution is not a patch contribution: {contribution_id}")
    result = {"status": "would_apply", "checked_at": utc_now(), "changed_files": []}
    try:
        target_type_for_path(root, contribution["target_path"])
        if contribution.get("source_actor") in {"agent", "external_worker"} and not contribution.get("source_refs"):
            raise RuntimeError("agent-generated patch contribution is missing source refs")
        proposed_path = Path(contribution["proposed_content_path"])
        if not proposed_path.exists():
            raise RuntimeError("proposed content is missing")
        target_path = Path(contribution["target_path"])
        current = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
        if _text_hash(current) != contribution.get("target_base_hash"):
            raise RuntimeError("target changed since patch generation")
        result["changed_files"] = [contribution["target"]]
    except RuntimeError as exc:
        result = {"status": "conflict", "checked_at": utc_now(), "reason": str(exc), "changed_files": []}
    if write_result:
        contribution["check_result"] = result
        contribution["updated_at"] = utc_now()
        write_yaml(path, contribution)
    return result


def apply_patch_contribution(root, contribution_id, reviewer="local_user"):
    contribution, path = load_contribution(root, contribution_id)
    if contribution.get("status") != "pending":
        raise RuntimeError(f"Contribution is already {contribution.get('status')}: {contribution_id}")
    result = check_patch_contribution(root, contribution_id, write_result=False)
    now = utc_now()
    if result["status"] != "would_apply":
        contribution["status"] = "conflict"
        contribution["review_state"] = "conflict"
        contribution["conflict_reason"] = result.get("reason", "patch check failed")
        contribution["check_result"] = result
        contribution["updated_at"] = now
        write_yaml(path, contribution)
        raise RuntimeError(f"Patch contribution conflict: {contribution['conflict_reason']}")
    target_path = Path(contribution["target_path"])
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(Path(contribution["proposed_content_path"]).read_text(encoding="utf-8"), encoding="utf-8")
    contribution["status"] = "accepted"
    contribution["review_state"] = "accepted"
    contribution["reviewed_by"] = reviewer
    contribution["reviewed_at"] = now
    contribution["merged_at"] = now
    contribution["changed_files"] = result["changed_files"]
    contribution["check_result"] = result
    contribution["updated_at"] = now
    write_yaml(path, contribution)
    return contribution


def request_changes_contribution(root, contribution_id, reason, reviewer="local_user"):
    contribution, path = load_contribution(root, contribution_id)
    if contribution.get("status") != "pending":
        raise RuntimeError(f"Contribution is already {contribution.get('status')}: {contribution_id}")
    now = utc_now()
    contribution["status"] = "changes_requested"
    contribution["review_state"] = "changes_requested"
    contribution["reviewed_by"] = reviewer
    contribution["reviewed_at"] = now
    contribution["review_comment"] = reason
    contribution["updated_at"] = now
    write_yaml(path, contribution)
    return contribution


def _write_accepted_knowledge(root, contribution, reviewer, reviewed_at):
    if contribution.get("type") != "knowledge_import":
        return None
    base = require_workspace(root)
    artifact = load_artifact(root, contribution["artifact_id"])
    source_path = Path(artifact["path"])
    raw_path = base / "knowledge" / "raw" / f"{contribution['id']}-{Path(contribution['title']).name}"
    accepted_path = base / "knowledge" / "accepted" / f"{contribution['id']}.md"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    accepted_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, raw_path)
    raw_text = raw_path.read_text(encoding="utf-8", errors="replace")
    accepted_text = "\n".join(
        [
            "# Accepted Knowledge",
            "",
            f"- Contribution: {contribution['id']}",
            f"- Source artifact: {artifact['id']}",
            f"- Source path: {artifact.get('source_path', '-')}",
            f"- Reviewed by: {reviewer}",
            f"- Reviewed at: {reviewed_at}",
            "",
            "## Content",
            "",
            raw_text.strip(),
            "",
        ]
    )
    accepted_path.write_text(accepted_text, encoding="utf-8")
    record = {
        "id": contribution["id"],
        "type": "accepted_knowledge",
        "title": contribution.get("title"),
        "source_artifact_id": artifact["id"],
        "raw_path": str(raw_path),
        "accepted_path": str(accepted_path),
        "reviewed_by": reviewer,
        "reviewed_at": reviewed_at,
    }
    append_jsonl(base / "knowledge" / "index.jsonl", record)
    return record


def decide_contribution(root, contribution_id, status, reviewer="local_user"):
    contribution, path = load_contribution(root, contribution_id)
    if contribution.get("status") != "pending":
        raise RuntimeError(f"Contribution is already {contribution.get('status')}: {contribution_id}")
    now = utc_now()
    knowledge_record = None
    if status == "accepted":
        knowledge_record = _write_accepted_knowledge(root, contribution, reviewer, now)
    contribution["status"] = status
    contribution["review_state"] = status
    contribution["reviewed_by"] = reviewer
    contribution["reviewed_at"] = now
    contribution["updated_at"] = now
    if knowledge_record:
        contribution["accepted_knowledge_path"] = knowledge_record["accepted_path"]
        contribution["knowledge_index_id"] = knowledge_record["id"]
    write_yaml(path, contribution)
    return contribution


def memory_candidates(root):
    base = require_workspace(root)
    candidates = []
    for path in sorted((base / "memory" / "candidates").glob("*.yaml")):
        candidates.append(read_yaml(path, {}))
    return candidates


def load_memory_candidate(root, candidate_id):
    path = require_workspace(root) / "memory" / "candidates" / f"{candidate_id}.yaml"
    candidate = read_yaml(path, None)
    if not candidate:
        raise RuntimeError(f"Memory candidate not found: {candidate_id}")
    return candidate, path


def decide_memory_candidate(root, candidate_id, status, reviewer="local_user"):
    base = require_workspace(root)
    candidate, path = load_memory_candidate(root, candidate_id)
    if candidate.get("status") != "proposed":
        raise RuntimeError(f"Memory candidate is already {candidate.get('status')}: {candidate_id}")
    now = utc_now()
    candidate["status"] = status
    candidate["reviewed_by"] = reviewer
    candidate["reviewed_at"] = now
    write_yaml(path, candidate)
    if status == "accepted":
        accepted = {
            "id": candidate["id"],
            "type": candidate["type"],
            "subject": candidate["subject"],
            "claim": candidate["claim"],
            "accepted_at": now,
            "reviewed_by": reviewer,
            "evidence": candidate.get("evidence", []),
        }
        if candidate["type"] == "project":
            with (base / "memory" / "project.md").open("a", encoding="utf-8") as handle:
                handle.write(f"\n- {candidate['claim']} ({candidate['id']})\n")
        elif candidate["type"] == "procedural":
            append_jsonl(base / "memory" / "procedural.jsonl", accepted)
        else:
            append_jsonl(base / "memory" / "episodic.jsonl", accepted)
    return candidate
