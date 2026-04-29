from .ids import new_id
from .store import read_yaml, require_workspace, utc_now


def builtin_tools():
    return [
        {
            "id": "search_stub.query",
            "description": "Deterministic local search stub used to validate tool records.",
            "risk": "read_only",
            "policy": "allowed",
            "input_schema": {"query": "string"},
            "output_artifacts": ["search_result_stub"],
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


def evaluate_policy(tool):
    if tool.get("risk") == "read_only":
        return "allowed"
    return "blocked"


def execute_tool(root, run_id, agent, tool_id, args):
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
    }

    if tool_id not in agent.get("tool_scope", []):
        call["status"] = "blocked"
        call["policy_result"] = "blocked"
        call["block_reason"] = "tool_not_in_agent_scope"
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

    call["status"] = "blocked"
    call["policy_result"] = "blocked"
    call["block_reason"] = "executor_not_implemented"
    call["updated_at"] = utc_now()
    return call
