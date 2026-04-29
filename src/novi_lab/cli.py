import argparse
import os
import sys
from pathlib import Path

from .agents import (
    add_agent_list_value,
    create_agent,
    list_agents,
    load_agent,
    remove_agent_list_value,
    set_agent_model,
)
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
from .tools import execute_tool, list_tools, load_tool


def _response_body(run_dir):
    path = Path(run_dir) / "response.md"
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8").strip()
    if text.startswith("# Model Response"):
        return text.replace("# Model Response", "", 1).strip()
    return text


def _run_id_arg(root, value):
    if value != "latest":
        return value
    session = active_session(root)
    run_id = session.get("current_run_id")
    if not run_id:
        raise RuntimeError("No latest run in active session.")
    return run_id


def _run_dir(root, run_id):
    base = require_workspace(root)
    return base / "runs" / run_id


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


def cmd_agent_list(args):
    for agent in list_agents(Path.cwd()):
        print(f"{agent['id']}\t{agent['role']}\t{agent.get('model_profile', '-')}")
    return 0


def cmd_agent_show(args):
    agent = load_agent(Path.cwd(), args.agent_id)
    print(f"Agent: {agent['id']}")
    print(f"Role: {agent['role']}")
    print(f"Description: {agent.get('description', '')}")
    print(f"Model profile: {agent.get('model_profile', '-')}")
    print("Skill refs:")
    for skill_ref in agent.get("skill_refs", []):
        print(f"- {skill_ref}")
    print("Tool scope:")
    for tool_id in agent.get("tool_scope", []):
        print(f"- {tool_id}")
    print("Context scope:")
    for scope in agent.get("context_scope", []):
        print(f"- {scope}")
    print("Permission scope:")
    for scope in agent.get("permission_scope", []):
        print(f"- {scope}")
    return 0


def cmd_agent_create(args):
    agent = create_agent(Path.cwd(), args.agent_id, args.role)
    print(f"Created agent {agent['id']}: {agent['role']}")
    return 0


def cmd_agent_grant_tool(args):
    agent = add_agent_list_value(Path.cwd(), args.agent_id, "tool_scope", args.tool_id)
    print(f"Granted {args.tool_id} to {agent['id']}")
    return 0


def cmd_agent_revoke_tool(args):
    agent = remove_agent_list_value(Path.cwd(), args.agent_id, "tool_scope", args.tool_id)
    print(f"Revoked {args.tool_id} from {agent['id']}")
    return 0


def cmd_agent_add_skill(args):
    agent = add_agent_list_value(Path.cwd(), args.agent_id, "skill_refs", args.skill_id)
    print(f"Added skill {args.skill_id} to {agent['id']}")
    return 0


def cmd_agent_set_model(args):
    agent = set_agent_model(Path.cwd(), args.agent_id, args.model_profile)
    print(f"Set model profile for {agent['id']}: {agent['model_profile']}")
    return 0


def cmd_tool_list(args):
    require_workspace(Path.cwd())
    for tool in list_tools(Path.cwd()):
        print(f"{tool['id']}\t{tool.get('risk', '-')}\t{tool.get('policy', '-')}\t{tool.get('description', '')}")
    return 0


def cmd_tool_show(args):
    tool = load_tool(Path.cwd(), args.tool_id)
    print(f"Tool: {tool['id']}")
    print(f"Source: {tool.get('source', '-')}")
    print(f"Description: {tool.get('description', '')}")
    print(f"Risk: {tool.get('risk', '-')}")
    print(f"Policy: {tool.get('policy', '-')}")
    print("Input schema:")
    for key, value in tool.get("input_schema", {}).items():
        print(f"- {key}: {value}")
    print("Output artifacts:")
    for artifact_type in tool.get("output_artifacts", []):
        print(f"- {artifact_type}")
    return 0


def _parse_arg_values(values):
    parsed = {}
    for value in values:
        if "=" not in value:
            raise RuntimeError(f"Tool args must use key=value: {value}")
        key, raw = value.split("=", 1)
        parsed[key] = raw
    return parsed


def cmd_tool_call(args):
    agent = load_agent(Path.cwd(), args.agent_id)
    participant = {
        "agent_id": agent["id"],
        "tool_scope": list(agent.get("tool_scope", [])),
    }
    call = execute_tool(Path.cwd(), "manual", participant, args.tool_id, _parse_arg_values(args.arg))
    print(f"{call['tool_id']} {call['status']} {call.get('block_reason') or call.get('risk', '-')}")
    if call.get("result_ref"):
        for key, value in call["result_ref"].items():
            print(f"{key}: {value}")
    if call.get("error"):
        print(f"error: {call['error']}")
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
    agents = [load_agent(Path.cwd(), agent_id) for agent_id in args.agent]
    run = start_deterministic_run(Path.cwd(), session, args.type, args.objective, agents, kernel=args.kernel)
    print(f"Started and completed run {run['id']}: {run['objective']}")
    body = _response_body(require_workspace(Path.cwd()) / "runs" / run["id"])
    if body:
        print("")
        print("Response:")
        print(body)
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
        detail = call.get("block_reason") if call.get("status") == "blocked" else call.get("risk", "-")
        print(f"- {call['tool_id']} {call['status']} {detail}")
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


def cmd_run_prompt(args):
    base = require_workspace(Path.cwd())
    run = load_run(Path.cwd(), args.run_id)
    if not run:
        raise RuntimeError(f"Run not found: {args.run_id}")
    prompt_path = base / "runs" / args.run_id / "prompt.md"
    if not prompt_path.exists():
        raise RuntimeError(f"Prompt pack not found for run: {args.run_id}")
    print(prompt_path.read_text(encoding="utf-8").strip())
    return 0


def cmd_run_output(args):
    run_id = _run_id_arg(Path.cwd(), args.run_id)
    run_dir = _run_dir(Path.cwd(), run_id)
    body = _response_body(run_dir)
    if not body:
        raise RuntimeError(f"Response not found for run: {run_id}")
    print(body)
    return 0


def cmd_run_trace(args):
    run_id = _run_id_arg(Path.cwd(), args.run_id)
    run_dir = _run_dir(Path.cwd(), run_id)
    print(f"Run: {run_id}")
    print("Model calls:")
    for call in read_jsonl(run_dir / "model_calls.jsonl"):
        provider = call.get("model_provider") or "-"
        model = call.get("model_profile") or "-"
        print(f"- {call.get('status')} {call.get('kernel')} {provider} {model}")
        if call.get("error"):
            print(f"  error: {call['error']}")
    print("DeepAgents messages:")
    messages = read_jsonl(run_dir / "deepagents_messages.jsonl")
    if not messages:
        print("- none")
    for message in messages:
        content = str(message.get("content", "")).replace("\n", " ")
        if len(content) > 120:
            content = content[:117] + "..."
        print(f"- {message.get('index')} {message.get('role')}: {content}")
        if message.get("tool_calls"):
            print(f"  tool_calls: {message['tool_calls']}")
    print("Tool calls:")
    tool_calls = read_jsonl(run_dir / "tool_calls.jsonl")
    if not tool_calls:
        print("- none")
    for call in tool_calls:
        print(f"- {call.get('tool_id')} {call.get('status')} {call.get('source', '-')}")
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


def cmd_doctor_model(args):
    provider = os.environ.get("NOVI_MODEL_PROVIDER", "deepagents_default")
    model = os.environ.get("NOVI_MODEL", "openai:gpt-4.1-mini")
    base_url = os.environ.get("NOVI_API_BASE") or os.environ.get("OPENAI_API_BASE") or "-"
    api_key = os.environ.get("NOVI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    print(f"Provider: {provider}")
    print(f"Model: {model}")
    print(f"Base URL: {base_url}")
    print(f"API key: {'set' if api_key else 'unset'}")
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

    agent_parser = subparsers.add_parser("agent")
    agent_sub = agent_parser.add_subparsers(dest="agent_command", required=True)
    agent_list = agent_sub.add_parser("list")
    agent_list.set_defaults(func=cmd_agent_list)
    agent_show = agent_sub.add_parser("show")
    agent_show.add_argument("agent_id")
    agent_show.set_defaults(func=cmd_agent_show)
    agent_create = agent_sub.add_parser("create")
    agent_create.add_argument("agent_id")
    agent_create.add_argument("--role", required=True)
    agent_create.set_defaults(func=cmd_agent_create)
    agent_grant_tool = agent_sub.add_parser("grant-tool")
    agent_grant_tool.add_argument("agent_id")
    agent_grant_tool.add_argument("tool_id")
    agent_grant_tool.set_defaults(func=cmd_agent_grant_tool)
    agent_revoke_tool = agent_sub.add_parser("revoke-tool")
    agent_revoke_tool.add_argument("agent_id")
    agent_revoke_tool.add_argument("tool_id")
    agent_revoke_tool.set_defaults(func=cmd_agent_revoke_tool)
    agent_add_skill = agent_sub.add_parser("add-skill")
    agent_add_skill.add_argument("agent_id")
    agent_add_skill.add_argument("skill_id")
    agent_add_skill.set_defaults(func=cmd_agent_add_skill)
    agent_set_model = agent_sub.add_parser("set-model")
    agent_set_model.add_argument("agent_id")
    agent_set_model.add_argument("model_profile")
    agent_set_model.set_defaults(func=cmd_agent_set_model)

    tool_parser = subparsers.add_parser("tool")
    tool_sub = tool_parser.add_subparsers(dest="tool_command", required=True)
    tool_list = tool_sub.add_parser("list")
    tool_list.set_defaults(func=cmd_tool_list)
    tool_show = tool_sub.add_parser("show")
    tool_show.add_argument("tool_id")
    tool_show.set_defaults(func=cmd_tool_show)
    tool_call = tool_sub.add_parser("call")
    tool_call.add_argument("tool_id")
    tool_call.add_argument("--agent", dest="agent_id", required=True)
    tool_call.add_argument("--arg", action="append", default=[])
    tool_call.set_defaults(func=cmd_tool_call)

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
    run_start.add_argument("--agent", action="append", default=[])
    run_start.add_argument("--kernel", choices=["simple", "deepagents"], default="simple")
    run_start.set_defaults(func=cmd_run_start)
    run_list = run_sub.add_parser("list")
    run_list.set_defaults(func=cmd_run_list)
    run_inspect = run_sub.add_parser("inspect")
    run_inspect.add_argument("run_id")
    run_inspect.set_defaults(func=cmd_run_inspect)
    run_prompt = run_sub.add_parser("prompt")
    run_prompt.add_argument("run_id")
    run_prompt.set_defaults(func=cmd_run_prompt)
    run_output = run_sub.add_parser("output")
    run_output.add_argument("run_id")
    run_output.set_defaults(func=cmd_run_output)
    run_trace = run_sub.add_parser("trace")
    run_trace.add_argument("run_id")
    run_trace.set_defaults(func=cmd_run_trace)

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

    doctor_parser = subparsers.add_parser("doctor")
    doctor_sub = doctor_parser.add_subparsers(dest="doctor_command", required=True)
    doctor_model = doctor_sub.add_parser("model")
    doctor_model.set_defaults(func=cmd_doctor_model)

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
