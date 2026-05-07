from pathlib import Path

from .store import read_yaml, require_workspace, write_yaml


def default_workflows():
    return [
        {
            "id": "document-merge",
            "version": 1,
            "status": "active",
            "title": "Document Merge",
            "description": "Process an imported document into an analysis note and optional document patch contribution.",
            "inputs": {
                "required": ["import_contribution"],
                "optional": ["target_document"],
            },
            "default_agents": {
                "curator": "agent_orchestrator",
                "reviewer": "agent_auditor",
            },
            "steps": [
                {
                    "id": "load_import",
                    "title": "Load imported document",
                    "kind": "load_source",
                    "actor": "system",
                    "inputs": ["import_contribution", "source_artifact"],
                    "outputs": [{"type": "context", "name": "imported_document"}],
                    "required": True,
                },
                {
                    "id": "analyze",
                    "title": "Analyze imported document",
                    "kind": "produce_artifact",
                    "actor": "agent",
                    "agent_ref": "agent_orchestrator",
                    "skill_refs": ["document.curate"],
                    "inputs": ["imported_document"],
                    "outputs": [{"type": "artifact", "artifact_type": "analysis_note"}],
                    "instructions": "Extract useful ideas, uncertain claims, source links, and likely merge targets. Do not modify accepted documents directly.",
                    "required": True,
                },
                {
                    "id": "choose_target",
                    "title": "Choose merge target",
                    "kind": "review_gate",
                    "actor": "human",
                    "condition": "target_missing",
                    "decision": {"options": ["provide_target", "analysis_only", "reject_import"]},
                    "required": False,
                },
                {
                    "id": "draft_patch",
                    "title": "Draft document patch",
                    "kind": "produce_contribution",
                    "actor": "agent",
                    "agent_ref": "agent_orchestrator",
                    "skill_refs": ["document.merge"],
                    "condition": "target_provided",
                    "inputs": ["imported_document", "analysis_note", "target_document"],
                    "outputs": [{"type": "contribution", "contribution_type": "document_patch"}],
                    "instructions": "Propose a patch against the target Markdown document. Preserve source links and cite the import contribution and analysis note.",
                    "required": False,
                    "review_required": True,
                },
                {
                    "id": "check_patch",
                    "title": "Check patch",
                    "kind": "check",
                    "actor": "system",
                    "condition": "document_patch_created",
                    "rules": ["target_scope_allowed", "source_refs_required_for_agent_patch", "target_base_hash_matches"],
                    "required": True,
                },
                {
                    "id": "review_patch",
                    "title": "Review patch",
                    "kind": "review_gate",
                    "actor": "human",
                    "condition": "check_passed",
                    "decision": {"options": ["accept", "reject", "request_changes"]},
                    "required": True,
                },
                {
                    "id": "apply_patch",
                    "title": "Apply accepted patch",
                    "kind": "apply_change",
                    "actor": "system",
                    "condition": "review_accepted",
                    "required": True,
                },
            ],
            "success_signals": [
                "imported_document_preserved",
                "analysis_note_created",
                "patch_created_when_target_provided",
                "patch_check_passes_before_accept",
            ],
        },
        {
            "id": "research-loop",
            "version": 1,
            "status": "active",
            "title": "Research Loop",
            "description": "Run a skill-driven research task, produce auditable outputs, and surface follow-up review items.",
            "inputs": {"required": ["objective"], "optional": ["accepted_knowledge", "active_skills"]},
            "default_agents": {"orchestrator": "agent_orchestrator", "reviewer": "agent_auditor"},
            "steps": [
                {"id": "plan", "title": "Plan task", "kind": "produce_artifact", "actor": "agent", "agent_ref": "agent_orchestrator", "required": True},
                {"id": "work", "title": "Execute research step", "kind": "agent_run", "actor": "agent", "agent_ref": "agent_orchestrator", "required": True},
                {"id": "review", "title": "Review outputs", "kind": "review_gate", "actor": "human", "required": False},
                {"id": "continue", "title": "Continue or close task", "kind": "decision", "actor": "human_or_agent", "required": False},
            ],
            "success_signals": ["run_created", "output_archived", "trace_available"],
        },
        {
            "id": "research-iteration",
            "version": 1,
            "status": "active",
            "title": "Research Iteration",
            "description": "Use DeepAgents to frame a topic, map evidence, propose experiment iterations, and extract reviewable physical prior candidates.",
            "inputs": {
                "required": ["objective"],
                "optional": ["accepted_knowledge", "imported_documents", "experiment_logs", "active_skills"],
            },
            "default_agents": {"orchestrator": "agent_orchestrator", "reviewer": "agent_auditor"},
            "steps": [
                {
                    "id": "frame_topic",
                    "title": "Frame topic and map evidence",
                    "kind": "produce_artifact",
                    "actor": "agent",
                    "agent_ref": "agent_orchestrator",
                    "skill_refs": ["topic.research", "document.evidence"],
                    "instructions": "Create topic-brief.md and evidence-map.md. Define the topic, scope, known facts, unknowns, hypotheses, evidence, assumptions, mechanisms, uncertainty, and falsification notes.",
                    "required": True,
                },
                {
                    "id": "iterate_and_extract",
                    "title": "Design experiment iteration and extract priors",
                    "kind": "produce_artifact",
                    "actor": "agent",
                    "agent_ref": "agent_orchestrator",
                    "skill_refs": ["experiment.iterate", "physics.prior.extract", "document.evidence"],
                    "instructions": "Create hypotheses.md, experiment-plan.md, iteration-log.md, physical-priors.md, and proposals.md. Propose the smallest useful next trial and extract prior candidates with statement, mechanism, evidence, boundary, counterexample, confidence, and next validation step.",
                    "required": True,
                },
                {
                    "id": "review",
                    "title": "Review prior candidates and proposals",
                    "kind": "review_gate",
                    "actor": "human",
                    "decision": {"options": ["accept", "request_changes", "continue"]},
                    "required": False,
                },
            ],
            "success_signals": [
                "topic_brief_created",
                "evidence_map_created",
                "experiment_plan_created",
                "physical_prior_candidates_created",
                "outputs_archived",
            ],
        },
        {
            "id": "analysis-loop",
            "version": 1,
            "status": "active",
            "title": "Analysis Loop",
            "description": "Analyze materials, map evidence, produce conclusions, and identify next checks.",
            "inputs": {"required": ["objective"], "optional": ["source_files", "accepted_knowledge", "prior_task_runs"]},
            "default_agents": {"orchestrator": "agent_orchestrator", "reviewer": "agent_auditor"},
            "steps": [
                {
                    "id": "analyze",
                    "title": "Analyze evidence and uncertainty",
                    "kind": "produce_artifact",
                    "actor": "agent",
                    "agent_ref": "agent_orchestrator",
                    "skill_refs": ["document.evidence", "research.review"],
                    "required_tools": ["filesystem.read", "filesystem.list"],
                    "expected_files": ["evidence-map.md", "research-note.md", "next-actions.md"],
                    "continue_from": ["prior_task_runs", "accepted_knowledge"],
                    "instructions": "Read the available material, separate evidence from inference, write an evidence map, concise analysis note, and next actions.",
                    "required": True,
                }
            ],
            "success_signals": ["evidence_map_created", "analysis_note_created", "next_actions_created"],
        },
        {
            "id": "experiment-loop",
            "version": 1,
            "status": "active",
            "title": "Experiment Loop",
            "description": "Read an experiment brief, run or prepare the smallest useful command, analyze outputs, and propose the next iteration.",
            "inputs": {"required": ["objective"], "optional": ["experiment_dir", "prior_task_runs", "accepted_knowledge"]},
            "default_agents": {"orchestrator": "agent_orchestrator", "reviewer": "agent_auditor"},
            "steps": [
                {
                    "id": "run_or_plan",
                    "title": "Run or plan experiment",
                    "kind": "agent_run",
                    "actor": "agent",
                    "agent_ref": "agent_orchestrator",
                    "skill_refs": ["experiment.iterate", "document.evidence"],
                    "required_tools": ["filesystem.read", "filesystem.write", "filesystem.list", "shell.run", "artifact.save"],
                    "expected_files": ["metrics.md", "notes.md", "next-actions.md"],
                    "expected_artifacts": ["shell_output"],
                    "continue_from": ["prior_task_runs", "latest_outputs"],
                    "instructions": "Inspect the experiment instructions, run the smallest safe command when available, preserve command output, summarize metrics and notes, and write next-actions.md.",
                    "required": True,
                }
            ],
            "success_signals": ["command_output_archived", "metrics_created", "next_actions_created"],
        },
        {
            "id": "improvement-loop",
            "version": 1,
            "status": "active",
            "title": "Improvement Loop",
            "description": "Inspect prior failure or weak output, make a narrow improvement, verify it, and summarize the delta.",
            "inputs": {"required": ["objective"], "optional": ["prior_task_runs", "target_files", "accepted_knowledge"]},
            "default_agents": {"orchestrator": "agent_orchestrator", "reviewer": "agent_auditor"},
            "steps": [
                {
                    "id": "improve",
                    "title": "Improve and verify",
                    "kind": "agent_run",
                    "actor": "agent",
                    "agent_ref": "agent_orchestrator",
                    "skill_refs": ["research.review"],
                    "required_tools": ["filesystem.read", "filesystem.write", "filesystem.list", "shell.run", "git.status"],
                    "expected_files": ["improvement-summary.md", "next-actions.md"],
                    "expected_artifacts": ["shell_output"],
                    "continue_from": ["prior_task_runs", "latest_outputs"],
                    "instructions": "Use prior outputs to identify one narrow improvement, make or propose it, run a verification command when possible, and summarize the delta and next action.",
                    "required": True,
                }
            ],
            "success_signals": ["improvement_summary_created", "verification_output_archived"],
        },
        {
            "id": "reflection-loop",
            "version": 1,
            "status": "active",
            "title": "Reflection Loop",
            "description": "Reflect on workflow, skills, and document organization, then propose reviewable improvements.",
            "inputs": {"required": ["objective"], "optional": ["recent_runs", "workflow_specs", "skills"]},
            "default_agents": {"orchestrator": "agent_orchestrator", "reviewer": "agent_auditor"},
            "steps": [
                {"id": "inspect", "title": "Inspect current process", "kind": "agent_run", "actor": "agent", "agent_ref": "agent_orchestrator", "required": True},
                {"id": "propose", "title": "Propose process changes", "kind": "produce_contribution", "actor": "agent", "agent_ref": "agent_orchestrator", "required": False},
                {"id": "review", "title": "Review process proposals", "kind": "review_gate", "actor": "human", "required": True},
            ],
            "success_signals": ["reflection_archived", "proposals_reviewable"],
        }
    ]


def write_default_workflows(root):
    base = require_workspace(root)
    workflow_dir = base / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    for workflow in default_workflows():
        path = workflow_dir / f"{workflow['id']}.yaml"
        if not path.exists():
            write_yaml(path, workflow)


def list_workflows(root):
    base = require_workspace(root)
    workflows = []
    for path in sorted((base / "workflows").glob("*.yaml")):
        workflows.append(read_yaml(path, {}))
    return workflows


def load_workflow(root, workflow_id):
    base = require_workspace(root)
    workflow = read_yaml(base / "workflows" / f"{workflow_id}.yaml", None)
    if not workflow:
        raise RuntimeError(f"Workflow not found: {workflow_id}")
    return workflow


def workflow_prompt(workflow):
    lines = [
        f"# {workflow.get('title', workflow.get('id', 'Workflow'))} Workflow",
        "",
        f"- Workflow ID: {workflow.get('id')}",
        f"- Version: {workflow.get('version')}",
        "",
        workflow.get("description", ""),
        "",
        "## Steps",
        "",
    ]
    for step in workflow.get("steps", []):
        lines.extend(
            [
                f"### {step.get('id')} - {step.get('title')}",
                "",
                f"- Kind: {step.get('kind')}",
                f"- Actor: {step.get('actor')}",
            ]
        )
        if step.get("skill_refs"):
            lines.append(f"- Skill refs: {', '.join(step.get('skill_refs', []))}")
        if step.get("condition"):
            lines.append(f"- Condition: {step.get('condition')}")
        if step.get("instructions"):
            lines.extend(["", step["instructions"]])
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def workflow_steps(workflow):
    return list(workflow.get("steps", []))


def workflow_round_size(workflow):
    size = 0
    for step in workflow_steps(workflow):
        if step.get("actor") == "human":
            break
        size += 1
    return max(size, 1)


def initial_workflow_state(workflow):
    steps = workflow_steps(workflow)
    first = _next_executable_step(steps, start_index=0)
    current = first["id"] if first else None
    return {
        "workflow_id": workflow.get("id"),
        "current_step_id": current,
        "completed_step_ids": [],
        "iteration": 0,
    }


def workflow_step_by_id(workflow, step_id):
    for step in workflow_steps(workflow):
        if step.get("id") == step_id:
            return step
    return None


def current_workflow_step(workflow, state):
    step_id = (state or {}).get("current_step_id")
    if not step_id:
        steps = workflow_steps(workflow)
        return steps[0] if steps else None
    return workflow_step_by_id(workflow, step_id)


def advance_workflow_state(workflow, state, completed_step_id):
    state = dict(state or initial_workflow_state(workflow))
    completed = list(state.get("completed_step_ids", []))
    completed.append(completed_step_id)
    steps = workflow_steps(workflow)
    step_ids = [step.get("id") for step in steps]
    try:
        index = step_ids.index(completed_step_id)
    except ValueError:
        index = -1
    if steps:
        next_step = _next_executable_step(steps, start_index=index + 1)
        state["current_step_id"] = next_step.get("id") if next_step else None
    else:
        state["current_step_id"] = None
    state["completed_step_ids"] = completed
    state["iteration"] = int(state.get("iteration") or 0) + 1
    return state


def _next_executable_step(steps, start_index=0):
    if not steps:
        return None
    for offset in range(len(steps)):
        step = steps[(start_index + offset) % len(steps)]
        if step.get("actor") == "human":
            continue
        return step
    return None


def workflow_step_instruction(workflow, task, step):
    title = step.get("title") or step.get("id")
    kind = step.get("kind", "-")
    actor = step.get("actor", "-")
    lines = [
        task.get("objective", ""),
        "",
        f"Task objective: {task.get('objective', '')}",
        f"Workflow: {workflow.get('id')}",
        f"Workflow step: {step.get('id')} - {title}",
        f"Step kind: {kind}",
        f"Actor: {actor}",
        "",
        "Execute only this workflow step. Use accepted knowledge, active skills, prior task runs, and available tools.",
        "",
        "For research or reflection steps, produce durable Markdown working files when possible. Prefer these filenames when they fit the step:",
        "- topic-brief.md for topic scope, known facts, unknowns, and evidence needs",
        "- evidence-map.md for claims, evidence, assumptions, mechanisms, uncertainty, and falsification notes",
        "- hypotheses.md for ranked hypotheses and expected observations",
        "- experiment-plan.md for the next minimal experiment, variables, controls, measurements, and stop criteria",
        "- iteration-log.md for the trial record template and interpretation notes",
        "- physical-priors.md for reviewable physical prior candidates with evidence, boundaries, counterexamples, confidence, and next validation",
        "- research-note.md for findings, synthesis, assumptions, and uncertainty",
        "- next-actions.md for concrete follow-up steps and open questions",
        "- proposals.md for proposed knowledge, skill, or workflow changes that need review",
    ]
    if step.get("skill_refs"):
        lines.extend(["", f"Step skill refs: {', '.join(step.get('skill_refs', []))}"])
    if step.get("required_tools"):
        lines.extend(["", f"Required tools: {', '.join(step.get('required_tools', []))}"])
    if step.get("expected_files"):
        lines.extend(["", "Expected files:", *[f"- {path}" for path in step.get("expected_files", [])]])
    if step.get("expected_artifacts"):
        lines.extend(["", "Expected artifacts:", *[f"- {artifact_type}" for artifact_type in step.get("expected_artifacts", [])]])
    if step.get("continue_from"):
        lines.extend(["", f"Continue from: {', '.join(step.get('continue_from', []))}"])
    if step.get("instructions"):
        lines.extend(["", "Step instructions:", step["instructions"]])
    lines.extend(
        [
            "",
            "Output should be concrete and auditable. If durable knowledge, skill, or workflow changes are needed, produce proposals rather than silently modifying accepted state.",
        ]
    )
    return "\n".join(lines).strip()
