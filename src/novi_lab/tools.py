import subprocess
from pathlib import Path

from .ids import new_id
from .store import read_yaml, require_workspace, utc_now, write_yaml


def builtin_tools():
    return [
        {
            "id": "search_stub.query",
            "description": "Deterministic local search stub used to validate tool records.",
            "risk": "read_only",
            "policy": "allowed",
            "input_schema": {"query": "string"},
            "output_artifacts": ["search_result_stub"],
            "expose_to": ["agent_orchestrator"],
        },
        {
            "id": "filesystem.read",
            "description": "Read a UTF-8 text file inside the Novi workspace.",
            "risk": "read_only",
            "policy": "allowed",
            "input_schema": {"path": "string"},
            "output_artifacts": ["file_text"],
            "expose_to": ["agent_orchestrator", "agent_auditor"],
        },
        {
            "id": "git.status",
            "description": "Read git status for the Novi workspace.",
            "risk": "read_only",
            "policy": "allowed",
            "input_schema": {},
            "output_artifacts": ["git_status"],
            "expose_to": ["agent_orchestrator", "agent_auditor"],
        }
    ]


def list_tools(root):
    tools = {tool["id"]: dict(tool, source="builtin") for tool in builtin_tools()}
    project_dir = require_workspace(root) / "tools"
    for path in sorted(project_dir.glob("*.yaml")):
        tool = read_yaml(path, {})
        if tool.get("id"):
            tools[tool["id"]] = dict(tool, source="project")
    return [tools[tool_id] for tool_id in sorted(tools)]


def load_tool(root, tool_id):
    for tool in list_tools(root):
        if tool["id"] == tool_id:
            return tool
    raise RuntimeError(f"Tool not found: {tool_id}")


def _tool_path(base, tool_id):
    safe_id = tool_id.replace("/", "_").replace(".", "_")
    return Path(base) / "tools" / f"{safe_id}.yaml"


def expose_tool_to_agent(root, tool_id, agent_id):
    base = require_workspace(root)
    tool = dict(load_tool(root, tool_id))
    tool.pop("source", None)
    exposed = list(tool.get("expose_to", []))
    if agent_id not in exposed:
        exposed.append(agent_id)
    tool["expose_to"] = exposed
    write_yaml(_tool_path(base, tool_id), tool)
    return tool


def evaluate_policy(tool):
    if tool.get("risk") == "read_only":
        return "allowed"
    return "blocked"


def tool_exposed_to_agent(tool, agent_id):
    exposed = tool.get("expose_to", [])
    return "*" in exposed or agent_id in exposed


def available_tool_ids(root, agent):
    available = []
    unavailable = []
    for tool_id in agent.get("tool_scope", []):
        tool = load_tool(root, tool_id)
        if tool_exposed_to_agent(tool, agent.get("agent_id")):
            available.append(tool_id)
        else:
            unavailable.append({"tool_id": tool_id, "reason": "tool_not_exposed_to_agent"})
    return available, unavailable


def execute_tool(root, run_id, agent, tool_id, args, source="manual"):
    tool = load_tool(root, tool_id)
    now = utc_now()
    call = {
        "id": new_id("tc"),
        "run_id": run_id,
        "tool_id": tool_id,
        "agent_id": agent["agent_id"],
        "status": "running",
        "created_at": now,
        "updated_at": now,
        "args_ref": args,
        "result_ref": {},
        "risk": tool.get("risk", "unknown"),
        "policy_result": "unknown",
        "artifact_ids": [],
        "executor": "novi_tool_runtime",
        "source": source,
    }

    if tool_id not in agent.get("tool_scope", []):
        call["status"] = "blocked"
        call["policy_result"] = "blocked"
        call["block_reason"] = "tool_not_in_agent_scope"
        call["updated_at"] = utc_now()
        return call

    if not tool_exposed_to_agent(tool, agent.get("agent_id")):
        call["status"] = "blocked"
        call["policy_result"] = "blocked"
        call["block_reason"] = "tool_not_exposed_to_agent"
        call["updated_at"] = utc_now()
        return call

    policy_result = evaluate_policy(tool)
    if policy_result != "allowed":
        call["status"] = "blocked"
        call["policy_result"] = policy_result
        call["block_reason"] = "policy_not_allowed"
        call["updated_at"] = utc_now()
        return call

    if tool_id == "search_stub.query":
        call["status"] = "success"
        call["policy_result"] = "allowed"
        call["result_ref"] = {
            "source": "deterministic_stub",
            "summary": f"No network search was performed for: {args.get('query', '')}",
        }
        call["updated_at"] = utc_now()
        return call

    if tool_id == "filesystem.read":
        workspace = Path(root).resolve()
        raw_path = args.get("path", "")
        path = Path(raw_path)
        if path.is_absolute():
            requested = path.resolve()
            if not str(requested).startswith(str(workspace)):
                requested = (workspace / raw_path.lstrip("/")).resolve()
        else:
            requested = (workspace / raw_path).resolve()
        if not str(requested).startswith(str(workspace)):
            call["status"] = "blocked"
            call["policy_result"] = "blocked"
            call["block_reason"] = "path_outside_workspace"
            call["updated_at"] = utc_now()
            return call
        if not requested.is_file():
            call["status"] = "error"
            call["policy_result"] = "allowed"
            call["error"] = f"File not found: {args.get('path', '')}"
            call["updated_at"] = utc_now()
            return call
        content = requested.read_text(encoding="utf-8")
        call["status"] = "success"
        call["policy_result"] = "allowed"
        call["result_ref"] = {
            "path": str(requested.relative_to(workspace)),
            "content": content[:4000],
            "truncated": len(content) > 4000,
        }
        call["updated_at"] = utc_now()
        return call

    if tool_id == "git.status":
        result = subprocess.run(
            ["git", "status", "--short", "--branch"],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=10,
        )
        call["policy_result"] = "allowed"
        call["status"] = "success" if result.returncode == 0 else "error"
        call["result_ref"] = {"stdout": result.stdout, "stderr": result.stderr}
        call["updated_at"] = utc_now()
        return call

    call["status"] = "blocked"
    call["policy_result"] = "blocked"
    call["block_reason"] = "executor_not_implemented"
    call["updated_at"] = utc_now()
    return call
