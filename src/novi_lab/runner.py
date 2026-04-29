from pathlib import Path

from .ids import new_id
from .store import (
    append_jsonl,
    content_hash,
    create_run_dir,
    load_session,
    save_session,
    utc_now,
    write_yaml,
)


def _event(run_id, event_type, session_id=None, agent_id=None, summary="", payload=None):
    return {
        "id": new_id("evt"),
        "run_id": run_id,
        "session_id": session_id,
        "type": event_type,
        "created_at": utc_now(),
        "actor": "system",
        "agent_id": agent_id,
        "summary": summary,
        "payload": payload or {},
    }


def start_deterministic_run(root, session, run_type, objective):
    now = utc_now()
    run_id = new_id("run")
    run_dir = create_run_dir(root, run_id)
    orchestrator = "agent_orchestrator"
    auditor = "agent_auditor"

    run_record = {
        "id": run_id,
        "session_id": session["id"],
        "type": run_type,
        "objective": objective,
        "status": "running",
        "created_at": now,
        "updated_at": now,
        "actor": "local_user",
        "skill_refs": ["research.review"] if run_type == "research" else [],
        "participants": [
            {
                "agent_id": orchestrator,
                "role": "orchestrator",
                "status": "active",
                "joined_at": now,
                "tool_scope": ["search_stub.query"],
                "context_scope": ["project", "session", "skill", "tools"],
                "permission_scope": ["read_only"],
            },
            {
                "agent_id": auditor,
                "role": "auditor",
                "status": "completed",
                "joined_at": now,
                "tool_scope": [],
                "context_scope": ["run_records"],
                "permission_scope": ["read_only"],
            },
        ],
        "context_pack_ids": [],
        "artifact_ids": [],
        "summary_path": str(run_dir / "summary.md"),
    }
    write_yaml(run_dir / "run.yaml", run_record)
    append_jsonl(run_dir / "events.jsonl", _event(run_id, "RunCreated", session["id"], orchestrator, "Run created."))

    context_id = new_id("ctx")
    context_path = run_dir / "context_pack.yaml"
    context = {
        "id": context_id,
        "session_id": session["id"],
        "run_id": run_id,
        "agent_id": orchestrator,
        "created_at": utc_now(),
        "model_profile": "deterministic-local",
        "token_budget": 4000,
        "includes": ["project spec summary", "session summary", "active skill", "visible tools"],
        "excludes": ["raw old messages", "unreviewed memory", "network content"],
        "skill_refs": run_record["skill_refs"],
        "tool_refs": ["search_stub.query"],
    }
    write_yaml(context_path, context)
    run_record["context_pack_ids"].append(context_id)
    append_jsonl(run_dir / "events.jsonl", _event(run_id, "ContextPackBuilt", session["id"], orchestrator, "Context pack built.", {"context_pack_id": context_id}))

    tool_call_id = new_id("tc")
    tool_call = {
        "id": tool_call_id,
        "run_id": run_id,
        "tool_id": "search_stub.query",
        "agent_id": orchestrator,
        "status": "success",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "args_ref": {"query": objective},
        "result_ref": {"source": "deterministic_stub"},
        "risk": "read_only",
        "policy_result": "allowed",
        "artifact_ids": [],
    }
    append_jsonl(run_dir / "tool_calls.jsonl", tool_call)
    append_jsonl(run_dir / "events.jsonl", _event(run_id, "ToolExecuted", session["id"], orchestrator, "search_stub.query completed.", {"tool_call_id": tool_call_id}))

    artifact_id = new_id("art")
    artifact_path = run_dir / "artifacts" / f"{artifact_id}-research-note.md"
    artifact_path.write_text(
        "\n".join(
            [
                "# Deterministic Research Note",
                "",
                f"Objective: {objective}",
                "",
                "This first runner validates Novi records without using a real model or network search.",
                "The output is intentionally deterministic and reviewable.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    artifact_record = {
        "id": artifact_id,
        "type": "research_note",
        "path": str(artifact_path),
        "run_id": run_id,
        "created_at": utc_now(),
        "produced_by": orchestrator,
        "hash": content_hash(artifact_path),
        "hash_algorithm": "sha256",
        "mime_type": "text/markdown",
        "size_bytes": artifact_path.stat().st_size,
    }
    write_yaml(run_dir / "artifacts" / f"{artifact_id}.yaml", artifact_record)
    run_record["artifact_ids"].append(artifact_id)
    append_jsonl(run_dir / "events.jsonl", _event(run_id, "ArtifactCreated", session["id"], orchestrator, "Research note artifact created.", {"artifact_id": artifact_id}))

    memory_id = new_id("memcand")
    memory = {
        "id": memory_id,
        "type": "session",
        "subject": "phase-1 deterministic runner",
        "claim": "Novi can create auditable local run records without a real LLM dependency.",
        "status": "proposed",
        "created_at": utc_now(),
        "evidence": [{"artifact_id": artifact_id, "run_id": run_id}],
        "confidence": "high",
        "scope": session["id"],
        "proposed_by": auditor,
    }
    candidate_path = Path(root) / ".novi" / "memory" / "candidates" / f"{memory_id}.yaml"
    write_yaml(candidate_path, memory)
    append_jsonl(run_dir / "events.jsonl", _event(run_id, "MemoryCandidateProposed", session["id"], auditor, "Memory candidate proposed.", {"memory_candidate_id": memory_id}))
    append_jsonl(run_dir / "events.jsonl", _event(run_id, "AuditorReviewed", session["id"], auditor, "Auditor checked deterministic records."))

    summary = "\n".join(
        [
            f"# Run {run_id}",
            "",
            f"Status: completed",
            f"Objective: {objective}",
            "",
            "The deterministic local runner wrote a context pack, one read-only tool call, one artifact, and one memory candidate.",
            "",
        ]
    )
    (run_dir / "summary.md").write_text(summary, encoding="utf-8")
    append_jsonl(run_dir / "events.jsonl", _event(run_id, "RunSummarized", session["id"], orchestrator, "Run summary written."))
    append_jsonl(run_dir / "events.jsonl", _event(run_id, "RunCompleted", session["id"], orchestrator, "Run completed."))

    run_record["status"] = "completed"
    run_record["updated_at"] = utc_now()
    run_record["completed_at"] = utc_now()
    run_record["memory_candidate_ids"] = [memory_id]
    write_yaml(run_dir / "run.yaml", run_record)

    session = load_session(root, session["id"])
    session["current_run_id"] = run_id
    session.setdefault("run_ids", []).append(run_id)
    save_session(root, session)
    return run_record
