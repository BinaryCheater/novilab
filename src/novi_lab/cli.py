import argparse
import os
import shlex
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .agents import (
    add_agent_list_value,
    create_agent,
    list_agents,
    load_agent,
    remove_agent_list_value,
    set_agent_model,
)
from .litellm_proxy import litellm_start_command, run_litellm_proxy, write_litellm_proxy_config
from .processing import process_imported_document, process_imported_documents
from .runner import start_deterministic_run
from .skills import discover_skills
from .store import (
    append_jsonl,
    accepted_knowledge,
    agent_review_contribution,
    apply_patch_contribution,
    active_session,
    append_session_message,
    check_patch_contribution,
    create_session,
    create_task,
    decide_memory_candidate,
    decide_contribution,
    import_knowledge_file,
    init_workspace,
    list_artifacts,
    list_contributions,
    list_sessions,
    list_tasks,
    load_accepted_knowledge,
    load_artifact,
    load_contribution,
    load_memory_candidate,
    load_run,
    load_session,
    load_task,
    memory_candidates,
    project_config,
    read_jsonl,
    read_yaml,
    request_changes_contribution,
    require_workspace,
    save_task,
    utc_now,
    update_project_config,
)
from .tools import execute_tool, expose_tool_to_agent, list_tools, load_tool
from .workflows import (
    advance_workflow_state,
    current_workflow_step,
    initial_workflow_state,
    list_workflows,
    load_workflow,
    workflow_step_by_id,
    workflow_round_size,
    workflow_step_instruction,
)


console = Console()


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
    print(f"Authority level: {agent.get('authority_level', 'executor')}")
    print(f"Model profile: {agent.get('model_profile', '-')}")
    print(f"Interface mode: {agent.get('interface_mode', 'headless')}")
    print("Skill refs:")
    for skill_ref in agent.get("skill_refs", []):
        print(f"- {skill_ref}")
    print("Prompt refs:")
    for prompt_ref in agent.get("prompt_refs", []):
        print(f"- {prompt_ref}")
    print("Tool scope:")
    for tool_id in agent.get("tool_scope", []):
        print(f"- {tool_id}")
    print("Context scope:")
    for scope in agent.get("context_scope", []):
        print(f"- {scope}")
    print("Permission scope:")
    for scope in agent.get("permission_scope", []):
        print(f"- {scope}")
    print("Kernel binding hints:")
    for kernel, hints in agent.get("kernel_binding_hints", {}).items():
        print(f"- {kernel}: {hints.get('binding', '-')}")
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


def cmd_workflow_list(args):
    for workflow in list_workflows(Path.cwd()):
        print(f"{workflow['id']}\t{workflow.get('version', '-')}\t{workflow.get('title', '')}")
    return 0


def cmd_workflow_show(args):
    workflow = load_workflow(Path.cwd(), args.workflow_id)
    print(f"Workflow: {workflow['id']}")
    print(f"Version: {workflow.get('version', '-')}")
    print(f"Title: {workflow.get('title', '')}")
    print(f"Status: {workflow.get('status', '-')}")
    print(f"Description: {workflow.get('description', '')}")
    print("Steps:")
    for step in workflow.get("steps", []):
        print(f"- {step.get('id')} {step.get('kind')} {step.get('actor')}: {step.get('title', '')}")
        if step.get("skill_refs"):
            print(f"  Skill refs: {', '.join(step.get('skill_refs', []))}")
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
    print("Expose to:")
    for agent_id in tool.get("expose_to", []):
        print(f"- {agent_id}")
    return 0


def cmd_tool_expose(args):
    load_agent(Path.cwd(), args.agent_id)
    tool = expose_tool_to_agent(Path.cwd(), args.tool_id, args.agent_id)
    print(f"Exposed {tool['id']} to {args.agent_id}")
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
    agent = load_agent(Path.cwd(), args.agent_id or "agent_orchestrator")
    participant = {
        "agent_id": agent["id"],
        "tool_scope": list(agent.get("tool_scope", [])),
    }
    call = execute_tool(Path.cwd(), "manual", participant, args.tool_id, _parse_arg_values(args.arg))
    print(f"{call['tool_id']} {call['status']} {call.get('block_reason') or call.get('risk', '-')}")
    print(f"agent: {agent['id']}")
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
    active_id = project_config(Path.cwd()).get("active_session_id")
    table = Table(title="Sessions")
    table.add_column("Active")
    table.add_column("Session ID")
    table.add_column("Status")
    table.add_column("Current Run")
    table.add_column("Title")
    for session in list_sessions(Path.cwd()):
        table.add_row(
            "*" if session["id"] == active_id else "",
            session["id"],
            session["status"],
            session.get("current_run_id") or "-",
            session["title"],
        )
    console.print(table)
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


def cmd_ask(args):
    session = active_session(Path.cwd())
    append_session_message(Path.cwd(), session["id"], "user", args.message)
    agents = [load_agent(Path.cwd(), agent_id) for agent_id in args.agent]
    run = start_deterministic_run(Path.cwd(), session, args.type, args.message, agents, kernel=args.kernel, preflight_tools=False)
    body = _response_body(require_workspace(Path.cwd()) / "runs" / run["id"])
    append_session_message(Path.cwd(), session["id"], "assistant", body, run_id=run["id"])
    print(f"Run: {run['id']}")
    if body:
        print("")
        print("Response:")
        print(body)
    return 0


def _prepare_task_step(root, task):
    workflow = load_workflow(root, task.get("workflow_id", "research-loop"))
    state = task.get("workflow_state") or initial_workflow_state(workflow)
    step = current_workflow_step(workflow, state)
    if not step:
        raise RuntimeError(f"Workflow {workflow.get('id')} has no executable steps.")
    task["workflow_state"] = state
    return workflow, state, step, workflow_step_instruction(workflow, task, step)


def _print_step_contract(step):
    if step.get("required_tools"):
        print(f"Required tools: {', '.join(step.get('required_tools', []))}")
    if step.get("expected_files"):
        print(f"Expected files: {', '.join(step.get('expected_files', []))}")
    if step.get("expected_artifacts"):
        print(f"Expected artifacts: {', '.join(step.get('expected_artifacts', []))}")
    if step.get("continue_from"):
        print(f"Continue from: {', '.join(step.get('continue_from', []))}")


def _artifact_types_for_run(root, run_id):
    run_dir = _run_dir(root, run_id)
    return {read_yaml(path, {}).get("type") for path in sorted((run_dir / "artifacts").glob("*.yaml"))}


def _print_expected_status(root, step, run_id=None):
    if not step:
        return
    expected_files = step.get("expected_files", [])
    expected_artifacts = step.get("expected_artifacts", [])
    if not expected_files and not expected_artifacts:
        return
    print("Expected outputs:")
    workspace = Path(root).resolve()
    for raw_path in expected_files:
        path = (workspace / raw_path).resolve()
        status = "ok" if str(path).startswith(str(workspace)) and path.is_file() else "missing"
        print(f"- file {status}: {raw_path}")
    artifact_types = _artifact_types_for_run(root, run_id) if run_id else set()
    for artifact_type in expected_artifacts:
        status = "ok" if artifact_type in artifact_types else "missing"
        print(f"- artifact {status}: {artifact_type}")


def _task_guidance_path(root, task_id):
    return require_workspace(root) / "tasks" / task_id / "guidance.jsonl"


def _append_task_guidance(root, task, kind, text):
    record = {
        "id": f"{kind}_{utc_now().replace('-', '').replace(':', '').replace('.', '_')}",
        "type": kind,
        "text": text,
        "created_at": utc_now(),
        "actor": "local_user",
    }
    guidance = list(task.get("human_guidance", []))
    guidance.append(record)
    task["human_guidance"] = guidance
    if kind == "amendment":
        task["objective"] = text
    save_task(root, task)
    append_jsonl(_task_guidance_path(root, task["id"]), record)
    return record


def _print_human_guidance(task):
    guidance = list(task.get("human_guidance", []))
    if not guidance:
        return
    print("Human guidance:")
    for item in guidance[-8:]:
        label = "amendment" if item.get("type") == "amendment" else "note"
        print(f"- {label}: {item.get('text', '')}")


def _finish_task_step(root, task, workflow, step, run):
    state = advance_workflow_state(workflow, task.get("workflow_state"), step["id"])
    task["workflow_state"] = state
    task.setdefault("run_ids", []).append(run["id"])
    task["current_run_id"] = run["id"]
    save_task(root, task)
    return task


def _run_task_step(root, task, session, args):
    workflow, _state, step, instruction = _prepare_task_step(root, task)
    agents = [load_agent(root, agent_id) for agent_id in args.agent]
    print(f"Workflow step: {step['id']} - {step.get('title', step['id'])}")
    _print_step_contract(step)
    run = start_deterministic_run(
        root,
        session,
        args.type,
        instruction,
        agents,
        kernel=args.kernel,
        preflight_tools=False,
        task_id=task["id"],
        workflow_id=workflow.get("id"),
        workflow_step=step,
    )
    _finish_task_step(root, task, workflow, step, run)
    return run


def cmd_task(args):
    root = Path.cwd()
    if args.steps < 1:
        raise RuntimeError("--steps must be 1 or greater.")
    if args.rounds is not None and args.rounds < 1:
        raise RuntimeError("--rounds must be 1 or greater.")
    if args.task_args and args.task_args[0] == "list":
        table = Table(title="Tasks")
        table.add_column("Task ID", no_wrap=True)
        table.add_column("Status")
        table.add_column("Workflow")
        table.add_column("Current Run")
        table.add_column("Objective")
        for task in list_tasks(root):
            table.add_row(task["id"], task.get("status", "-"), task.get("workflow_id", "-"), task.get("current_run_id") or "-", task.get("objective", ""))
        console.print(table)
        for task in list_tasks(root):
            print(f"Task {task['id']}: {task.get('workflow_id', '-')} {task.get('status', '-')} {task.get('objective', '')}")
        return 0
    if args.task_args and args.task_args[0] == "inspect":
        if len(args.task_args) < 2:
            raise RuntimeError("Usage: novi task inspect <task_id>")
        task = load_task(root, args.task_args[1])
        print(f"Task: {task['id']}")
        print(f"Objective: {task.get('objective', '-')}")
        print(f"Status: {task.get('status', '-')}")
        print(f"Workflow: {task.get('workflow_id', '-')}")
        print(f"Session: {task.get('session_id') or '-'}")
        print(f"Current run: {task.get('current_run_id') or '-'}")
        state = task.get("workflow_state") or {}
        print(f"Current step: {state.get('current_step_id') or '-'}")
        print(f"Completed steps: {', '.join(state.get('completed_step_ids', [])) or '-'}")
        _print_human_guidance(task)
        try:
            workflow = load_workflow(root, task.get("workflow_id", "research-loop"))
            step = current_workflow_step(workflow, state)
            if step:
                _print_step_contract(step)
                _print_expected_status(root, step, run_id=task.get("current_run_id"))
        except RuntimeError:
            pass
        print("Runs:")
        for run_id in task.get("run_ids", []):
            print(f"- {run_id}")
        return 0
    if args.task_args and args.task_args[0] == "note":
        if len(args.task_args) < 3:
            raise RuntimeError("Usage: novi task note <task_id> <text>")
        task = load_task(root, args.task_args[1])
        record = _append_task_guidance(root, task, "note", " ".join(args.task_args[2:]).strip())
        print(f"Task note: {task['id']}")
        print(record["text"])
        return 0
    if args.task_args and args.task_args[0] == "amend":
        if len(args.task_args) < 3:
            raise RuntimeError("Usage: novi task amend <task_id> <objective>")
        task = load_task(root, args.task_args[1])
        record = _append_task_guidance(root, task, "amendment", " ".join(args.task_args[2:]).strip())
        print(f"Task amended: {task['id']}")
        print(record["text"])
        return 0
    if args.task_args and args.task_args[0] == "pause":
        if len(args.task_args) < 2:
            raise RuntimeError("Usage: novi task pause <task_id>")
        task = load_task(root, args.task_args[1])
        task["status"] = "paused"
        save_task(root, task)
        print(f"Task paused: {task['id']}")
        return 0
    if args.task_args and args.task_args[0] == "resume":
        if len(args.task_args) < 2:
            raise RuntimeError("Usage: novi task resume <task_id>")
        task = load_task(root, args.task_args[1])
        task["status"] = "active"
        save_task(root, task)
        print(f"Task resumed: {task['id']}")
        return 0
    if args.task_args and args.task_args[0] in {"continue", "run"}:
        if len(args.task_args) < 2:
            raise RuntimeError("Usage: novi task continue <task_id>")
        task = load_task(root, args.task_args[1])
        if task.get("status") == "paused":
            raise RuntimeError(f"Task {task['id']} is paused. Run `novi task resume {task['id']}` before continuing.")
        pending = _pending_contributions(root, task_id=task["id"])
        if pending:
            ids = ", ".join(item["id"] for item in pending)
            raise RuntimeError(f"Task {task['id']} has pending review contribution(s): {ids}. Run `novi review --task {task['id']} --check` and `novi accept all --task {task['id']}` first.")
        session = load_session(root, task["session_id"]) if task.get("session_id") else active_session(root)
        workflow = load_workflow(root, task.get("workflow_id", "research-loop"))
        step_count = args.rounds * workflow_round_size(workflow) if args.rounds is not None else args.steps
        runs = []
        for _ in range(step_count):
            pending = _pending_contributions(root, task_id=task["id"])
            if pending:
                ids = ", ".join(item["id"] for item in pending)
                raise RuntimeError(f"Task {task['id']} has pending review contribution(s): {ids}. Run `novi review --task {task['id']} --check` and `novi accept all --task {task['id']}` first.")
            run = _run_task_step(root, task, session, args)
            runs.append(run)
            task = load_task(root, task["id"])
        print(f"Continued task: {task['id']}")
        if args.rounds is not None:
            print(f"Task rounds: {args.rounds}")
        if len(runs) == 1:
            print(f"Task run: {runs[0]['id']}")
        else:
            print(f"Task runs: {len(runs)}")
            for run in runs:
                print(f"- {run['id']}")
        return 0
    if args.task_args and args.task_args[0] == "close":
        if len(args.task_args) < 2:
            raise RuntimeError("Usage: novi task close <task_id>")
        task = load_task(root, args.task_args[1])
        task["status"] = "completed"
        save_task(root, task)
        print(f"Closed task: {task['id']}")
        return 0

    objective = " ".join(args.task_args).strip()
    if not objective:
        raise RuntimeError("Usage: novi task <objective>")
    workflow = load_workflow(root, args.workflow)
    print(f"Task: {objective}")
    try:
        session = active_session(root)
        print(f"Using active session: {session['id']}")
    except RuntimeError:
        session = create_session(root, objective)
        print(f"Created session: {session['id']}")
    task = create_task(root, objective, workflow_id=workflow["id"], session_id=session["id"])
    task["workflow_state"] = initial_workflow_state(workflow)
    save_task(root, task)
    print(f"Task ID: {task['id']}")
    print(f"Workflow: {task['workflow_id']}")
    append_session_message(root, session["id"], "user", objective)
    step_count = args.rounds * workflow_round_size(workflow) if args.rounds is not None else args.steps
    runs = []
    for _ in range(step_count):
        run = _run_task_step(root, task, session, args)
        runs.append(run)
        task = load_task(root, task["id"])
    body = _response_body(require_workspace(root) / "runs" / runs[-1]["id"])
    append_session_message(root, session["id"], "assistant", body, run_id=runs[-1]["id"])
    if args.rounds is not None:
        print(f"Task rounds: {args.rounds}")
    if len(runs) == 1:
        print(f"Task run: {runs[0]['id']}")
    else:
        print(f"Task runs: {len(runs)}")
        for run in runs:
            print(f"- {run['id']}")
    if body:
        print("")
        print("Response:")
        print(body)
    print("Next:")
    print("- novi run trace latest")
    print("- novi review --check")
    return 0


def cmd_trace(args):
    return cmd_run_trace(args)


def cmd_output(args):
    return cmd_run_output(args)


def cmd_run_list(args):
    session = active_session(Path.cwd())
    table = Table(title=f"Runs for {session['id']}")
    table.add_column("Run ID")
    table.add_column("Status")
    table.add_column("Type")
    table.add_column("Objective")
    for run_id in session.get("run_ids", []):
        run = load_run(Path.cwd(), run_id)
        table.add_row(run["id"], run["status"], run["type"], run["objective"])
    console.print(table)
    return 0


def cmd_run_inspect(args):
    base = require_workspace(Path.cwd())
    run_id = _run_id_arg(Path.cwd(), args.run_id)
    run = load_run(Path.cwd(), run_id)
    if not run:
        raise RuntimeError(f"Run not found: {run_id}")
    run_dir = base / "runs" / run_id
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
    print("Kernel bindings:")
    for binding in read_jsonl(run_dir / "kernel_bindings.jsonl"):
        print(f"- {binding.get('agent_id')} {binding.get('kernel')} {binding.get('binding')}")
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
    context = read_yaml(run_dir / "context_pack.yaml", {})
    print("Accepted knowledge:")
    refs = context.get("accepted_knowledge_refs", [])
    if not refs:
        print("- none")
    for ref in refs:
        print(f"- {ref.get('id')} {ref.get('source_artifact_id', '-')} {ref.get('title', '-')}")
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
    print("Artifacts:")
    artifact_paths = sorted((run_dir / "artifacts").glob("*.yaml"))
    if not artifact_paths:
        print("- none")
    for artifact_path in artifact_paths:
        artifact = read_yaml(artifact_path, {})
        print(f"- {artifact.get('id')} {artifact.get('type', '-')} {artifact.get('path', '-')}")
    run = load_run(Path.cwd(), run_id)
    files = run.get("deepagents_files", [])
    print("DeepAgents files:")
    if not files:
        print("- none")
    for item in files:
        print(f"- {item.get('artifact_id')} {item.get('path')}")
    print("Kernel bindings:")
    bindings = read_jsonl(run_dir / "kernel_bindings.jsonl")
    if not bindings:
        print("- none")
    for binding in bindings:
        print(f"- {binding.get('agent_id')} {binding.get('kernel')} {binding.get('binding')}")
    return 0


def _print_watch_snapshot(root, run_id):
    run = load_run(root, run_id)
    if not run:
        raise RuntimeError(f"Run not found: {run_id}")
    run_dir = _run_dir(root, run_id)
    print(f"Run: {run_id}")
    print(f"Status: {run.get('status', '-')}")
    if run.get("workflow_id"):
        print(f"Workflow: {run.get('workflow_id')} / {run.get('workflow_step_id') or '-'}")
    print(f"Objective: {run.get('objective', '-')}")
    print("")
    print("Events:")
    events = read_jsonl(run_dir / "events.jsonl")
    if not events:
        print("- none")
    for event in events[-12:]:
        print(f"- {event.get('created_at', '-')} {event.get('type', '-')}: {event.get('summary') or event.get('message') or '-'}")
    print("")
    print("Model calls:")
    model_calls = read_jsonl(run_dir / "model_calls.jsonl")
    if not model_calls:
        print("- none")
    for call in model_calls[-5:]:
        print(f"- {call.get('status', '-')} {call.get('kernel', '-')} {call.get('model_provider', '-')}/{call.get('model_profile', '-')}")
        if call.get("error"):
            print(f"  error: {call['error']}")
    print("")
    print("Tool calls:")
    tool_calls = read_jsonl(run_dir / "tool_calls.jsonl")
    if not tool_calls:
        print("- none")
    for call in tool_calls[-10:]:
        result = call.get("result_ref", {}) or {}
        detail = result.get("returncode", result.get("path", call.get("block_reason", "")))
        print(f"- {call.get('tool_id')} {call.get('status')} {detail}")
    print("")
    print("Artifacts:")
    artifact_paths = sorted((run_dir / "artifacts").glob("*.yaml"))
    if not artifact_paths:
        print("- none")
    for artifact_path in artifact_paths[-12:]:
        artifact = read_yaml(artifact_path, {})
        print(f"- {artifact.get('id')} {artifact.get('type', '-')} {artifact.get('path', '-')}")
    return run


def cmd_watch(args):
    root = Path.cwd()
    run_id = _run_id_arg(root, args.run_id)
    while True:
        run = _print_watch_snapshot(root, run_id)
        if not args.follow or run.get("status") in {"completed", "failed", "error", "blocked"}:
            return 0
        time.sleep(max(args.interval, 0))


def _workspace_relative_path(root, raw_path):
    if not raw_path:
        raise RuntimeError("Path is required.")
    path = Path(raw_path)
    if path.parts and path.parts[0] in {"experiment", "experiments"}:
        raise RuntimeError("Refusing to create Novi templates under experiment/ or experiments/. Pass an explicit scratch path outside those folders.")
    workspace = Path(root).resolve()
    requested = path.resolve() if path.is_absolute() else (workspace / path).resolve()
    if not str(requested).startswith(str(workspace)):
        raise RuntimeError("Path must be inside the current workspace.")
    return requested, str(requested.relative_to(workspace))


def cmd_experiment_init(args):
    root = Path.cwd()
    require_workspace(root)
    path, relative = _workspace_relative_path(root, args.path)
    path.mkdir(parents=True, exist_ok=True)
    outputs_dir = path / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    readme = path / "README.md"
    run_sh = path / "run.sh"
    metrics = path / "metrics.md"
    notes = path / "notes.md"
    if not readme.exists():
        readme.write_text(
            "\n".join(
                [
                    f"# {Path(relative).name}",
                    "",
                    "## Purpose",
                    "",
                    "State the question this experiment answers.",
                    "",
                    "## Run",
                    "",
                    "```bash",
                    "./run.sh",
                    "```",
                    "",
                    "## Expected Outputs",
                    "",
                    "- `outputs/` contains raw or derived result files.",
                    "- `metrics.md` summarizes metrics, failures, and next checks.",
                    "- `notes.md` records interpretation and follow-up questions.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    if not run_sh.exists():
        run_sh.write_text(
            "#!/usr/bin/env bash\nset -euo pipefail\nmkdir -p outputs\nprintf '# Metrics\\n\\n- status: draft\\n' > metrics.md\nprintf '# Notes\\n\\n- observation: fill me in\\n' > notes.md\n",
            encoding="utf-8",
        )
        run_sh.chmod(0o755)
    if not metrics.exists():
        metrics.write_text("# Metrics\n\n- status: draft\n", encoding="utf-8")
    if not notes.exists():
        notes.write_text("# Notes\n\n- observation: draft\n", encoding="utf-8")
    print(f"Experiment: {relative}")
    print(f"Run: {relative}/run.sh")
    print(f"Outputs: {relative}/outputs")
    return 0


def cmd_run_check(args):
    root = Path.cwd()
    run_id = _run_id_arg(root, args.run_id)
    run_dir = _run_dir(root, run_id)
    if not (run_dir / "run.yaml").exists():
        raise RuntimeError(f"Run not found: {run_id}")
    run = load_run(root, run_id)
    failed = False
    require_files = list(args.require_file)
    require_artifacts = list(args.require_artifact)
    if args.from_workflow:
        workflow_id = run.get("workflow_id")
        step_id = run.get("workflow_step_id")
        if workflow_id and step_id:
            workflow = load_workflow(root, workflow_id)
            step = workflow_step_by_id(workflow, step_id)
            if step:
                require_files.extend(step.get("expected_files", []))
                require_artifacts.extend(step.get("expected_artifacts", []))
    workspace = Path(root).resolve()
    for raw_path in dict.fromkeys(require_files):
        path = (workspace / raw_path).resolve()
        if str(path).startswith(str(workspace)) and path.is_file():
            print(f"file ok: {raw_path}")
        else:
            print(f"file missing: {raw_path}")
            failed = True
    artifact_records = [read_yaml(path, {}) for path in sorted((run_dir / "artifacts").glob("*.yaml"))]
    artifact_types = {record.get("type") for record in artifact_records}
    for artifact_type in dict.fromkeys(require_artifacts):
        if artifact_type in artifact_types:
            print(f"artifact ok: {artifact_type}")
        else:
            print(f"artifact missing: {artifact_type}")
            failed = True
    return 1 if failed else 0


def cmd_memory_review(args):
    candidates = [candidate for candidate in memory_candidates(Path.cwd()) if candidate.get("status") == "proposed"]
    if not candidates:
        print("No proposed memory candidates.")
        return 0
    for candidate in candidates:
        print(f"{candidate['id']}\t{candidate['status']}\t{candidate['type']}\t{candidate['claim']}")
    return 0


def cmd_memory_list(args):
    table = Table(title="Memory Candidates")
    table.add_column("ID", no_wrap=True)
    table.add_column("Status")
    table.add_column("Type")
    table.add_column("Subject")
    table.add_column("Claim")
    for candidate in memory_candidates(Path.cwd()):
        table.add_row(
            candidate["id"],
            candidate.get("status", "-"),
            candidate.get("type", "-"),
            candidate.get("subject", "-"),
            candidate.get("claim", ""),
        )
    console.print(table)
    return 0


def cmd_memory_show(args):
    candidate, _ = load_memory_candidate(Path.cwd(), args.candidate_id)
    print(f"Memory candidate: {candidate['id']}")
    print(f"Status: {candidate.get('status', '-')}")
    print(f"Type: {candidate.get('type', '-')}")
    print(f"Subject: {candidate.get('subject', '-')}")
    print(f"Scope: {candidate.get('scope', '-')}")
    print(f"Confidence: {candidate.get('confidence', '-')}")
    print(f"Proposed by: {candidate.get('proposed_by', '-')}")
    print(f"Reviewed by: {candidate.get('reviewed_by', '-')}")
    print(f"Reviewed at: {candidate.get('reviewed_at', '-')}")
    print("Claim:")
    print(candidate.get("claim", ""))
    print("Evidence:")
    for evidence in candidate.get("evidence", []):
        print(f"- Run: {evidence.get('run_id')} Artifact: {evidence.get('artifact_id')}")
    return 0


def cmd_memory_accept(args):
    candidate = decide_memory_candidate(Path.cwd(), args.candidate_id, "accepted")
    print(f"Memory candidate {candidate['id']} accepted")
    return 0


def cmd_memory_reject(args):
    candidate = decide_memory_candidate(Path.cwd(), args.candidate_id, "rejected")
    print(f"Memory candidate {candidate['id']} rejected")
    return 0


def _pending_memory(root):
    return [candidate for candidate in memory_candidates(root) if candidate.get("status") == "proposed"]


def _pending_contributions(root, task_id=None):
    contributions = [contribution for contribution in list_contributions(root) if contribution.get("status") == "pending"]
    if task_id:
        contributions = [contribution for contribution in contributions if contribution.get("task_id") == task_id]
    return contributions


def _resolve_pending_contributions(root, selector, task_id=None, reviewed=False):
    pending = _pending_contributions(root, task_id=task_id)
    if reviewed:
        pending = [item for item in pending if item.get("reviewer_decision") == "safe_to_accept"]
    if selector == "all":
        return pending
    if selector == "latest":
        if not pending:
            if reviewed:
                return []
            raise RuntimeError("No pending contributions.")
        pending.sort(key=lambda item: item.get("created_at", ""))
        return [pending[-1]]
    contribution, _ = load_contribution(root, selector)
    return [contribution]


def _accept_contribution(root, contribution_id):
    contribution, _ = load_contribution(root, contribution_id)
    if contribution.get("type") == "document_patch":
        return apply_patch_contribution(root, contribution_id), "accepted and merged"
    return decide_contribution(root, contribution_id, "accepted"), "accepted"


def cmd_review(args):
    root = Path.cwd()
    pending_memory = _pending_memory(root)
    pending_contributions = _pending_contributions(root, task_id=args.task)
    summary = Table(title="Pending Review")
    summary.add_column("Queue")
    summary.add_column("Count")
    summary.add_row("Memory candidates", str(len(pending_memory)))
    summary.add_row("Contributions", str(len(pending_contributions)))
    summary.add_row("Workflow patches", "0")
    summary.add_row("Approvals", "0")
    console.print(summary)

    if pending_memory:
        memory_table = Table(title="Memory Candidates")
        memory_table.add_column("ID")
        memory_table.add_column("Status")
        memory_table.add_column("Type")
        memory_table.add_column("Claim")
        for candidate in pending_memory:
            memory_table.add_row(candidate["id"], candidate.get("status", "-"), candidate.get("type", "-"), candidate.get("claim", ""))
        console.print(memory_table)

    if pending_contributions:
        contribution_table = Table(title="Contributions")
        contribution_table.add_column("ID", no_wrap=True)
        contribution_table.add_column("Status")
        contribution_table.add_column("Type")
        if args.check:
            contribution_table.add_column("Check")
        contribution_table.add_column("Title")
        for contribution in pending_contributions:
            check_status = "-"
            if args.check and contribution.get("type") == "document_patch":
                check_status = check_patch_contribution(root, contribution["id"]).get("status", "-")
            if args.agent:
                reviewed = agent_review_contribution(root, contribution["id"])
                print(f"Reviewer {reviewed.get('reviewer_agent')}: {reviewed['id']} {reviewed.get('reviewer_decision')} - {reviewed.get('reviewer_reason')}")
            contribution_table.add_row(
                contribution["id"],
                contribution.get("status", "-"),
                contribution.get("type", "-"),
                *([check_status] if args.check else []),
                contribution.get("title", ""),
            )
        console.print(contribution_table)
        if args.check:
            for contribution in pending_contributions:
                if contribution.get("type") == "document_patch":
                    result = contribution.get("check_result") or check_patch_contribution(root, contribution["id"])
                    print(f"Check {contribution['id']}: {result.get('status', '-')}")
    return 0


def cmd_accept(args):
    accepted = []
    for contribution in _resolve_pending_contributions(Path.cwd(), args.selector, task_id=args.task, reviewed=args.reviewed):
        record, message = _accept_contribution(Path.cwd(), contribution["id"])
        accepted.append(record["id"])
        print(f"Contribution {record['id']} {message}")
        if record.get("accepted_knowledge_path"):
            print(f"Accepted knowledge: {record['accepted_knowledge_path']}")
    if not accepted and args.reviewed:
        print("No reviewed safe contributions to accept.")
    elif not accepted:
        print("No pending contributions to accept.")
    return 0


def cmd_import(args):
    contribution, artifact = import_knowledge_file(Path.cwd(), args.source)
    print(f"Imported {contribution['title']}")
    print(f"Contribution: {contribution['id']}")
    print(f"Artifact: {artifact['id']}")
    return 0


def _progress(message):
    print(f"[novi] {message}", flush=True)


def _latest_pending_import(root):
    imports = [
        item
        for item in list_contributions(root)
        if item.get("type") == "knowledge_import" and item.get("status") == "pending"
    ]
    if not imports:
        raise RuntimeError("No pending knowledge import contribution found. Run `novi import <file>` first.")
    imports.sort(key=lambda item: item.get("created_at", ""))
    return imports[-1]


def _print_process_result(result):
    print(f"Run: {result['run']['id']}")
    print(f"Kernel: {result['run'].get('kernel', '-')}")
    print(f"Analysis artifact: {result['analysis_artifact']['id']}")
    patch_contributions = result.get("patch_contributions") or ([result["patch_contribution"]] if result.get("patch_contribution") else [])
    if patch_contributions:
        print("Patch contributions:")
        for patch in patch_contributions:
            print(f"Patch contribution: {patch['id']}")
        print("Next:")
        for patch in patch_contributions:
            patch_id = patch["id"]
            print(f"- novi contribution inspect {patch_id}")
            print(f"- novi contribution check {patch_id}")
            print(f"- novi contribution accept {patch_id}")
    else:
        print("No patch contribution created")
    if result.get("questions_for_human"):
        print("Questions for human:")
        for question in result["questions_for_human"]:
            print(f"- {question}")


def cmd_process(args):
    contribution_id = args.contribution_id
    if not contribution_id:
        contribution = _latest_pending_import(Path.cwd())
        contribution_id = contribution["id"]
        print(f"Using latest pending import contribution: {contribution_id}", flush=True)
    result = process_imported_document(
        Path.cwd(),
        contribution_id,
        workflow=args.workflow,
        target=args.target,
        kernel=args.kernel,
        progress=_progress,
        hint=getattr(args, "hint", None),
        task_id=getattr(args, "task", None),
    )
    _print_process_result(result)
    return 0


def cmd_ingest(args):
    root = Path.cwd()
    try:
        session = active_session(root)
        print(f"Using active session: {session['id']}", flush=True)
    except RuntimeError:
        session = create_session(root, args.session_title)
        print(f"Created session: {session['id']}", flush=True)
    contributions = []
    for source in args.sources:
        contribution, artifact = import_knowledge_file(root, source)
        contributions.append(contribution)
        print(f"Imported: {contribution['id']}")
        print(f"Import artifact: {artifact['id']}")
    result = process_imported_documents(
        root,
        [item["id"] for item in contributions],
        workflow=args.workflow,
        target=args.target,
        kernel=args.kernel,
        progress=_progress,
        hint=args.hint,
        task_id=args.task,
    )
    _print_process_result(result)
    if args.accept:
        patches = result.get("patch_contributions") or []
        if not patches:
            raise RuntimeError("No patch contribution was created; nothing to accept.")
        for patch in patches:
            accepted = apply_patch_contribution(root, patch["id"])
            print(f"Accepted and merged: {accepted['id']}")
    return 0


def cmd_artifact_list(args):
    table = Table(title="Artifacts")
    table.add_column("ID", no_wrap=True)
    table.add_column("Type")
    table.add_column("Run")
    table.add_column("Path")
    for artifact in list_artifacts(Path.cwd()):
        table.add_row(
            artifact["id"],
            artifact.get("type", "-"),
            artifact.get("run_id", "-"),
            artifact.get("path", "-"),
        )
    console.print(table)
    return 0


def cmd_artifact_show(args):
    artifact = load_artifact(Path.cwd(), args.artifact_id)
    print(f"Artifact: {artifact['id']}")
    print(f"Type: {artifact.get('type', '-')}")
    print(f"Path: {artifact.get('path', '-')}")
    print(f"Run: {artifact.get('run_id', '-')}")
    print(f"Produced by: {artifact.get('produced_by', '-')}")
    print(f"Source path: {artifact.get('source_path', '-')}")
    print(f"MIME type: {artifact.get('mime_type', '-')}")
    print(f"Size bytes: {artifact.get('size_bytes', '-')}")
    print(f"SHA256: {artifact.get('hash', '-')}")
    return 0


def cmd_knowledge_list(args):
    table = Table(title="Accepted Knowledge")
    table.add_column("ID", no_wrap=True)
    table.add_column("Title")
    table.add_column("Source Artifact")
    table.add_column("Reviewed At")
    for record in accepted_knowledge(Path.cwd()):
        table.add_row(
            record["id"],
            record.get("title", "-"),
            record.get("source_artifact_id", "-"),
            record.get("reviewed_at", "-"),
        )
    console.print(table)
    return 0


def cmd_knowledge_show(args):
    record = load_accepted_knowledge(Path.cwd(), args.knowledge_id)
    print(f"Knowledge: {record['id']}")
    print(f"Title: {record.get('title', '-')}")
    print(f"Source artifact: {record.get('source_artifact_id', '-')}")
    print(f"Raw path: {record.get('raw_path', '-')}")
    print(f"Accepted path: {record.get('accepted_path', '-')}")
    print(f"Reviewed by: {record.get('reviewed_by', '-')}")
    print(f"Reviewed at: {record.get('reviewed_at', '-')}")
    if record.get("content"):
        print("")
        print(record["content"].strip())
    return 0


def cmd_contribution_list(args):
    table = Table(title="Contributions")
    table.add_column("ID", no_wrap=True)
    table.add_column("Status")
    table.add_column("Type")
    table.add_column("Target")
    table.add_column("Title")
    for contribution in list_contributions(Path.cwd()):
        table.add_row(
            contribution["id"],
            contribution.get("status", "-"),
            contribution.get("type", "-"),
            contribution.get("target", "-"),
            contribution.get("title", ""),
        )
    console.print(table)
    return 0


def cmd_contribution_inspect(args):
    contribution, _ = load_contribution(Path.cwd(), args.contribution_id)
    print(f"Contribution: {contribution['id']}")
    print(f"Status: {contribution.get('status', '-')}")
    print(f"Type: {contribution.get('type', '-')}")
    print(f"Title: {contribution.get('title', '')}")
    print(f"Target: {contribution.get('target', '-')}")
    print(f"Source: {contribution.get('source', '-')}")
    print(f"Source artifact: {contribution.get('artifact_id', '-')}")
    print(f"Source actor: {contribution.get('source_actor', '-')}")
    if contribution.get("source_refs"):
        print("Source refs:")
        for ref in contribution.get("source_refs", []):
            print(f"- {ref.get('type')}: {ref.get('id')}")
    if contribution.get("patch_path"):
        print(f"Patch: {contribution.get('patch_path')}")
    if contribution.get("check_result"):
        print(f"Check: {contribution['check_result'].get('status')}")
    if contribution.get("merged_at"):
        print(f"Merged at: {contribution.get('merged_at')}")
    if contribution.get("changed_files"):
        print("Changed files:")
        for changed_file in contribution.get("changed_files", []):
            print(f"- {changed_file}")
    if contribution.get("conflict_reason"):
        print(f"Conflict reason: {contribution.get('conflict_reason')}")
    if contribution.get("review_comment"):
        print(f"Review comment: {contribution.get('review_comment')}")
    if contribution.get("reviewer_decision"):
        print(f"Reviewer decision: {contribution.get('reviewer_decision')}")
        print(f"Reviewer: {contribution.get('reviewer_agent', '-')}")
        print(f"Reviewer reason: {contribution.get('reviewer_reason', '-')}")
    return 0


def cmd_contribution_reject(args):
    contribution = decide_contribution(Path.cwd(), args.contribution_id, "rejected")
    print(f"Contribution {contribution['id']} rejected")
    return 0


def cmd_contribution_accept(args):
    contribution, message = _accept_contribution(Path.cwd(), args.contribution_id)
    print(f"Contribution {contribution['id']} {message}")
    if contribution.get("accepted_knowledge_path"):
        print(f"Accepted knowledge: {contribution['accepted_knowledge_path']}")
    return 0


def cmd_contribution_check(args):
    result = check_patch_contribution(Path.cwd(), args.contribution_id)
    if result["status"] == "would_apply":
        print(f"Contribution {args.contribution_id} would apply")
        for changed_file in result.get("changed_files", []):
            print(f"- {changed_file}")
        return 0
    print(f"Contribution {args.contribution_id} conflict: {result.get('reason', '-')}")
    return 1


def cmd_contribution_request_changes(args):
    contribution = request_changes_contribution(Path.cwd(), args.contribution_id, args.reason)
    print(f"Contribution {contribution['id']} changes requested")
    return 0


def cmd_status(args):
    config = project_config(Path.cwd())
    print(f"Workspace: {config.get('workspace')}")
    print(f"Active session: {config.get('active_session_id') or '-'}")
    return 0


def cmd_ps(args):
    root = Path.cwd()
    config = project_config(root)
    sessions = list_sessions(root)
    active_id = config.get("active_session_id")
    active = load_session(root, active_id) if active_id else None

    if active:
        console.print(
            Panel(
                "\n".join(
                    [
                        f"Session: {active['id']}",
                        f"Title: {active['title']}",
                        f"Current run: {active.get('current_run_id') or '-'}",
                    ]
                ),
                title="Active session",
            )
        )
    else:
        console.print(Panel("No active session", title="Active session"))

    session_table = Table(title="Sessions")
    session_table.add_column("Active")
    session_table.add_column("Session ID")
    session_table.add_column("Status")
    session_table.add_column("Current Run")
    session_table.add_column("Title")
    for session in sessions:
        session_table.add_row(
            "*" if session["id"] == active_id else "",
            session["id"],
            session["status"],
            session.get("current_run_id") or "-",
            session["title"],
        )
    console.print(session_table)

    run_table = Table(title="Recent runs")
    run_table.add_column("Run ID")
    run_table.add_column("Status")
    run_table.add_column("Type")
    run_table.add_column("Objective")
    recent_run_ids = []
    if active:
        recent_run_ids = list(reversed(active.get("run_ids", [])))[:5]
    for run_id in recent_run_ids:
        run = load_run(root, run_id)
        run_table.add_row(run["id"], run["status"], run["type"], run["objective"])
    console.print(run_table)

    pending_memory = _pending_memory(root)
    pending_contributions = _pending_contributions(root)
    pending_table = Table(title="Pending review")
    pending_table.add_column("Queue")
    pending_table.add_column("Count")
    pending_table.add_row("Memory candidates", str(len(pending_memory)))
    pending_table.add_row("Contributions", str(len(pending_contributions)))
    pending_table.add_row("Workflow patches", "0")
    pending_table.add_row("Approvals", "0")
    console.print(pending_table)
    return 0


def _configured_model_from_args(args):
    if args.provider == "siliconflow":
        return {
            "provider": "openai_chat",
            "model": args.model,
            "base_url": args.base_url or "https://api.siliconflow.cn/v1",
            "api_key": args.api_key,
        }
    if args.provider == "openai-chat":
        if not args.base_url:
            raise RuntimeError("openai-chat provider requires --base-url.")
        return {
            "provider": "openai_chat",
            "model": args.model,
            "base_url": args.base_url,
            "api_key": args.api_key,
        }
    if args.provider == "openai-responses":
        return {
            "provider": "openai_responses",
            "model": args.model,
            "base_url": args.base_url,
            "api_key": args.api_key,
        }
    if args.provider == "litellm-proxy":
        return {
            "provider": "litellm_proxy",
            "model": args.model,
            "base_url": args.base_url or "http://localhost:4000/v1",
            "api_key": args.api_key,
            "api_shape": args.api_shape,
            "auto_start": not args.no_auto_start,
        }
    raise RuntimeError(f"Unknown model provider: {args.provider}")


def cmd_configure_model(args):
    model_config = _configured_model_from_args(args)
    update_project_config(Path.cwd(), model=model_config)
    print(f"Configured model provider: {model_config['provider']}")
    print(f"Model: {model_config['model']}")
    print(f"Base URL: {model_config.get('base_url') or '-'}")
    print(f"API key: {'set' if model_config.get('api_key') else 'unset'}")
    return 0


def cmd_doctor_model(args):
    config = project_config(Path.cwd()).get("model", {}) or {}
    provider = config.get("provider") or os.environ.get("NOVI_MODEL_PROVIDER", "deepagents_default")
    model = config.get("model") or os.environ.get("NOVI_MODEL", "openai:gpt-4.1-mini")
    base_url = config.get("base_url") or os.environ.get("NOVI_API_BASE") or os.environ.get("OPENAI_API_BASE") or "-"
    api_key = config.get("api_key") or os.environ.get("NOVI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    print(f"Provider: {provider}")
    print(f"Model: {model}")
    print(f"Base URL: {base_url}")
    print(f"API key: {'set' if api_key else 'unset'}")
    return 0


def cmd_litellm_init(args):
    path = write_litellm_proxy_config(
        Path.cwd(),
        model_name=args.model_name,
        upstream_model=args.upstream_model,
        upstream_api_key_env=args.upstream_api_key_env,
        upstream_base_url=args.upstream_base_url,
        proxy_api_key_env=args.proxy_api_key_env,
        port=args.port,
        api_shape=args.api_shape,
    )
    print(f"LiteLLM proxy config written: {path}")
    print(f"Configured model provider: litellm_proxy")
    print(f"Model alias: {args.model_name}")
    print(f"Base URL: http://localhost:{args.port}/v1")
    print(f"API shape: {args.api_shape}")
    print(f"Auto start: enabled")
    print(f"Manual start: novi litellm start --port {args.port}")
    return 0


def cmd_litellm_start(args):
    command = litellm_start_command(Path.cwd(), port=args.port)
    if args.print_command:
        print(" ".join(shlex.quote(part) for part in command))
        return 0
    return run_litellm_proxy(Path.cwd(), port=args.port)


def build_parser():
    parser = argparse.ArgumentParser(prog="novi")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.set_defaults(func=cmd_init)

    status_parser = subparsers.add_parser("status")
    status_parser.set_defaults(func=cmd_status)

    ps_parser = subparsers.add_parser("ps")
    ps_parser.set_defaults(func=cmd_ps)

    watch_parser = subparsers.add_parser("watch")
    watch_parser.add_argument("run_id", nargs="?", default="latest")
    watch_parser.add_argument("--follow", action="store_true")
    watch_parser.add_argument("--interval", type=float, default=2.0)
    watch_parser.set_defaults(func=cmd_watch)

    experiment_parser = subparsers.add_parser("experiment")
    experiment_sub = experiment_parser.add_subparsers(dest="experiment_command", required=True)
    experiment_init = experiment_sub.add_parser("init")
    experiment_init.add_argument("path")
    experiment_init.set_defaults(func=cmd_experiment_init)

    import_parser = subparsers.add_parser("import")
    import_parser.add_argument("source")
    import_parser.set_defaults(func=cmd_import)

    ingest_parser = subparsers.add_parser("ingest")
    ingest_parser.add_argument("sources", nargs="+")
    ingest_parser.add_argument("--target")
    ingest_parser.add_argument("--hint")
    ingest_parser.add_argument("--task")
    ingest_parser.add_argument("--workflow", default="document-merge")
    ingest_parser.add_argument("--kernel", choices=["simple", "deepagents"], default="deepagents")
    ingest_parser.add_argument("--session-title", default="document ingest")
    ingest_parser.add_argument("--accept", action="store_true")
    ingest_parser.set_defaults(func=cmd_ingest)

    process_parser = subparsers.add_parser("process")
    process_parser.add_argument("contribution_id", nargs="?")
    process_parser.add_argument("--workflow", default="document-merge")
    process_parser.add_argument("--target")
    process_parser.add_argument("--hint")
    process_parser.add_argument("--task")
    process_parser.add_argument("--kernel", choices=["simple", "deepagents"], default="deepagents")
    process_parser.set_defaults(func=cmd_process)

    accept_parser = subparsers.add_parser("accept")
    accept_parser.add_argument("selector", nargs="?", default="latest")
    accept_parser.add_argument("--task")
    accept_parser.add_argument("--reviewed", action="store_true")
    accept_parser.set_defaults(func=cmd_accept)

    review_parser = subparsers.add_parser("review")
    review_parser.add_argument("--check", action="store_true")
    review_parser.add_argument("--task")
    review_parser.add_argument("--agent", action="store_true")
    review_parser.set_defaults(func=cmd_review)

    artifact_parser = subparsers.add_parser("artifact")
    artifact_sub = artifact_parser.add_subparsers(dest="artifact_command", required=True)
    artifact_list = artifact_sub.add_parser("list")
    artifact_list.set_defaults(func=cmd_artifact_list)
    artifact_show = artifact_sub.add_parser("show")
    artifact_show.add_argument("artifact_id")
    artifact_show.set_defaults(func=cmd_artifact_show)

    knowledge_parser = subparsers.add_parser("knowledge")
    knowledge_sub = knowledge_parser.add_subparsers(dest="knowledge_command", required=True)
    knowledge_list = knowledge_sub.add_parser("list")
    knowledge_list.set_defaults(func=cmd_knowledge_list)
    knowledge_show = knowledge_sub.add_parser("show")
    knowledge_show.add_argument("knowledge_id")
    knowledge_show.set_defaults(func=cmd_knowledge_show)

    configure_parser = subparsers.add_parser("configure")
    configure_sub = configure_parser.add_subparsers(dest="configure_command", required=True)
    configure_model = configure_sub.add_parser("model")
    configure_model.add_argument("provider", choices=["siliconflow", "openai-chat", "openai-responses", "litellm-proxy"])
    configure_model.add_argument("--model", required=True)
    configure_model.add_argument("--api-key")
    configure_model.add_argument("--base-url")
    configure_model.add_argument("--api-shape", choices=["responses", "chat_completions"], default="responses")
    configure_model.add_argument("--no-auto-start", action="store_true")
    configure_model.set_defaults(func=cmd_configure_model)

    litellm_parser = subparsers.add_parser("litellm")
    litellm_sub = litellm_parser.add_subparsers(dest="litellm_command", required=True)
    litellm_init = litellm_sub.add_parser("init")
    litellm_init.add_argument("--model-name", required=True)
    litellm_init.add_argument("--upstream-model", required=True)
    litellm_init.add_argument("--upstream-api-key-env", required=True)
    litellm_init.add_argument("--upstream-base-url")
    litellm_init.add_argument("--proxy-api-key-env", default="LITELLM_PROXY_API_KEY")
    litellm_init.add_argument("--api-shape", choices=["responses", "chat_completions"], default="responses")
    litellm_init.add_argument("--port", type=int, default=4000)
    litellm_init.set_defaults(func=cmd_litellm_init)
    litellm_start = litellm_sub.add_parser("start")
    litellm_start.add_argument("--port", type=int, default=4000)
    litellm_start.add_argument("--print-command", action="store_true")
    litellm_start.set_defaults(func=cmd_litellm_start)

    ask_parser = subparsers.add_parser("ask")
    ask_parser.add_argument("message")
    ask_parser.add_argument("--type", choices=["research", "analysis", "audit"], default="research")
    ask_parser.add_argument("--agent", action="append", default=[])
    ask_parser.add_argument("--kernel", choices=["simple", "deepagents"], default="deepagents")
    ask_parser.set_defaults(func=cmd_ask)

    task_parser = subparsers.add_parser("task")
    task_parser.add_argument("task_args", nargs="*")
    task_parser.add_argument("--workflow", default="research-loop")
    task_parser.add_argument("--type", choices=["research", "analysis", "audit"], default="research")
    task_parser.add_argument("--agent", action="append", default=[])
    task_parser.add_argument("--kernel", choices=["simple", "deepagents"], default="deepagents")
    task_parser.add_argument("--steps", type=int, default=1)
    task_parser.add_argument("--rounds", type=int)
    task_parser.set_defaults(func=cmd_task)

    trace_parser = subparsers.add_parser("trace")
    trace_parser.add_argument("run_id", nargs="?", default="latest")
    trace_parser.set_defaults(func=cmd_trace)

    output_parser = subparsers.add_parser("output")
    output_parser.add_argument("run_id", nargs="?", default="latest")
    output_parser.set_defaults(func=cmd_output)

    skill_parser = subparsers.add_parser("skill")
    skill_sub = skill_parser.add_subparsers(dest="skill_command", required=True)
    skill_list = skill_sub.add_parser("list")
    skill_list.set_defaults(func=cmd_skill_list)

    workflow_parser = subparsers.add_parser("workflow")
    workflow_sub = workflow_parser.add_subparsers(dest="workflow_command", required=True)
    workflow_list = workflow_sub.add_parser("list")
    workflow_list.set_defaults(func=cmd_workflow_list)
    workflow_show = workflow_sub.add_parser("show")
    workflow_show.add_argument("workflow_id")
    workflow_show.set_defaults(func=cmd_workflow_show)

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
    tool_expose = tool_sub.add_parser("expose")
    tool_expose.add_argument("tool_id")
    tool_expose.add_argument("agent_id")
    tool_expose.set_defaults(func=cmd_tool_expose)
    tool_call = tool_sub.add_parser("call")
    tool_call.add_argument("tool_id")
    tool_call.add_argument("--agent", dest="agent_id")
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
    run_check = run_sub.add_parser("check")
    run_check.add_argument("run_id")
    run_check.add_argument("--require-file", action="append", default=[])
    run_check.add_argument("--require-artifact", action="append", default=[])
    run_check.add_argument("--from-workflow", action="store_true")
    run_check.set_defaults(func=cmd_run_check)

    memory_parser = subparsers.add_parser("memory")
    memory_sub = memory_parser.add_subparsers(dest="memory_command", required=True)
    memory_list = memory_sub.add_parser("list")
    memory_list.set_defaults(func=cmd_memory_list)
    memory_show = memory_sub.add_parser("show")
    memory_show.add_argument("candidate_id")
    memory_show.set_defaults(func=cmd_memory_show)
    memory_review = memory_sub.add_parser("review")
    memory_review.set_defaults(func=cmd_memory_review)
    memory_accept = memory_sub.add_parser("accept")
    memory_accept.add_argument("candidate_id")
    memory_accept.set_defaults(func=cmd_memory_accept)
    memory_reject = memory_sub.add_parser("reject")
    memory_reject.add_argument("candidate_id")
    memory_reject.set_defaults(func=cmd_memory_reject)

    contribution_parser = subparsers.add_parser("contribution")
    contribution_sub = contribution_parser.add_subparsers(dest="contribution_command", required=True)
    contribution_list = contribution_sub.add_parser("list")
    contribution_list.set_defaults(func=cmd_contribution_list)
    contribution_inspect = contribution_sub.add_parser("inspect")
    contribution_inspect.add_argument("contribution_id")
    contribution_inspect.set_defaults(func=cmd_contribution_inspect)
    contribution_check = contribution_sub.add_parser("check")
    contribution_check.add_argument("contribution_id")
    contribution_check.set_defaults(func=cmd_contribution_check)
    contribution_reject = contribution_sub.add_parser("reject")
    contribution_reject.add_argument("contribution_id")
    contribution_reject.set_defaults(func=cmd_contribution_reject)
    contribution_accept = contribution_sub.add_parser("accept")
    contribution_accept.add_argument("contribution_id")
    contribution_accept.set_defaults(func=cmd_contribution_accept)
    contribution_request_changes = contribution_sub.add_parser("request-changes")
    contribution_request_changes.add_argument("contribution_id")
    contribution_request_changes.add_argument("--reason", required=True)
    contribution_request_changes.set_defaults(func=cmd_contribution_request_changes)

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
