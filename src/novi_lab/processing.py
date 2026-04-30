from pathlib import Path
import json

from .ids import new_id
from .kernels import require_deepagents_kernel
from .model_providers import resolve_deepagents_model
from .skills import discover_skills
from .store import (
    active_session,
    append_jsonl,
    content_hash,
    create_document_patch_contribution,
    create_run_dir,
    load_artifact,
    load_contribution,
    load_session,
    save_session,
    target_type_for_path,
    utc_now,
    write_yaml,
)
from .workflows import load_workflow, workflow_prompt


def _event(run_id, event_type, session_id, summary, payload=None):
    return {
        "id": new_id("evt"),
        "run_id": run_id,
        "session_id": session_id,
        "type": event_type,
        "created_at": utc_now(),
        "actor": "system",
        "summary": summary,
        "payload": payload or {},
    }


def _append_import_section(target_text, import_contribution, source_text, source_artifact_id, analysis_artifact_id):
    section = "\n".join(
        [
            f"## Imported: {import_contribution.get('title', import_contribution['id'])}",
            "",
            f"- Import contribution: {import_contribution['id']}",
            f"- Source artifact: {source_artifact_id}",
            f"- Analysis artifact: {analysis_artifact_id}",
            "",
            source_text.strip(),
            "",
        ]
    )
    base = target_text.rstrip()
    return f"{base}\n\n{section}\n" if base else f"{section}\n"


def _deepagents_file_content(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return str(value.get("content", value.get("data", value)))
    return str(getattr(value, "content", value))


def _message_content(message):
    if isinstance(message, dict):
        return str(message.get("content", ""))
    return str(getattr(message, "content", ""))


def _archive_deepagents_messages(run_dir, result):
    if not isinstance(result, dict) or not result.get("messages"):
        return
    for index, message in enumerate(result["messages"]):
        append_jsonl(
            Path(run_dir) / "deepagents_messages.jsonl",
            {
                "index": index,
                "role": getattr(message, "role", None) or (message.get("role") if isinstance(message, dict) else type(message).__name__),
                "content": _message_content(message),
                "message_type": type(message).__name__,
            },
        )


def _extract_json_payload(text):
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return {}


def _extract_deepagents_outputs(result):
    files = result.get("files", {}) if isinstance(result, dict) else {}
    normalized = {str(path).lstrip("/"): _deepagents_file_content(value) for path, value in files.items()}
    analysis = normalized.get("analysis_note.md") or normalized.get("analysis.md")
    proposed = normalized.get("proposed.md") or normalized.get("target.md")
    response_text = ""
    if isinstance(result, dict) and result.get("messages"):
        response_text = _message_content(result["messages"][-1])
    elif isinstance(result, str):
        response_text = result
    payload = _extract_json_payload(response_text)
    analysis = analysis or payload.get("analysis_markdown") or payload.get("analysis_note")
    proposed = proposed or payload.get("proposed_markdown") or payload.get("proposed_document")
    return analysis, proposed, response_text


def _skill_text(root, skill_id):
    for skill in discover_skills(root):
        if skill["id"] == skill_id:
            return Path(skill["path"]).read_text(encoding="utf-8")
    return ""


def _processing_prompt(root, workflow_record, source_text, source_artifact, import_contribution, target, target_text):
    skill_ids = []
    for step in workflow_record.get("steps", []):
        skill_ids.extend(step.get("skill_refs", []))
    skill_sections = []
    for skill_id in dict.fromkeys(skill_ids):
        text = _skill_text(root, skill_id)
        if text:
            skill_sections.extend([f"## Skill: {skill_id}", "", text.strip(), ""])
    return "\n".join(
        [
            workflow_prompt(workflow_record).strip(),
            "",
            "# Novi Document Processing Output Protocol",
            "",
            "Return virtual files when possible:",
            "- /analysis_note.md: Markdown analysis note.",
            "- /proposed.md: Complete proposed target Markdown document when a target is provided.",
            "",
            "If virtual files are unavailable, respond with JSON:",
            '{"analysis_markdown": "...", "proposed_markdown": "..."}',
            "",
            "# Skills",
            "",
            *skill_sections,
            "# Source Refs",
            "",
            f"- Import contribution: {import_contribution['id']}",
            f"- Source artifact: {source_artifact['id']}",
            "",
            "# Imported Document",
            "",
            source_text.strip(),
            "",
            "# Target Document",
            "",
            f"- Target: {target or '-'}",
            "",
            target_text.strip() if target_text else "(no target provided)",
            "",
        ]
    )


def _run_deepagents_processing(root, run_dir, run_record, workflow_record, source_text, source_artifact, import_contribution, target, target_text):
    deepagents = require_deepagents_kernel()
    create_deep_agent = getattr(deepagents, "create_deep_agent")
    prompt = _processing_prompt(root, workflow_record, source_text, source_artifact, import_contribution, target, target_text)
    prompt_path = Path(run_dir) / "processing_prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    participant = {
        "agent_id": "agent_orchestrator",
        "model_profile": "deterministic-local",
    }
    model, model_record = resolve_deepagents_model(root, participant)
    started_at = utc_now()
    try:
        agent = create_deep_agent(
            model=model,
            tools=[],
            system_prompt=prompt,
            name="agent_orchestrator",
        )
        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "Process the imported document according to the WorkflowSpec and output protocol.",
                    }
                ]
            }
        )
        _archive_deepagents_messages(run_dir, result)
        analysis, proposed, response_text = _extract_deepagents_outputs(result)
        (Path(run_dir) / "response.md").write_text(f"# Model Response\n\n{response_text}\n", encoding="utf-8")
        append_jsonl(
            Path(run_dir) / "model_calls.jsonl",
            {
                "run_id": run_record["id"],
                "agent_id": "agent_orchestrator",
                **model_record,
                "kernel": "deepagents",
                "status": "success",
                "started_at": started_at,
                "completed_at": utc_now(),
                "prompt_path": str(prompt_path),
            },
        )
        return analysis, proposed
    except Exception as exc:
        append_jsonl(
            Path(run_dir) / "model_calls.jsonl",
            {
                "run_id": run_record["id"],
                "agent_id": "agent_orchestrator",
                **model_record,
                "kernel": "deepagents",
                "status": "error",
                "started_at": started_at,
                "completed_at": utc_now(),
                "prompt_path": str(prompt_path),
                "error": str(exc),
            },
        )
        raise RuntimeError(f"DeepAgents document processing failed: {exc}") from exc


def _step(workflow, step_id, status, artifact_ids=None, contribution_ids=None, skipped_reason=None):
    step_spec = next((item for item in workflow.get("steps", []) if item.get("id") == step_id), {})
    result = {
        "step_id": step_id,
        "kind": step_spec.get("kind"),
        "actor": step_spec.get("actor"),
        "status": status,
    }
    if artifact_ids:
        result["artifact_ids"] = artifact_ids
    if contribution_ids:
        result["contribution_ids"] = contribution_ids
    if skipped_reason:
        result["skipped_reason"] = skipped_reason
    return result


def process_imported_document(root, contribution_id, workflow="document-merge", target=None, kernel="simple"):
    workflow_record = load_workflow(root, workflow)
    if workflow_record.get("id") != "document-merge":
        raise RuntimeError(f"Unsupported processing workflow: {workflow}")
    if kernel not in {"simple", "deepagents"}:
        raise RuntimeError(f"Unsupported processing kernel: {kernel}")

    session = active_session(root)
    if target:
        target_type_for_path(root, target)
    import_contribution, _ = load_contribution(root, contribution_id)
    if import_contribution.get("type") != "knowledge_import":
        raise RuntimeError(f"Contribution is not an import contribution: {contribution_id}")
    source_artifact = load_artifact(root, import_contribution["artifact_id"])
    source_path = Path(source_artifact["path"])
    source_text = source_path.read_text(encoding="utf-8", errors="replace")
    target_text = ""
    if target:
        target_path_for_prompt = Path(target)
        target_text = target_path_for_prompt.read_text(encoding="utf-8") if target_path_for_prompt.exists() else ""

    run_id = new_id("run")
    run_dir = create_run_dir(root, run_id)
    now = utc_now()
    run_record = {
        "id": run_id,
        "session_id": session["id"],
        "type": "analysis",
        "objective": f"Process import contribution {contribution_id}",
        "status": "running",
        "created_at": now,
        "updated_at": now,
        "actor": "local_user",
        "kernel": kernel,
        "workflow_id": workflow_record["id"],
        "workflow_version": workflow_record.get("version"),
        "source_contribution_id": contribution_id,
        "artifact_ids": [],
        "contribution_ids": [],
        "step_results": [],
        "summary_path": str(run_dir / "summary.md"),
    }
    write_yaml(run_dir / "run.yaml", run_record)
    append_jsonl(run_dir / "events.jsonl", _event(run_id, "RunCreated", session["id"], "Document processing run created."))
    (run_dir / "workflow_prompt.md").write_text(workflow_prompt(workflow_record), encoding="utf-8")
    run_record["step_results"].append(_step(workflow_record, "load_import", "completed"))

    model_analysis = None
    model_proposed = None
    if kernel == "deepagents":
        model_analysis, model_proposed = _run_deepagents_processing(
            root,
            run_dir,
            run_record,
            workflow_record,
            source_text,
            source_artifact,
            import_contribution,
            target,
            target_text,
        )

    analysis_artifact_id = new_id("art")
    analysis_path = run_dir / "artifacts" / f"{analysis_artifact_id}-analysis-note.md"
    analysis_text = model_analysis or "\n".join(
        [
            "# Analysis Note",
            "",
            f"- Import contribution: {contribution_id}",
            f"- Source artifact: {source_artifact['id']}",
            f"- Workflow: {workflow}",
            f"- Target: {target or '-'}",
            "",
            "## Summary",
            "",
            "This deterministic processor preserved the imported document and prepared it for reviewable document-library merge.",
            "",
            "## Imported Content",
            "",
            source_text.strip(),
            "",
        ]
    )
    analysis_path.write_text(analysis_text, encoding="utf-8")
    analysis_record = {
        "id": analysis_artifact_id,
        "type": "analysis_note",
        "path": str(analysis_path),
        "run_id": run_id,
        "created_at": utc_now(),
        "produced_by": "agent_orchestrator",
        "hash": content_hash(analysis_path),
        "hash_algorithm": "sha256",
        "mime_type": "text/markdown",
        "size_bytes": analysis_path.stat().st_size,
    }
    write_yaml(run_dir / "artifacts" / f"{analysis_artifact_id}.yaml", analysis_record)
    run_record["artifact_ids"].append(analysis_artifact_id)
    run_record["step_results"].append(_step(workflow_record, "analyze", "completed", artifact_ids=[analysis_artifact_id]))
    append_jsonl(run_dir / "events.jsonl", _event(run_id, "ArtifactCreated", session["id"], "Analysis note artifact created.", {"artifact_id": analysis_artifact_id}))

    patch_contribution = None
    if target:
        target_path = Path(target)
        target_text = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
        proposed = model_proposed or _append_import_section(
            target_text,
            import_contribution,
            source_text,
            source_artifact["id"],
            analysis_artifact_id,
        )
        patch_contribution = create_document_patch_contribution(
            root,
            title=f"Merge {import_contribution.get('title', contribution_id)} into {target_path.name}",
            target=target_path,
            proposed_content=proposed,
            source_refs=[
                {"type": "contribution", "id": contribution_id},
                {"type": "artifact", "id": source_artifact["id"]},
                {"type": "run", "id": run_id},
                {"type": "artifact", "id": analysis_artifact_id},
            ],
            source_actor="agent",
            rationale=f"Generated by {workflow} from import contribution {contribution_id}.",
        )
        run_record["contribution_ids"].append(patch_contribution["id"])
        run_record["step_results"].append(_step(workflow_record, "choose_target", "skipped", skipped_reason="target_provided"))
        run_record["step_results"].append(_step(workflow_record, "draft_patch", "completed", contribution_ids=[patch_contribution["id"]]))
        run_record["step_results"].append(_step(workflow_record, "check_patch", "pending", contribution_ids=[patch_contribution["id"]]))
        run_record["step_results"].append(_step(workflow_record, "review_patch", "pending", contribution_ids=[patch_contribution["id"]]))
        run_record["step_results"].append(_step(workflow_record, "apply_patch", "pending", contribution_ids=[patch_contribution["id"]]))
        append_jsonl(
            run_dir / "events.jsonl",
            _event(
                run_id,
                "ContributionProposed",
                session["id"],
                "Document patch contribution proposed.",
                {"contribution_id": patch_contribution["id"]},
            ),
        )
    else:
        run_record["step_results"].append(_step(workflow_record, "choose_target", "pending", skipped_reason="target_missing"))
        run_record["step_results"].append(_step(workflow_record, "draft_patch", "skipped", skipped_reason="target_missing"))

    run_record["status"] = "completed"
    run_record["updated_at"] = utc_now()
    run_record["completed_at"] = utc_now()
    (run_dir / "summary.md").write_text(
        "\n".join(
            [
                f"# Run {run_id}",
                "",
                "Status: completed",
                f"Objective: Process import contribution {contribution_id}",
                f"Workflow: {workflow_record['id']} v{workflow_record.get('version')}",
                "",
                f"Analysis artifact: {analysis_artifact_id}",
                f"Patch contribution: {patch_contribution['id'] if patch_contribution else '-'}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    write_yaml(run_dir / "run.yaml", run_record)
    append_jsonl(run_dir / "events.jsonl", _event(run_id, "RunCompleted", session["id"], "Document processing run completed."))

    session = load_session(root, session["id"])
    session["current_run_id"] = run_id
    session.setdefault("run_ids", []).append(run_id)
    save_session(root, session)

    return {
        "run": run_record,
        "analysis_artifact": analysis_record,
        "patch_contribution": patch_contribution,
    }
