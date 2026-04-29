from pathlib import Path

from .agents import agent_snapshot, load_agent
from .ids import new_id
from .kernels import run_deepagents_kernel, validate_kernel
from .prompts import write_prompt_pack
from .store import (
    append_jsonl,
    content_hash,
    create_run_dir,
    load_session,
    save_session,
    utc_now,
    write_yaml,
)
from .tools import execute_tool


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


def _write_timeline(run_dir):
    import json

    events_path = Path(run_dir) / "events.jsonl"
    lines = ["# Run Timeline", ""]
    if events_path.exists():
        for raw in events_path.read_text(encoding="utf-8").splitlines():
            if not raw:
                continue
            event = json.loads(raw)
            lines.append(f"- {event['created_at']} `{event['type']}` {event.get('summary', '')}")
    (Path(run_dir) / "timeline.md").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def _write_memory_candidate_markdown(root, memory):
    path = Path(root) / ".novi" / "memory" / "candidates" / f"{memory['id']}.md"
    lines = [
        "# Memory Candidate",
        "",
        f"- ID: {memory['id']}",
        f"- Status: {memory['status']}",
        f"- Type: {memory['type']}",
        f"- Subject: {memory['subject']}",
        f"- Confidence: {memory['confidence']}",
        f"- Proposed by: {memory['proposed_by']}",
        "",
        "## Claim",
        "",
        memory["claim"],
        "",
        "## Evidence",
        "",
    ]
    for evidence in memory.get("evidence", []):
        lines.append(f"- Run: {evidence.get('run_id')} Artifact: {evidence.get('artifact_id')}")
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def _selected_agents(root, agents):
    if agents:
        return agents
    return [load_agent(root, "agent_orchestrator"), load_agent(root, "agent_auditor")]


def start_deterministic_run(root, session, run_type, objective, agents=None, kernel="simple", preflight_tools=True):
    validate_kernel(kernel)
    now = utc_now()
    run_id = new_id("run")
    run_dir = create_run_dir(root, run_id)
    selected_agents = _selected_agents(root, agents or [])
    participants = [agent_snapshot(agent, now) for agent in selected_agents]
    orchestrator = participants[0]["agent_id"]
    auditor = "agent_auditor"
    for participant in participants:
        if participant["role"] == "auditor":
            auditor = participant["agent_id"]

    run_record = {
        "id": run_id,
        "session_id": session["id"],
        "type": run_type,
        "objective": objective,
        "status": "running",
        "created_at": now,
        "updated_at": now,
        "actor": "local_user",
        "kernel": kernel,
        "skill_refs": ["research.review"] if run_type == "research" else [],
        "participants": participants,
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
    prompt_path, _ = write_prompt_pack(root, run_dir, run_record, context, kernel=kernel)

    for index, participant in enumerate(participants, start=1):
        step_artifact_id = new_id("art")
        step_path = run_dir / "artifacts" / f"{step_artifact_id}-agent-step.md"
        step_path.write_text(
            "\n".join(
                [
                    f"# Agent Step {index}",
                    "",
                    f"Agent: {participant['agent_id']}",
                    f"Role: {participant['role']}",
                    f"Objective: {objective}",
                    "",
                    "This deterministic step records the selected Novi agent participant and its scoped execution boundary.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        step_record = {
            "id": step_artifact_id,
            "type": "agent_step_note",
            "path": str(step_path),
            "run_id": run_id,
            "created_at": utc_now(),
            "produced_by": participant["agent_id"],
            "hash": content_hash(step_path),
            "hash_algorithm": "sha256",
            "mime_type": "text/markdown",
            "size_bytes": step_path.stat().st_size,
        }
        write_yaml(run_dir / "artifacts" / f"{step_artifact_id}.yaml", step_record)
        run_record["artifact_ids"].append(step_artifact_id)
        append_jsonl(
            run_dir / "events.jsonl",
            _event(
                run_id,
                "AgentStepCompleted",
                session["id"],
                participant["agent_id"],
                f"{participant['agent_id']} completed deterministic step.",
                {"artifact_id": step_artifact_id, "step_index": index},
            ),
        )

    tool_actor = participants[0]
    if preflight_tools:
        tool_call = execute_tool(root, run_id, tool_actor, "search_stub.query", {"query": objective}, source="runner_preflight")
        append_jsonl(run_dir / "tool_calls.jsonl", tool_call)
        if tool_call["status"] == "success":
            append_jsonl(run_dir / "events.jsonl", _event(run_id, "ToolExecuted", session["id"], tool_actor["agent_id"], "search_stub.query completed.", {"tool_call_id": tool_call["id"]}))
        else:
            append_jsonl(
                run_dir / "events.jsonl",
                _event(
                    run_id,
                    "ToolBlocked",
                    session["id"],
                    tool_actor["agent_id"],
                    f"search_stub.query blocked: {tool_call.get('block_reason', 'unknown')}.",
                    {"tool_call_id": tool_call["id"], "block_reason": tool_call.get("block_reason")},
                ),
            )

    if kernel == "deepagents":
        run_deepagents_kernel(root, run_dir, run_record, prompt_path)
        append_jsonl(run_dir / "events.jsonl", _event(run_id, "KernelExecuted", session["id"], tool_actor["agent_id"], "DeepAgents kernel completed."))

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
    _write_memory_candidate_markdown(root, memory)
    append_jsonl(run_dir / "events.jsonl", _event(run_id, "MemoryCandidateProposed", session["id"], auditor, "Memory candidate proposed.", {"memory_candidate_id": memory_id}))
    append_jsonl(run_dir / "events.jsonl", _event(run_id, "AuditorReviewed", session["id"], auditor, "Auditor checked deterministic records."))

    summary = "\n".join(
        [
            f"# Run {run_id}",
            "",
            f"Status: completed",
            f"Objective: {objective}",
            "",
            f"The deterministic local runner wrote a context pack, {len(participants)} agent step artifacts, one tool runtime call attempt, one research note artifact, and one memory candidate.",
            "",
        ]
    )
    (run_dir / "summary.md").write_text(summary, encoding="utf-8")
    append_jsonl(run_dir / "events.jsonl", _event(run_id, "RunSummarized", session["id"], orchestrator, "Run summary written."))
    append_jsonl(run_dir / "events.jsonl", _event(run_id, "RunCompleted", session["id"], orchestrator, "Run completed."))
    _write_timeline(run_dir)

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
