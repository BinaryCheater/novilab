import json
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

    write_default_agents(root)
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
