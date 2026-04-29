from pathlib import Path

from .skills import discover_skills
from .tools import list_tools


SYSTEM_PROMPT = """# Novi Lab System Prompt

You are executing inside Novi Lab, a local-first, skill-first control plane.

## Operating Rules

- Treat the run as the primary unit of execution, audit, replay, and evidence.
- Use only tools listed in the prompt pack for the active agent.
- Every tool request must be routed through Novi ToolRuntime; do not bypass policy or scope.
- Prefer evidence-backed outputs. Important claims should point to artifacts, tool results, or run records.
- Long-term memory is proposed as a reviewable candidate. Do not write durable memory directly.
- Keep external frameworks, providers, and services as adapters. Novi owns sessions, runs, tools, artifacts, memory, policy, and audit records.

## Context Management

- Use the provided context pack instead of assuming full chat history is available.
- Prefer session summaries, run state, active skills, accepted memory, and selected artifacts.
- Exclude raw old messages, unreviewed memory, and unavailable tools unless explicitly supplied.
"""


def _by_id(items):
    return {item["id"]: item for item in items}


def build_prompt_markdown(root, run_record, context_pack):
    skills = _by_id(discover_skills(root))
    tools = _by_id(list_tools(root))
    participants = run_record.get("participants", [])
    primary_agent = participants[0] if participants else {}
    lines = [
        SYSTEM_PROMPT.strip(),
        "",
        "# Run",
        "",
        f"- Run ID: {run_record['id']}",
        f"- Session ID: {run_record['session_id']}",
        f"- Type: {run_record['type']}",
        f"- Objective: {run_record['objective']}",
        f"- Status: {run_record['status']}",
        "",
        "# Active Agent",
        "",
        f"- Agent: {primary_agent.get('agent_id', '-')}",
        f"- Role: {primary_agent.get('role', '-')}",
        f"- Model profile: {primary_agent.get('model_profile', context_pack.get('model_profile', '-'))}",
        f"- Permission scope: {', '.join(primary_agent.get('permission_scope', [])) or '-'}",
        "",
        "# Context Pack",
        "",
        f"- Context pack ID: {context_pack['id']}",
        f"- Token budget: {context_pack.get('token_budget', '-')}",
        "",
        "## Includes",
        "",
    ]
    lines.extend(f"- {item}" for item in context_pack.get("includes", []))
    lines.extend(["", "## Excludes", ""])
    lines.extend(f"- {item}" for item in context_pack.get("excludes", []))

    lines.extend(["", "# Skills", ""])
    for skill_ref in primary_agent.get("skill_refs", []) or run_record.get("skill_refs", []):
        skill = skills.get(skill_ref, {"description": ""})
        lines.append(f"## Skill: {skill_ref}")
        lines.append("")
        lines.append(skill.get("description", ""))
        lines.append("")

    lines.extend(["# Tools", ""])
    for tool_id in primary_agent.get("tool_scope", []):
        tool = tools.get(tool_id)
        if not tool:
            continue
        lines.append(f"## Tool: {tool_id}")
        lines.append("")
        lines.append(f"- Risk: {tool.get('risk', '-')}")
        lines.append(f"- Policy: {tool.get('policy', '-')}")
        lines.append(f"- Description: {tool.get('description', '')}")
        lines.append(f"- Input schema: {tool.get('input_schema', {})}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def write_prompt_pack(root, run_dir, run_record, context_pack):
    prompt_path = Path(run_dir) / "prompt.md"
    request_path = Path(run_dir) / "model_request.yaml"
    prompt_path.write_text(build_prompt_markdown(root, run_record, context_pack), encoding="utf-8")
    request = {
        "run_id": run_record["id"],
        "agent_id": run_record.get("participants", [{}])[0].get("agent_id"),
        "model_profile": run_record.get("participants", [{}])[0].get("model_profile", context_pack.get("model_profile")),
        "prompt_path": str(prompt_path),
        "response_path": str(Path(run_dir) / "response.md"),
        "executor": "not_connected",
    }
    from .store import write_yaml

    write_yaml(request_path, request)
    return prompt_path, request_path
