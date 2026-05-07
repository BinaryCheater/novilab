import json
from hashlib import sha256
from pathlib import Path

from .skills import discover_skills
from .model_providers import configured_model_record
from .store import accepted_knowledge, append_jsonl, session_messages
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

## Durable Outputs

- For research or reflection work, produce concrete Markdown working files when possible.
- Prefer `topic-brief.md` for topic scope, known facts, unknowns, and evidence needs.
- Prefer `evidence-map.md` for claims, evidence, assumptions, mechanisms, uncertainty, and falsification notes.
- Prefer `hypotheses.md` for ranked hypotheses and expected observations.
- Prefer `experiment-plan.md` for the next minimal experiment, variables, controls, measurements, and stop criteria.
- Prefer `iteration-log.md` for the trial record template and interpretation notes.
- Prefer `physical-priors.md` for reviewable physical prior candidates with evidence, boundaries, counterexamples, confidence, and next validation.
- Prefer `research-note.md` for findings, synthesis, assumptions, and uncertainty.
- Prefer `next-actions.md` for concrete follow-up steps and open questions.
- Prefer `proposals.md` for proposed knowledge, skill, or workflow changes that need review.
"""


def _by_id(items):
    return {item["id"]: item for item in items}


def _merged_refs(*ref_lists):
    refs = []
    for ref_list in ref_lists:
        for ref in ref_list or []:
            if ref not in refs:
                refs.append(ref)
    return refs


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
        f"- Workflow ID: {run_record.get('workflow_id') or '-'}",
        f"- Workflow step: {run_record.get('workflow_step_id') or '-'}",
        f"- Workflow step kind: {run_record.get('workflow_step_kind') or '-'}",
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
    for skill_ref in _merged_refs(primary_agent.get("skill_refs", []), run_record.get("skill_refs", [])):
        skill = skills.get(skill_ref, {"description": ""})
        skill_text = skill.get("body") or skill.get("description", "")
        skill_lines.extend([f"## Skill: {skill_ref}", "", skill_text, ""])

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

    knowledge_lines = ["# Accepted Knowledge", ""]
    knowledge_records = accepted_knowledge(root)
    if knowledge_records:
        for record in knowledge_records:
            knowledge_lines.extend(
                [
                    f"## {record.get('title') or record['id']}",
                    "",
                    f"- Contribution: {record['id']}",
                    f"- Source artifact: {record.get('source_artifact_id', '-')}",
                    "",
                    record.get("content", "").strip(),
                    "",
                ]
            )
    else:
        knowledge_lines.append("No accepted knowledge records.")

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
    task_history_lines = ["# Task History", ""]
    task_refs = context_pack.get("task_run_refs", [])
    if task_refs:
        for ref in task_refs:
            task_history_lines.extend(
                [
                    f"## Run {ref.get('run_id')}",
                    "",
                    f"- Status: {ref.get('status') or '-'}",
                    f"- Workflow step: {ref.get('workflow_step_id') or '-'}",
                    f"- Step title: {ref.get('workflow_step_title') or '-'}",
                    f"- Summary path: {ref.get('summary_path') or '-'}",
                    "",
                ]
            )
    else:
        task_history_lines.append("No prior task runs.")
    current_task_lines = ["# Current Task", "", run_record["objective"], ""]
    if run_record.get("workflow_step_id"):
        current_task_lines.extend(
            [
                f"Workflow step: {run_record.get('workflow_step_id')}",
                f"Step title: {run_record.get('workflow_step_title') or '-'}",
                f"Step kind: {run_record.get('workflow_step_kind') or '-'}",
                "",
            ]
        )
    current_task = "\n".join(current_task_lines)
    return [
        ("00-system.md", system),
        ("20-agent.md", run_context.strip() + "\n"),
        ("30-skills.md", "\n".join(skill_lines).strip() + "\n"),
        ("40-tools.md", "\n".join(tool_lines).strip() + "\n"),
        ("60-accepted-knowledge.md", "\n".join(knowledge_lines).strip() + "\n"),
        ("70-recent-messages.jsonl", recent_messages + ("\n" if recent_messages else "")),
        ("75-task-history.md", "\n".join(task_history_lines).strip() + "\n"),
        ("80-current-task.md", current_task),
    ]


def build_prompt_markdown(root, run_record, context_pack):
    return "\n\n".join(content.strip() for _, content in build_prompt_parts(root, run_record, context_pack)) + "\n"


def build_system_prompt_markdown(root, run_record, context_pack):
    stable_part_names = {"00-system.md", "30-skills.md", "40-tools.md", "60-accepted-knowledge.md"}
    return "\n\n".join(
        content.strip()
        for filename, content in build_prompt_parts(root, run_record, context_pack)
        if filename in stable_part_names
    ) + "\n"


def build_model_messages(root, run_record, limit=12):
    messages = []
    for message in session_messages(root, run_record["session_id"], limit=limit):
        role = message.get("role")
        content = message.get("content")
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})
    if not messages or messages[-1] != {"role": "user", "content": run_record["objective"]}:
        messages.append({"role": "user", "content": run_record["objective"]})
    return messages


def _write_jsonl(path, rows):
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_prompt_pack(root, run_dir, run_record, context_pack, kernel="simple"):
    prompt_path = Path(run_dir) / "prompt.md"
    system_prompt_path = Path(run_dir) / "system_prompt.md"
    model_messages_path = Path(run_dir) / "model_messages.jsonl"
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
    system_prompt_path.write_text(build_system_prompt_markdown(root, run_record, context_pack), encoding="utf-8")
    _write_jsonl(model_messages_path, build_model_messages(root, run_record))
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
        "model_api_shape": model_record.get("model_api_shape"),
        "kernel": kernel,
        "prompt_path": str(prompt_path),
        "system_prompt_path": str(system_prompt_path),
        "model_messages_path": str(model_messages_path),
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
            "model_api_shape": request.get("model_api_shape"),
            "kernel": kernel,
            "status": "not_connected",
            "prompt_path": str(system_prompt_path),
            "model_messages_path": str(model_messages_path),
            "response_path": str(response_path),
        },
    )
    return system_prompt_path, request_path
