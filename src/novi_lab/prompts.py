import json
from hashlib import sha256
from pathlib import Path

from .skills import discover_skills
from .model_providers import configured_model_record
from .store import append_jsonl, session_messages
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


def _part_record(path, content):
    digest = sha256(content.encode("utf-8")).hexdigest()
    return {
        "path": str(path),
        "hash": digest,
        "hash_algorithm": "sha256",
        "size_bytes": len(content.encode("utf-8")),
    }


def _tool_callable_name(tool_id):
    return tool_id.replace(".", "_").replace("-", "_")


def build_prompt_parts(root, run_record, context_pack):
    skills = _by_id(discover_skills(root))
    tools = _by_id(list_tools(root))
    participants = run_record.get("participants", [])
    primary_agent = participants[0] if participants else {}
    system = SYSTEM_PROMPT.strip() + "\n"
    run_context = "\n".join(
        [
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
        *[f"- {item}" for item in context_pack.get("includes", [])],
        "",
        "## Excludes",
        "",
        *[f"- {item}" for item in context_pack.get("excludes", [])],
        "",
        ]
    )

    skill_lines = ["# Skills", ""]
    for skill_ref in primary_agent.get("skill_refs", []) or run_record.get("skill_refs", []):
        skill = skills.get(skill_ref, {"description": ""})
        skill_lines.extend([f"## Skill: {skill_ref}", "", skill.get("description", ""), ""])

    tool_lines = [
        "# Tools",
        "",
        "Call the tool function when tool output is needed. Do not only say that you will inspect or read something.",
        "Use the callable names below when selecting tools.",
        "",
    ]
    for tool_id in primary_agent.get("tool_scope", []):
        tool = tools.get(tool_id)
        if not tool:
            continue
        tool_lines.extend(
            [
                f"## Tool: {tool_id}",
                "",
                f"- Callable name: {_tool_callable_name(tool_id)}",
                f"- Risk: {tool.get('risk', '-')}",
                f"- Policy: {tool.get('policy', '-')}",
                f"- Description: {tool.get('description', '')}",
                f"- Input schema: {tool.get('input_schema', {})}",
                "",
            ]
        )

    recent_messages = "\n".join(
        json.dumps(
            {
                "role": message.get("role"),
                "content": message.get("content"),
                "run_id": message.get("run_id"),
            },
            sort_keys=True,
        )
        for message in session_messages(root, run_record["session_id"], limit=12)
    )
    current_task = "\n".join(["# Current Task", "", run_record["objective"], ""])
    return [
        ("00-system.md", system),
        ("20-agent.md", run_context.strip() + "\n"),
        ("30-skills.md", "\n".join(skill_lines).strip() + "\n"),
        ("40-tools.md", "\n".join(tool_lines).strip() + "\n"),
        ("70-recent-messages.jsonl", recent_messages + ("\n" if recent_messages else "")),
        ("80-current-task.md", current_task),
    ]


def build_prompt_markdown(root, run_record, context_pack):
    return "\n\n".join(content.strip() for _, content in build_prompt_parts(root, run_record, context_pack)) + "\n"


def write_prompt_pack(root, run_dir, run_record, context_pack, kernel="simple"):
    prompt_path = Path(run_dir) / "prompt.md"
    request_path = Path(run_dir) / "model_request.yaml"
    parts_dir = Path(run_dir) / "prompt_parts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    part_records = []
    prompt_parts = build_prompt_parts(root, run_record, context_pack)
    for filename, content in prompt_parts:
        path = parts_dir / filename
        path.write_text(content, encoding="utf-8")
        part_records.append(_part_record(path.relative_to(run_dir), content))
    prompt_path.write_text("\n\n".join(content.strip() for _, content in prompt_parts) + "\n", encoding="utf-8")
    response_path = Path(run_dir) / "response.md"
    response_path.write_text(
        "# Model Response\n\nNo model executor connected. This run was produced by the simple kernel.\n",
        encoding="utf-8",
    )
    model_record = configured_model_record(root, run_record.get("participants", [{}])[0])
    request = {
        "run_id": run_record["id"],
        "agent_id": run_record.get("participants", [{}])[0].get("agent_id"),
        "agent_model_profile": run_record.get("participants", [{}])[0].get("model_profile", context_pack.get("model_profile")),
        "model_profile": model_record["model_profile"],
        "model_provider": model_record["model_provider"],
        "model_base_url": model_record["model_base_url"],
        "kernel": kernel,
        "prompt_path": str(prompt_path),
        "prompt_parts": part_records,
        "response_path": str(response_path),
        "executor": kernel,
    }
    from .store import write_yaml

    write_yaml(parts_dir / "manifest.yaml", {"parts": part_records})
    write_yaml(request_path, request)
    append_jsonl(
        Path(run_dir) / "model_calls.jsonl",
        {
            "run_id": run_record["id"],
            "agent_id": request["agent_id"],
            "model_profile": request["model_profile"],
            "model_provider": request["model_provider"],
            "model_base_url": request["model_base_url"],
            "kernel": kernel,
            "status": "not_connected",
            "prompt_path": str(prompt_path),
            "response_path": str(response_path),
        },
    )
    return prompt_path, request_path
