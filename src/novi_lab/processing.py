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


def _message_field(message, field):
    if isinstance(message, dict):
        return message.get(field)
    return getattr(message, field, None)


def _jsonable(value):
    try:
        json.dumps(value)
        return value
    except TypeError:
        return json.loads(json.dumps(value, default=str))


def _archive_deepagents_messages(run_dir, result):
    if not isinstance(result, dict) or not result.get("messages"):
        return
    for index, message in enumerate(result["messages"]):
        record = {
            "index": index,
            "role": getattr(message, "role", None) or (message.get("role") if isinstance(message, dict) else type(message).__name__),
            "content": _message_content(message),
            "message_type": type(message).__name__,
        }
        for field in ("tool_calls", "invalid_tool_calls", "additional_kwargs", "response_metadata", "name", "tool_call_id"):
            value = _message_field(message, field)
            if value:
                record[field] = _jsonable(value)
        append_jsonl(
            Path(run_dir) / "deepagents_messages.jsonl",
            record,
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
    integration_plan = normalized.get("integration_plan.md")
    proposals_payload = normalized.get("proposals.json")
    response_text = ""
    if isinstance(result, dict) and result.get("messages"):
        response_text = _message_content(result["messages"][-1])
    elif isinstance(result, str):
        response_text = result
    payload = _extract_json_payload(response_text)
    if proposals_payload:
        proposals_file_payload = _extract_json_payload(proposals_payload)
        if proposals_file_payload:
            payload = {**payload, **proposals_file_payload}
    analysis = analysis or payload.get("analysis_markdown") or payload.get("analysis_note")
    proposed = proposed or payload.get("proposed_markdown") or payload.get("proposed_document")
    integration_plan = integration_plan or payload.get("integration_plan_markdown") or payload.get("integration_plan")
    proposals = payload.get("proposals") or []
    questions = payload.get("questions_for_human") or []
    return analysis, proposed, response_text, integration_plan, proposals, questions


def _skill_text(root, skill_id):
    for skill in discover_skills(root):
        if skill["id"] == skill_id:
            return Path(skill["path"]).read_text(encoding="utf-8")
    return ""


def _library_context(root, limit=40, chars_per_file=1200):
    base = Path(root) / ".novi" / "knowledge"
    if not base.exists():
        return "(knowledge library is empty)"
    sections = []
    for path in sorted(base.rglob("*.md"))[:limit]:
        relative = path.relative_to(Path(root))
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        sections.extend([f"## {relative}", "", text[:chars_per_file] if text else "(empty)", ""])
    return "\n".join(sections).strip() or "(knowledge library has no Markdown documents)"


def _processing_prompt(root, workflow_record, imported_documents, target=None, target_text="", hint=None):
    skill_ids = []
    for step in workflow_record.get("steps", []):
        skill_ids.extend(step.get("skill_refs", []))
    skill_sections = []
    for skill_id in dict.fromkeys(skill_ids):
        text = _skill_text(root, skill_id)
        if text:
            skill_sections.extend([f"## Skill: {skill_id}", "", text.strip(), ""])
    imported_sections = []
    for index, item in enumerate(imported_documents, start=1):
        imported_sections.extend(
            [
                f"# Imported Document {index}",
                "",
                f"- Import contribution: {item['contribution']['id']}",
                f"- Source artifact: {item['artifact']['id']}",
                f"- Title: {item['contribution'].get('title', item['contribution']['id'])}",
                "",
                item["text"].strip(),
                "",
            ]
        )
    return "\n".join(
        [
            workflow_prompt(workflow_record).strip(),
            "",
            "# Novi Document Processing Output Protocol",
            "",
            "Do not try to read Novi workspace paths such as `.novi/...` or `/.novi/...` through DeepAgents working-file tools.",
            "Those tools only see the DeepAgents virtual workspace, not the Novi project workspace.",
            "The Imported Document and Target Document sections below are authoritative snapshots supplied by Novi.",
            "The Target Document section below is authoritative even when the named target path is not visible to your tools.",
            "Do not directly edit the Novi knowledge library. Produce proposals; Novi will turn proposals into reviewable patch contributions.",
            "",
            "Return virtual files when possible:",
            "- /analysis_note.md: Markdown analysis note.",
            "- /integration_plan.md: Markdown plan explaining how the library should be updated.",
            "- /proposed.md: Complete proposed target Markdown document when a target is provided.",
            "- /proposals.json: JSON object with `proposals` for agent-directed library integration.",
            "",
            "If virtual files are unavailable, respond with JSON:",
            '{"analysis_markdown": "...", "integration_plan_markdown": "...", "proposals": [{"path": ".novi/knowledge/...", "rationale": "...", "proposed_markdown": "..."}], "questions_for_human": []}',
            "",
            "When no explicit target is provided, inspect the Library Context and decide whether to propose zero, one, or many document updates.",
            "A proposal path must stay under `.novi/knowledge/`, `.novi/workflows/`, or `.novi/skills/`.",
            "If the right integration is unclear, return no proposals and include `questions_for_human`.",
            "",
            "# Skills",
            "",
            *skill_sections,
            "# User Hint",
            "",
            hint or "(none)",
            "",
            "# Library Context",
            "",
            _library_context(root),
            "",
            *imported_sections,
            "# Target Document",
            "",
            f"- Target: {target or '-'}",
            "",
            target_text.strip() if target_text else "(no target provided)",
            "",
        ]
    )


def _run_deepagents_processing(root, run_dir, run_record, workflow_record, imported_documents, target=None, target_text="", hint=None, progress=None):
    deepagents = require_deepagents_kernel()
    create_deep_agent = getattr(deepagents, "create_deep_agent")
    prompt = _processing_prompt(root, workflow_record, imported_documents, target=target, target_text=target_text, hint=hint)
    prompt_path = Path(run_dir) / "processing_prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    participant = {
        "agent_id": "agent_orchestrator",
        "model_profile": "deterministic-local",
    }
    model, model_record = resolve_deepagents_model(root, participant)
    started_at = utc_now()
    try:
        if progress:
            progress("Preparing DeepAgents document processor.")
        agent = create_deep_agent(
            model=model,
            tools=[],
            system_prompt=prompt,
            name="agent_orchestrator",
        )
        if progress:
            progress("Waiting for DeepAgents model response...")
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
        if progress:
            progress("Archiving DeepAgents response and virtual files.")
        _archive_deepagents_messages(run_dir, result)
        analysis, proposed, response_text, integration_plan, proposals, questions = _extract_deepagents_outputs(result)
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
        return analysis, proposed, integration_plan, proposals, questions
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


def process_imported_document(root, contribution_id, workflow="document-merge", target=None, kernel="deepagents", progress=None, hint=None):
    return process_imported_documents(root, [contribution_id], workflow=workflow, target=target, kernel=kernel, progress=progress, hint=hint)


def process_imported_documents(root, contribution_ids, workflow="document-merge", target=None, kernel="deepagents", progress=None, hint=None):
    if progress:
        progress(f"Loading workflow: {workflow}")
    workflow_record = load_workflow(root, workflow)
    if workflow_record.get("id") != "document-merge":
        raise RuntimeError(f"Unsupported processing workflow: {workflow}")
    if kernel not in {"simple", "deepagents"}:
        raise RuntimeError(f"Unsupported processing kernel: {kernel}")

    session = active_session(root)
    if target:
        target_type_for_path(root, target)
    imported_documents = []
    for contribution_id in contribution_ids:
        if progress:
            progress(f"Loading import contribution: {contribution_id}")
        import_contribution, _ = load_contribution(root, contribution_id)
        if import_contribution.get("type") != "knowledge_import":
            raise RuntimeError(f"Contribution is not an import contribution: {contribution_id}")
        source_artifact = load_artifact(root, import_contribution["artifact_id"])
        source_path = Path(source_artifact["path"])
        imported_documents.append(
            {
                "contribution": import_contribution,
                "artifact": source_artifact,
                "text": source_path.read_text(encoding="utf-8", errors="replace"),
            }
        )
    target_text = ""
    if target:
        target_path_for_prompt = Path(target)
        target_text = target_path_for_prompt.read_text(encoding="utf-8") if target_path_for_prompt.exists() else ""

    run_id = new_id("run")
    run_dir = create_run_dir(root, run_id)
    if progress:
        progress(f"Created run: {run_id}")
    now = utc_now()
    run_record = {
        "id": run_id,
        "session_id": session["id"],
        "type": "analysis",
        "objective": f"Process import contribution(s) {', '.join(contribution_ids)}",
        "status": "running",
        "created_at": now,
        "updated_at": now,
        "actor": "local_user",
        "kernel": kernel,
        "workflow_id": workflow_record["id"],
        "workflow_version": workflow_record.get("version"),
        "source_contribution_id": contribution_ids[0] if len(contribution_ids) == 1 else None,
        "source_contribution_ids": contribution_ids,
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
    integration_plan = None
    proposals = []
    questions_for_human = []
    if kernel == "deepagents":
        model_analysis, model_proposed, integration_plan, proposals, questions_for_human = _run_deepagents_processing(
            root,
            run_dir,
            run_record,
            workflow_record,
            imported_documents,
            target=target,
            target_text=target_text,
            hint=hint,
            progress=progress,
        )

    if progress:
        progress("Writing analysis artifact.")
    analysis_artifact_id = new_id("art")
    analysis_path = run_dir / "artifacts" / f"{analysis_artifact_id}-analysis-note.md"
    analysis_text = model_analysis or "\n".join(
        [
            "# Analysis Note",
            "",
            f"- Import contributions: {', '.join(contribution_ids)}",
            f"- Source artifacts: {', '.join(item['artifact']['id'] for item in imported_documents)}",
            f"- Workflow: {workflow}",
            f"- Target: {target or '-'}",
            f"- Hint: {hint or '-'}",
            "",
            "## Summary",
            "",
            "This deterministic processor preserved the imported document and prepared it for reviewable document-library merge.",
            "",
            "## Imported Content",
            "",
            "\n\n".join(item["text"].strip() for item in imported_documents),
            "",
        ]
    )
    if integration_plan:
        analysis_text = f"{analysis_text.rstrip()}\n\n{integration_plan.strip()}\n"
    if questions_for_human:
        analysis_text = f"{analysis_text.rstrip()}\n\n## Questions for Human\n\n" + "\n".join(f"- {item}" for item in questions_for_human) + "\n"
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

    patch_contributions = []
    if target:
        if progress:
            progress("Creating reviewable document patch contribution.")
        target_path = Path(target)
        target_text = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
        proposed = model_proposed or _append_import_section(
            target_text,
            imported_documents[0]["contribution"],
            "\n\n".join(item["text"].strip() for item in imported_documents),
            imported_documents[0]["artifact"]["id"],
            analysis_artifact_id,
        )
        patch_contribution = create_document_patch_contribution(
            root,
            title=f"Merge imported document(s) into {target_path.name}",
            target=target_path,
            proposed_content=proposed,
            source_refs=[
                *[{"type": "contribution", "id": item["contribution"]["id"]} for item in imported_documents],
                *[{"type": "artifact", "id": item["artifact"]["id"]} for item in imported_documents],
                {"type": "run", "id": run_id},
                {"type": "artifact", "id": analysis_artifact_id},
            ],
            source_actor="agent",
            rationale=f"Generated by {workflow} from import contribution(s) {', '.join(contribution_ids)}.",
        )
        patch_contributions.append(patch_contribution)
    elif proposals:
        if progress:
            progress(f"Creating {len(proposals)} agent-proposed patch contribution(s).")
        for proposal in proposals:
            proposal_target = proposal.get("path") or proposal.get("target") or proposal.get("target_path")
            proposed_content = proposal.get("proposed_markdown") or proposal.get("proposed_document")
            if not proposal_target or not proposed_content:
                continue
            patch_contributions.append(
                create_document_patch_contribution(
                    root,
                    title=f"Agent proposal for {Path(proposal_target).name}",
                    target=Path(root) / proposal_target,
                    proposed_content=proposed_content,
                    source_refs=[
                        *[{"type": "contribution", "id": item["contribution"]["id"]} for item in imported_documents],
                        *[{"type": "artifact", "id": item["artifact"]["id"]} for item in imported_documents],
                        {"type": "run", "id": run_id},
                        {"type": "artifact", "id": analysis_artifact_id},
                    ],
                    source_actor="agent",
                    rationale=proposal.get("rationale") or integration_plan or f"Generated by {workflow}.",
                )
            )
    if patch_contributions:
        run_record["contribution_ids"].extend(item["id"] for item in patch_contributions)
        run_record["step_results"].append(_step(workflow_record, "choose_target", "skipped", skipped_reason="target_provided"))
        run_record["step_results"].append(_step(workflow_record, "draft_patch", "completed", contribution_ids=[item["id"] for item in patch_contributions]))
        run_record["step_results"].append(_step(workflow_record, "check_patch", "pending", contribution_ids=[item["id"] for item in patch_contributions]))
        run_record["step_results"].append(_step(workflow_record, "review_patch", "pending", contribution_ids=[item["id"] for item in patch_contributions]))
        run_record["step_results"].append(_step(workflow_record, "apply_patch", "pending", contribution_ids=[item["id"] for item in patch_contributions]))
        for patch_contribution in patch_contributions:
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
                f"Objective: Process import contribution(s) {', '.join(contribution_ids)}",
                f"Workflow: {workflow_record['id']} v{workflow_record.get('version')}",
                "",
                f"Analysis artifact: {analysis_artifact_id}",
                f"Patch contributions: {', '.join(item['id'] for item in patch_contributions) if patch_contributions else '-'}",
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
        "patch_contribution": patch_contributions[0] if patch_contributions else None,
        "patch_contributions": patch_contributions,
        "questions_for_human": questions_for_human,
    }
