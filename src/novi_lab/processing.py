from pathlib import Path

from .ids import new_id
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


def process_imported_document(root, contribution_id, workflow="document-merge", target=None, kernel="simple"):
    if workflow != "document-merge":
        raise RuntimeError(f"Unsupported processing workflow: {workflow}")
    if kernel != "simple":
        raise RuntimeError("Document processing currently supports --kernel simple.")

    session = active_session(root)
    if target:
        target_type_for_path(root, target)
    import_contribution, _ = load_contribution(root, contribution_id)
    if import_contribution.get("type") != "knowledge_import":
        raise RuntimeError(f"Contribution is not an import contribution: {contribution_id}")
    source_artifact = load_artifact(root, import_contribution["artifact_id"])
    source_path = Path(source_artifact["path"])
    source_text = source_path.read_text(encoding="utf-8", errors="replace")

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
        "workflow": workflow,
        "source_contribution_id": contribution_id,
        "artifact_ids": [],
        "contribution_ids": [],
        "summary_path": str(run_dir / "summary.md"),
    }
    write_yaml(run_dir / "run.yaml", run_record)
    append_jsonl(run_dir / "events.jsonl", _event(run_id, "RunCreated", session["id"], "Document processing run created."))

    analysis_artifact_id = new_id("art")
    analysis_path = run_dir / "artifacts" / f"{analysis_artifact_id}-analysis-note.md"
    analysis_text = "\n".join(
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
    append_jsonl(run_dir / "events.jsonl", _event(run_id, "ArtifactCreated", session["id"], "Analysis note artifact created.", {"artifact_id": analysis_artifact_id}))

    patch_contribution = None
    if target:
        target_path = Path(target)
        target_text = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
        proposed = _append_import_section(
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
