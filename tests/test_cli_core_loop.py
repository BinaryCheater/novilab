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
