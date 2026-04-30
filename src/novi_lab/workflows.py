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
