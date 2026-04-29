from pathlib import Path

from .store import read_yaml, require_workspace, utc_now, write_yaml


def default_agents():
    return [
        {
            "id": "agent_orchestrator",
            "role": "orchestrator",
            "description": "Plans runs, selects skills, calls allowed tools, and writes summaries.",
            "skill_refs": ["research.review"],
            "tool_scope": ["search_stub.query"],
            "context_scope": ["project", "session", "skill", "tools"],
            "permission_scope": ["read_only"],
            "model_profile": "deterministic-local",
            "output_schema": "run_summary",
        },
        {
            "id": "agent_auditor",
            "role": "auditor",
            "description": "Checks run records, artifacts, tool calls, and memory candidates.",
            "skill_refs": ["run.audit", "memory.curate"],
            "tool_scope": [],
            "context_scope": ["run_records", "artifacts", "memory_candidates"],
            "permission_scope": ["read_only"],
            "model_profile": "deterministic-local",
            "output_schema": "audit_note",
        },
    ]


def _agent_path(base, agent_id):
    return Path(base) / "agents" / f"{agent_id}.yaml"


def write_default_agents(root):
    base = require_workspace(root)
    for agent in default_agents():
        path = _agent_path(base, agent["id"])
        if not path.exists():
            record = dict(agent)
            record["created_at"] = utc_now()
            record["updated_at"] = record["created_at"]
            write_yaml(path, record)


def list_agents(root):
    base = require_workspace(root)
    agents = []
    for path in sorted((base / "agents").glob("*.yaml")):
        agents.append(read_yaml(path, {}))
    return agents


def load_agent(root, agent_id):
    base = require_workspace(root)
    agent = read_yaml(_agent_path(base, agent_id), None)
    if not agent:
        raise RuntimeError(f"Agent not found: {agent_id}")
    return agent


def create_agent(root, agent_id, role):
    base = require_workspace(root)
    path = _agent_path(base, agent_id)
    if path.exists():
        raise RuntimeError(f"Agent already exists: {agent_id}")
    now = utc_now()
    record = {
        "id": agent_id,
        "role": role,
        "description": f"Project-local {role} agent.",
        "skill_refs": [],
        "tool_scope": [],
        "context_scope": ["project", "session", "run_records"],
        "permission_scope": ["read_only"],
        "model_profile": "deterministic-local",
        "output_schema": "agent_step_note",
        "created_at": now,
        "updated_at": now,
    }
    write_yaml(path, record)
    return record


def _save_agent(root, agent):
    base = require_workspace(root)
    agent["updated_at"] = utc_now()
    write_yaml(_agent_path(base, agent["id"]), agent)
    return agent


def add_agent_list_value(root, agent_id, field, value):
    agent = load_agent(root, agent_id)
    values = list(agent.get(field, []))
    if value not in values:
        values.append(value)
    agent[field] = values
    return _save_agent(root, agent)


def remove_agent_list_value(root, agent_id, field, value):
    agent = load_agent(root, agent_id)
    agent[field] = [item for item in agent.get(field, []) if item != value]
    return _save_agent(root, agent)


def set_agent_model(root, agent_id, model_profile):
    agent = load_agent(root, agent_id)
    agent["model_profile"] = model_profile
    return _save_agent(root, agent)


def agent_snapshot(agent, joined_at):
    return {
        "agent_id": agent["id"],
        "role": agent["role"],
        "description": agent.get("description", ""),
        "status": "active",
        "joined_at": joined_at,
        "skill_refs": list(agent.get("skill_refs", [])),
        "tool_scope": list(agent.get("tool_scope", [])),
        "context_scope": list(agent.get("context_scope", [])),
        "permission_scope": list(agent.get("permission_scope", [])),
        "model_profile": agent.get("model_profile", "deterministic-local"),
        "output_schema": agent.get("output_schema", "agent_step_note"),
    }
