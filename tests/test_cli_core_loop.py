import os
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_cli(cwd, *args):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "novi_lab.cli", *args],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
    )


def parse_id(output, prefix):
    match = re.search(rf"\b({prefix}[0-9TZA-Z_a-z]+)\b", output)
    assert match, output
    return match.group(1)


def test_project_requires_python_311_for_deepagents_adapter():
    pyproject = (REPO_ROOT / "pyproject.toml").read_text()

    assert 'requires-python = ">=3.11"' in pyproject
    assert "deepagents" in pyproject


def test_init_creates_local_workspace(tmp_path):
    result = run_cli(tmp_path, "init")

    assert result.returncode == 0, result.stderr
    assert (tmp_path / ".novi" / "novi.yaml").exists()
    assert (tmp_path / ".novi" / "sessions").is_dir()
    assert (tmp_path / ".novi" / "runs").is_dir()
    assert "initialized" in result.stdout


def test_init_creates_default_agent_definitions(tmp_path):
    result = run_cli(tmp_path, "init")

    assert result.returncode == 0, result.stderr
    agent_dir = tmp_path / ".novi" / "agents"
    assert (agent_dir / "agent_orchestrator.yaml").exists()
    assert (agent_dir / "agent_auditor.yaml").exists()
    assert "role: orchestrator" in (agent_dir / "agent_orchestrator.yaml").read_text()
    assert "role: auditor" in (agent_dir / "agent_auditor.yaml").read_text()


def test_skill_list_shows_builtin_skills(tmp_path):
    run_cli(tmp_path, "init")

    result = run_cli(tmp_path, "skill", "list")

    assert result.returncode == 0, result.stderr
    assert "research.review" in result.stdout
    assert "run.audit" in result.stdout
    assert "memory.curate" in result.stdout


def test_agent_create_list_and_show(tmp_path):
    run_cli(tmp_path, "init")

    create_result = run_cli(tmp_path, "agent", "create", "agent_researcher", "--role", "researcher")
    list_result = run_cli(tmp_path, "agent", "list")
    show_result = run_cli(tmp_path, "agent", "show", "agent_researcher")

    assert create_result.returncode == 0, create_result.stderr
    assert "agent_researcher" in create_result.stdout
    assert list_result.returncode == 0, list_result.stderr
    assert "agent_orchestrator" in list_result.stdout
    assert "agent_researcher" in list_result.stdout
    assert show_result.returncode == 0, show_result.stderr
    assert "Role: researcher" in show_result.stdout
    assert "Tool scope:" in show_result.stdout


def test_agent_configuration_commands_update_scope_and_model(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "agent", "create", "agent_reader", "--role", "reader")

    grant_result = run_cli(tmp_path, "agent", "grant-tool", "agent_reader", "filesystem.read")
    skill_result = run_cli(tmp_path, "agent", "add-skill", "agent_reader", "research.review")
    model_result = run_cli(tmp_path, "agent", "set-model", "agent_reader", "openai:gpt-4.1-mini")
    revoke_result = run_cli(tmp_path, "agent", "revoke-tool", "agent_reader", "filesystem.read")
    show_result = run_cli(tmp_path, "agent", "show", "agent_reader")

    assert grant_result.returncode == 0, grant_result.stderr
    assert skill_result.returncode == 0, skill_result.stderr
    assert model_result.returncode == 0, model_result.stderr
    assert revoke_result.returncode == 0, revoke_result.stderr
    assert "Model profile: openai:gpt-4.1-mini" in show_result.stdout
    assert "research.review" in show_result.stdout
    assert "filesystem.read" not in show_result.stdout


def test_tool_list_and_show_builtin_tool(tmp_path):
    run_cli(tmp_path, "init")

    list_result = run_cli(tmp_path, "tool", "list")
    show_result = run_cli(tmp_path, "tool", "show", "search_stub.query")

    assert list_result.returncode == 0, list_result.stderr
    assert "search_stub.query" in list_result.stdout
    assert "read_only" in list_result.stdout
    assert show_result.returncode == 0, show_result.stderr
    assert "Tool: search_stub.query" in show_result.stdout
    assert "Risk: read_only" in show_result.stdout
    assert "Policy: allowed" in show_result.stdout


def test_manual_tool_call_uses_agent_scope_and_reads_workspace_file(tmp_path):
    run_cli(tmp_path, "init")
    (tmp_path / "note.md").write_text("local evidence", encoding="utf-8")
    run_cli(tmp_path, "agent", "create", "agent_reader", "--role", "reader")

    blocked = run_cli(
        tmp_path,
        "tool",
        "call",
        "filesystem.read",
        "--agent",
        "agent_reader",
        "--arg",
        "path=note.md",
    )
    run_cli(tmp_path, "agent", "grant-tool", "agent_reader", "filesystem.read")
    allowed = run_cli(
        tmp_path,
        "tool",
        "call",
        "filesystem.read",
        "--agent",
        "agent_reader",
        "--arg",
        "path=note.md",
    )

    assert blocked.returncode == 0, blocked.stderr
    assert "blocked" in blocked.stdout
    assert "tool_not_in_agent_scope" in blocked.stdout
    assert allowed.returncode == 0, allowed.stderr
    assert "success" in allowed.stdout
    assert "local evidence" in allowed.stdout


def test_session_create_writes_session_records(tmp_path):
    run_cli(tmp_path, "init")

    result = run_cli(tmp_path, "session", "create", "physical-ai literature scan")

    assert result.returncode == 0, result.stderr
    session_id = parse_id(result.stdout, "sess_")
    session_dir = tmp_path / ".novi" / "sessions" / session_id
    assert (session_dir / "session.yaml").exists()
    assert (session_dir / "summary.md").exists()
    assert (session_dir / "messages.jsonl").exists()


def test_run_start_creates_auditable_deterministic_records(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "physical-ai literature scan")

    result = run_cli(tmp_path, "run", "start", "research", "summarize recent work")

    assert result.returncode == 0, result.stderr
    run_id = parse_id(result.stdout, "run_")
    run_dir = tmp_path / ".novi" / "runs" / run_id
    assert (run_dir / "run.yaml").exists()
    assert (run_dir / "events.jsonl").read_text().count("\n") >= 5
    assert (run_dir / "tool_calls.jsonl").exists()
    assert (run_dir / "summary.md").exists()
    assert list((run_dir / "artifacts").glob("*.md"))


def test_run_writes_prompt_pack_and_human_readable_timeline(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "prompt run")

    result = run_cli(tmp_path, "run", "start", "research", "summarize context handling")

    assert result.returncode == 0, result.stderr
    run_id = parse_id(result.stdout, "run_")
    run_dir = tmp_path / ".novi" / "runs" / run_id
    prompt_text = (run_dir / "prompt.md").read_text()
    timeline_text = (run_dir / "timeline.md").read_text()
    request_text = (run_dir / "model_request.yaml").read_text()
    manifest_text = (run_dir / "prompt_parts" / "manifest.yaml").read_text()
    response_text = (run_dir / "response.md").read_text()
    model_calls_text = (run_dir / "model_calls.jsonl").read_text()
    prompt_result = run_cli(tmp_path, "run", "prompt", run_id)

    assert (run_dir / "prompt_parts" / "00-system.md").exists()
    assert (run_dir / "prompt_parts" / "20-agent.md").exists()
    assert (run_dir / "prompt_parts" / "40-tools.md").exists()
    assert "Novi Lab System Prompt" in prompt_text
    assert "Agent: agent_orchestrator" in prompt_text
    assert "Skill: research.review" in prompt_text
    assert "Tool: search_stub.query" in prompt_text
    assert "Context Management" in prompt_text
    assert "prompt.md" in request_text
    assert "prompt_parts/00-system.md" in request_text
    assert "model_profile: deterministic-local" in request_text
    assert "sha256" in manifest_text
    assert "No model executor connected" in response_text
    assert '"status": "not_connected"' in model_calls_text
    assert "RunCreated" in timeline_text
    assert "ToolExecuted" in timeline_text
    assert prompt_result.returncode == 0, prompt_result.stderr
    assert "Novi Lab System Prompt" in prompt_result.stdout


def test_run_start_records_selected_simple_kernel(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "kernel run")

    result = run_cli(tmp_path, "run", "start", "research", "record kernel", "--kernel", "simple")

    assert result.returncode == 0, result.stderr
    run_id = parse_id(result.stdout, "run_")
    run_text = (tmp_path / ".novi" / "runs" / run_id / "run.yaml").read_text()
    request_text = (tmp_path / ".novi" / "runs" / run_id / "model_request.yaml").read_text()

    assert "kernel: simple" in run_text
    assert "kernel: simple" in request_text


def test_deepagents_kernel_requires_optional_dependency(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "deepagents run")

    result = run_cli(tmp_path, "run", "start", "research", "try deepagents", "--kernel", "deepagents")

    assert result.returncode == 1
    assert "DeepAgents kernel requires optional dependency" in result.stderr


def test_memory_candidate_has_markdown_companion(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "memory markdown run")

    result = run_cli(tmp_path, "run", "start", "research", "record readable memory")

    assert result.returncode == 0, result.stderr
    run_id = parse_id(result.stdout, "run_")
    candidate_id = parse_id(run_cli(tmp_path, "memory", "review").stdout, "memcand_")
    candidate_md = tmp_path / ".novi" / "memory" / "candidates" / f"{candidate_id}.md"

    assert candidate_md.exists()
    candidate_text = candidate_md.read_text()
    assert "# Memory Candidate" in candidate_text
    assert candidate_id in candidate_text
    assert run_id in candidate_text
    assert "Evidence" in candidate_text


def test_run_start_with_selected_agents_records_sequential_steps(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "agent", "create", "agent_researcher", "--role", "researcher")
    run_cli(tmp_path, "session", "create", "agent run")

    result = run_cli(
        tmp_path,
        "run",
        "start",
        "research",
        "compare two planning approaches",
        "--agent",
        "agent_researcher",
        "--agent",
        "agent_auditor",
    )

    assert result.returncode == 0, result.stderr
    run_id = parse_id(result.stdout, "run_")
    run_dir = tmp_path / ".novi" / "runs" / run_id
    run_text = (run_dir / "run.yaml").read_text()
    events_text = (run_dir / "events.jsonl").read_text()
    summary_text = (run_dir / "summary.md").read_text()
    artifacts = list((run_dir / "artifacts").glob("*-agent-step.md"))

    assert "agent_researcher" in run_text
    assert "agent_auditor" in run_text
    assert "AgentStepCompleted" in events_text
    assert "2 agent step artifacts" in summary_text
    assert len(artifacts) == 2


def test_run_records_allowed_tool_runtime_result(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "tool run")

    result = run_cli(tmp_path, "run", "start", "research", "inspect local tool runtime")

    assert result.returncode == 0, result.stderr
    run_id = parse_id(result.stdout, "run_")
    tool_calls = (tmp_path / ".novi" / "runs" / run_id / "tool_calls.jsonl").read_text()

    assert '"tool_id": "search_stub.query"' in tool_calls
    assert '"policy_result": "allowed"' in tool_calls
    assert '"status": "success"' in tool_calls
    assert '"executor": "novi_tool_runtime"' in tool_calls


def test_run_records_blocked_tool_when_agent_lacks_scope(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "agent", "create", "agent_observer", "--role", "observer")
    run_cli(tmp_path, "session", "create", "blocked tool run")

    result = run_cli(
        tmp_path,
        "run",
        "start",
        "research",
        "attempt scoped search",
        "--agent",
        "agent_observer",
    )

    assert result.returncode == 0, result.stderr
    run_id = parse_id(result.stdout, "run_")
    inspect_result = run_cli(tmp_path, "run", "inspect", run_id)
    tool_calls = (tmp_path / ".novi" / "runs" / run_id / "tool_calls.jsonl").read_text()
    summary_text = (tmp_path / ".novi" / "runs" / run_id / "summary.md").read_text()

    assert '"tool_id": "search_stub.query"' in tool_calls
    assert '"policy_result": "blocked"' in tool_calls
    assert '"status": "blocked"' in tool_calls
    assert "search_stub.query blocked tool_not_in_agent_scope" in inspect_result.stdout
    assert "one tool runtime call attempt" in summary_text


def test_run_inspect_and_memory_review_explain_outputs(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "physical-ai literature scan")
    run_result = run_cli(
        tmp_path, "run", "start", "research", "summarize recent work"
    )
    run_id = parse_id(run_result.stdout, "run_")

    inspect_result = run_cli(tmp_path, "run", "inspect", run_id)
    review_result = run_cli(tmp_path, "memory", "review")

    assert inspect_result.returncode == 0, inspect_result.stderr
    assert "completed" in inspect_result.stdout
    assert "search_stub.query" in inspect_result.stdout
    assert review_result.returncode == 0, review_result.stderr
    assert "proposed" in review_result.stdout


def test_memory_accept_and_reject_record_review_decisions(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "physical-ai literature scan")
    run_cli(tmp_path, "run", "start", "research", "summarize recent work")
    review_result = run_cli(tmp_path, "memory", "review")
    candidate_id = parse_id(review_result.stdout, "memcand_")

    accept_result = run_cli(tmp_path, "memory", "accept", candidate_id)
    accepted_review = run_cli(tmp_path, "memory", "review")

    assert accept_result.returncode == 0, accept_result.stderr
    assert "accepted" in accept_result.stdout
    assert candidate_id not in accepted_review.stdout
    assert candidate_id in (tmp_path / ".novi" / "memory" / "episodic.jsonl").read_text()

    run_cli(tmp_path, "run", "start", "research", "summarize a second topic")
    second_review = run_cli(tmp_path, "memory", "review")
    second_candidate_id = parse_id(second_review.stdout, "memcand_")
    reject_result = run_cli(tmp_path, "memory", "reject", second_candidate_id)

    assert reject_result.returncode == 0, reject_result.stderr
    assert "rejected" in reject_result.stdout
    assert second_candidate_id not in run_cli(tmp_path, "memory", "review").stdout
