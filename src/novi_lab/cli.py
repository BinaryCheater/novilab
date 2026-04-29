import argparse
import sys
from pathlib import Path

from .runner import start_deterministic_run
from .skills import discover_skills
from .store import (
    active_session,
    create_session,
    decide_memory_candidate,
    init_workspace,
    list_sessions,
    load_run,
    load_session,
    memory_candidates,
    project_config,
    read_jsonl,
    require_workspace,
    update_project_config,
)


def cmd_init(args):
    init_workspace(Path.cwd())
    print("Novi workspace initialized at .novi")
    print("Next: novi skill list")
    return 0


def cmd_skill_list(args):
    require_workspace(Path.cwd())
    skills = discover_skills(Path.cwd())
    for skill in skills:
        print(f"{skill['id']}\t{skill['source']}\t{skill['description']}")
    return 0


def cmd_session_create(args):
    session = create_session(Path.cwd(), args.title)
    print(f"Created session {session['id']}: {session['title']}")
    return 0


def cmd_session_list(args):
    for session in list_sessions(Path.cwd()):
        print(f"{session['id']}\t{session['status']}\t{session.get('current_run_id') or '-'}\t{session['title']}")
    return 0


def cmd_session_open(args):
    session = load_session(Path.cwd(), args.session_id)
    if not session:
        raise RuntimeError(f"Session not found: {args.session_id}")
    update_project_config(Path.cwd(), active_session_id=args.session_id)
    print(f"Opened session {args.session_id}")
    return 0


def cmd_session_inspect(args):
    session = load_session(Path.cwd(), args.session_id)
    if not session:
        raise RuntimeError(f"Session not found: {args.session_id}")
    print(f"Session: {session['id']}")
    print(f"Title: {session['title']}")
    print(f"Status: {session['status']}")
    print(f"Current run: {session.get('current_run_id') or '-'}")
    print("Runs:")
    for run_id in session.get("run_ids", []):
        print(f"- {run_id}")
    return 0


def cmd_run_start(args):
    session = active_session(Path.cwd())
    run = start_deterministic_run(Path.cwd(), session, args.type, args.objective)
    print(f"Started and completed run {run['id']}: {run['objective']}")
    return 0


def cmd_run_list(args):
    session = active_session(Path.cwd())
    for run_id in session.get("run_ids", []):
        run = load_run(Path.cwd(), run_id)
        print(f"{run['id']}\t{run['status']}\t{run['type']}\t{run['objective']}")
    return 0


def cmd_run_inspect(args):
    base = require_workspace(Path.cwd())
    run = load_run(Path.cwd(), args.run_id)
    if not run:
        raise RuntimeError(f"Run not found: {args.run_id}")
    run_dir = base / "runs" / args.run_id
    tool_calls = read_jsonl(run_dir / "tool_calls.jsonl")
    print(f"Run: {run['id']}")
    print(f"Objective: {run['objective']}")
    print(f"Status: {run['status']}")
    print("Participants:")
    for participant in run.get("participants", []):
        print(f"- {participant['agent_id']} ({participant['role']})")
    print("Context packs:")
    for context_id in run.get("context_pack_ids", []):
        print(f"- {context_id}")
    print("Tool calls:")
    for call in tool_calls:
        print(f"- {call['tool_id']} {call['status']} {call.get('risk', '-')}")
    print("Artifacts:")
    for artifact_id in run.get("artifact_ids", []):
        print(f"- {artifact_id}")
    print("Memory candidates:")
    for candidate_id in run.get("memory_candidate_ids", []):
        print(f"- {candidate_id}")
    summary_path = Path(run["summary_path"])
    if summary_path.exists():
        print("Summary:")
        print(summary_path.read_text(encoding="utf-8").strip())
    return 0


def cmd_memory_review(args):
    candidates = [candidate for candidate in memory_candidates(Path.cwd()) if candidate.get("status") == "proposed"]
    if not candidates:
        print("No proposed memory candidates.")
        return 0
    for candidate in candidates:
        print(f"{candidate['id']}\t{candidate['status']}\t{candidate['type']}\t{candidate['claim']}")
    return 0


def cmd_memory_accept(args):
    candidate = decide_memory_candidate(Path.cwd(), args.candidate_id, "accepted")
    print(f"Memory candidate {candidate['id']} accepted")
    return 0


def cmd_memory_reject(args):
    candidate = decide_memory_candidate(Path.cwd(), args.candidate_id, "rejected")
    print(f"Memory candidate {candidate['id']} rejected")
    return 0


def cmd_status(args):
    config = project_config(Path.cwd())
    print(f"Workspace: {config.get('workspace')}")
    print(f"Active session: {config.get('active_session_id') or '-'}")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="novi")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.set_defaults(func=cmd_init)

    status_parser = subparsers.add_parser("status")
    status_parser.set_defaults(func=cmd_status)

    skill_parser = subparsers.add_parser("skill")
    skill_sub = skill_parser.add_subparsers(dest="skill_command", required=True)
    skill_list = skill_sub.add_parser("list")
    skill_list.set_defaults(func=cmd_skill_list)

    session_parser = subparsers.add_parser("session")
    session_sub = session_parser.add_subparsers(dest="session_command", required=True)
    session_create = session_sub.add_parser("create")
    session_create.add_argument("title")
    session_create.set_defaults(func=cmd_session_create)
    session_list = session_sub.add_parser("list")
    session_list.set_defaults(func=cmd_session_list)
    session_open = session_sub.add_parser("open")
    session_open.add_argument("session_id")
    session_open.set_defaults(func=cmd_session_open)
    session_inspect = session_sub.add_parser("inspect")
    session_inspect.add_argument("session_id")
    session_inspect.set_defaults(func=cmd_session_inspect)

    run_parser = subparsers.add_parser("run")
    run_sub = run_parser.add_subparsers(dest="run_command", required=True)
    run_start = run_sub.add_parser("start")
    run_start.add_argument("type", choices=["research", "analysis", "audit"])
    run_start.add_argument("objective")
    run_start.set_defaults(func=cmd_run_start)
    run_list = run_sub.add_parser("list")
    run_list.set_defaults(func=cmd_run_list)
    run_inspect = run_sub.add_parser("inspect")
    run_inspect.add_argument("run_id")
    run_inspect.set_defaults(func=cmd_run_inspect)

    memory_parser = subparsers.add_parser("memory")
    memory_sub = memory_parser.add_subparsers(dest="memory_command", required=True)
    memory_review = memory_sub.add_parser("review")
    memory_review.set_defaults(func=cmd_memory_review)
    memory_accept = memory_sub.add_parser("accept")
    memory_accept.add_argument("candidate_id")
    memory_accept.set_defaults(func=cmd_memory_accept)
    memory_reject = memory_sub.add_parser("reject")
    memory_reject.add_argument("candidate_id")
    memory_reject.set_defaults(func=cmd_memory_reject)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
