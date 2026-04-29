import json
from pathlib import Path

from .ids import new_id
from .model_providers import resolve_deepagents_model
from .store import append_jsonl, content_hash, utc_now, write_yaml
from .tools import execute_tool


def require_deepagents_kernel():
    try:
        import deepagents
    except ImportError as exc:
        raise RuntimeError(
            "DeepAgents kernel requires optional dependency. "
            "Install with `uv sync --extra deepagents` and run on Python 3.11+."
        ) from exc
    return deepagents


def validate_kernel(kernel):
    if kernel == "simple":
        return
    if kernel == "deepagents":
        require_deepagents_kernel()
        return
    raise RuntimeError(f"Unknown kernel: {kernel}")


def _tool_function_name(tool_id):
    return tool_id.replace(".", "_").replace("-", "_")


def _tool_wrapper(root, run_dir, run_id, participant, tool_id):
    def record_call(kwargs):
        call = execute_tool(root, run_id, participant, tool_id, kwargs)
        append_jsonl(Path(run_dir) / "tool_calls.jsonl", call)
        return json.dumps(
            {
                "tool_id": tool_id,
                "status": call.get("status"),
                "policy_result": call.get("policy_result"),
                "block_reason": call.get("block_reason"),
                "result": call.get("result_ref", {}),
                "error": call.get("error"),
            },
            sort_keys=True,
        )

    if tool_id == "search_stub.query":
        def search_stub_query(query: str = "") -> str:
            """Run Novi's deterministic search stub through ToolRuntime."""
            return record_call({"query": query})

        return search_stub_query

    if tool_id == "filesystem.read":
        def filesystem_read(path: str = "") -> str:
            """Read a UTF-8 text file inside the Novi workspace through ToolRuntime."""
            return record_call({"path": path})

        return filesystem_read

    if tool_id == "git.status":
        def git_status() -> str:
            """Read git status for the Novi workspace through ToolRuntime."""
            return record_call({})

        return git_status

    def call_tool(**kwargs):
        return record_call(kwargs)

    call_tool.__name__ = _tool_function_name(tool_id)
    call_tool.__doc__ = f"Novi-wrapped tool `{tool_id}`. All calls pass through Novi ToolRuntime and policy."
    return call_tool


def _extract_response_text(result):
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        messages = result.get("messages")
        if messages:
            last = messages[-1]
            if isinstance(last, dict):
                return str(last.get("content", last))
            return str(getattr(last, "content", last))
        if "output" in result:
            return str(result["output"])
    return str(result)


def _file_content(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return str(value.get("content", value.get("data", value)))
    return str(getattr(value, "content", value))


def _export_deepagents_files(run_dir, run_record, result):
    if not isinstance(result, dict) or not result.get("files"):
        return []
    exported = []
    export_dir = Path(run_dir) / "deepagents_files"
    export_dir.mkdir(parents=True, exist_ok=True)
    for raw_path, value in sorted(result["files"].items()):
        relative = str(raw_path).lstrip("/") or "unnamed"
        if ".." in Path(relative).parts:
            relative = relative.replace("..", "__")
        path = export_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_file_content(value), encoding="utf-8")
        artifact_id = new_id("art")
        artifact = {
            "id": artifact_id,
            "type": "deepagents_file",
            "path": str(path),
            "run_id": run_record["id"],
            "created_at": utc_now(),
            "produced_by": run_record.get("participants", [{}])[0].get("agent_id"),
            "hash": content_hash(path),
            "hash_algorithm": "sha256",
            "mime_type": "text/markdown",
            "size_bytes": path.stat().st_size,
            "source_path": str(raw_path),
        }
        write_yaml(Path(run_dir) / "artifacts" / f"{artifact_id}.yaml", artifact)
        run_record.setdefault("artifact_ids", []).append(artifact_id)
        exported.append({"artifact_id": artifact_id, "path": str(path.relative_to(run_dir))})
    run_record["deepagents_files"] = exported
    return exported


def run_deepagents_kernel(root, run_dir, run_record, prompt_path):
    deepagents = require_deepagents_kernel()
    create_deep_agent = getattr(deepagents, "create_deep_agent")
    participant = run_record.get("participants", [{}])[0]
    tool_scope = participant.get("tool_scope", [])
    tools = [_tool_wrapper(root, run_dir, run_record["id"], participant, tool_id) for tool_id in tool_scope]
    prompt_text = Path(prompt_path).read_text(encoding="utf-8")
    started_at = utc_now()
    response_path = Path(run_dir) / "response.md"
    model, model_record = resolve_deepagents_model(participant)
    try:
        agent = create_deep_agent(
            model=model,
            tools=tools,
            system_prompt=prompt_text,
            name=participant.get("agent_id"),
        )
        result = agent.invoke({"messages": [{"role": "user", "content": run_record["objective"]}]})
        response_text = _extract_response_text(result)
        exported_files = _export_deepagents_files(run_dir, run_record, result)
        response_path.write_text(f"# Model Response\n\n{response_text}\n", encoding="utf-8")
        append_jsonl(
            Path(run_dir) / "model_calls.jsonl",
            {
                "run_id": run_record["id"],
                "agent_id": participant.get("agent_id"),
                **model_record,
                "kernel": "deepagents",
                "status": "success",
                "started_at": started_at,
                "completed_at": utc_now(),
                "prompt_path": str(prompt_path),
                "response_path": str(response_path),
                "exported_files": exported_files,
            },
        )
    except Exception as exc:
        response_path.write_text(f"# Model Response\n\nDeepAgents execution failed: {exc}\n", encoding="utf-8")
        append_jsonl(
            Path(run_dir) / "model_calls.jsonl",
            {
                "run_id": run_record["id"],
                "agent_id": participant.get("agent_id"),
                **model_record,
                "kernel": "deepagents",
                "status": "error",
                "started_at": started_at,
                "completed_at": utc_now(),
                "prompt_path": str(prompt_path),
                "response_path": str(response_path),
                "error": str(exc),
            },
        )
        raise RuntimeError(f"DeepAgents execution failed: {exc}") from exc
