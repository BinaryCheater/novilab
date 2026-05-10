import shutil
import subprocess
from urllib.error import URLError
from urllib.request import Request, urlopen
from pathlib import Path

from .ids import new_id
from .store import content_hash, read_yaml, require_workspace, utc_now, write_yaml


def builtin_tools():
    return [
        {
            "id": "search_stub.query",
            "description": "Deterministic local search stub used to validate tool records.",
            "risk": "read_only",
            "policy": "allowed",
            "input_schema": {"query": "string"},
            "output_artifacts": ["search_result_stub"],
            "expose_to": ["agent_orchestrator"],
        },
        {
            "id": "filesystem.read",
            "description": "Read a UTF-8 text file inside the Novi workspace.",
            "risk": "read_only",
            "policy": "allowed",
            "input_schema": {"path": "string"},
            "output_artifacts": ["file_text"],
            "expose_to": ["agent_orchestrator", "agent_auditor"],
        },
        {
            "id": "filesystem.write",
            "description": "Write a UTF-8 text file inside the Novi workspace.",
            "risk": "write_local",
            "policy": "allowed",
            "input_schema": {"path": "string", "content": "string"},
            "output_artifacts": ["file_written"],
            "expose_to": ["agent_orchestrator"],
        },
        {
            "id": "filesystem.list",
            "description": "List files and directories inside the Novi workspace.",
            "risk": "read_only",
            "policy": "allowed",
            "input_schema": {"path": "string"},
            "output_artifacts": ["directory_listing"],
            "expose_to": ["agent_orchestrator", "agent_auditor"],
        },
        {
            "id": "shell.run",
            "description": "Run a shell command from the Novi workspace and capture stdout/stderr.",
            "risk": "execute_local",
            "policy": "allowed",
            "input_schema": {"command": "string", "cwd": "string", "timeout": "integer", "allow_failure": "boolean"},
            "output_artifacts": ["shell_output"],
            "expose_to": ["agent_orchestrator"],
        },
        {
            "id": "web.fetch",
            "description": "Fetch a URL and capture the response body as text.",
            "risk": "network",
            "policy": "allowed",
            "input_schema": {"url": "string", "timeout": "integer"},
            "output_artifacts": ["web_fetch"],
            "expose_to": ["agent_orchestrator"],
        },
        {
            "id": "artifact.save",
            "description": "Copy a workspace file into the Novi artifact store.",
            "risk": "write_local",
            "policy": "allowed",
            "input_schema": {"path": "string", "artifact_type": "string"},
            "output_artifacts": ["saved_artifact"],
            "expose_to": ["agent_orchestrator"],
        },
        {
            "id": "git.status",
            "description": "Read git status for the Novi workspace.",
            "risk": "read_only",
            "policy": "allowed",
            "input_schema": {},
            "output_artifacts": ["git_status"],
            "expose_to": ["agent_orchestrator", "agent_auditor"],
        }
    ]


def list_tools(root):
    tools = {tool["id"]: dict(tool, source="builtin") for tool in builtin_tools()}
    project_dir = require_workspace(root) / "tools"
    for path in sorted(project_dir.glob("*.yaml")):
        tool = read_yaml(path, {})
        if tool.get("id"):
            tools[tool["id"]] = dict(tool, source="project")
    return [tools[tool_id] for tool_id in sorted(tools)]


def load_tool(root, tool_id):
    for tool in list_tools(root):
        if tool["id"] == tool_id:
            return tool
    raise RuntimeError(f"Tool not found: {tool_id}")


def _tool_path(base, tool_id):
    safe_id = tool_id.replace("/", "_").replace(".", "_")
    return Path(base) / "tools" / f"{safe_id}.yaml"


def expose_tool_to_agent(root, tool_id, agent_id):
    base = require_workspace(root)
    tool = dict(load_tool(root, tool_id))
    tool.pop("source", None)
    exposed = list(tool.get("expose_to", []))
    if agent_id not in exposed:
        exposed.append(agent_id)
    tool["expose_to"] = exposed
    write_yaml(_tool_path(base, tool_id), tool)
    return tool


def evaluate_policy(tool):
    if tool.get("risk") == "read_only":
        return "allowed"
    if tool.get("policy") == "allowed":
        return "allowed"
    return "blocked"


def _workspace_path(root, raw_path, *, must_exist=False):
    workspace = Path(root).resolve()
    raw_path = raw_path or "."
    path = Path(raw_path)
    if path.is_absolute():
        requested = path.resolve()
        if not str(requested).startswith(str(workspace)):
            requested = (workspace / raw_path.lstrip("/")).resolve()
    else:
        requested = (workspace / raw_path).resolve()
    if not str(requested).startswith(str(workspace)):
        raise RuntimeError("path_outside_workspace")
    if must_exist and not requested.exists():
        raise FileNotFoundError(raw_path)
    return requested


def _truncate(text, limit=4000):
    text = text or ""
    return text[:limit], len(text) > limit


def _truthy(value):
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _run_artifact_dir(root, run_id):
    if not run_id or run_id == "manual":
        path = require_workspace(root) / "artifacts"
    else:
        path = require_workspace(root) / "runs" / run_id / "artifacts"
        if not path.exists():
            path = require_workspace(root) / "artifacts"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _save_artifact_record(root, run_id, artifact_type, source_path, produced_by=None, source_path_label=None):
    source_path = Path(source_path)
    artifact_id = new_id("art")
    artifact_dir = _run_artifact_dir(root, run_id)
    if artifact_dir.name == "artifacts" and artifact_dir.parent.name == ".novi":
        target_dir = artifact_dir / "saved"
        record_path = artifact_dir / f"{artifact_id}.yaml"
    else:
        target_dir = artifact_dir
        record_path = artifact_dir / f"{artifact_id}.yaml"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{artifact_id}-{source_path.name}"
    shutil.copyfile(source_path, target_path)
    artifact = {
        "id": artifact_id,
        "type": artifact_type,
        "path": str(target_path),
        "run_id": None if run_id == "manual" else run_id,
        "created_at": utc_now(),
        "produced_by": produced_by,
        "hash": content_hash(target_path),
        "hash_algorithm": "sha256",
        "mime_type": "text/plain",
        "size_bytes": target_path.stat().st_size,
        "source_path": source_path_label or str(source_path),
    }
    write_yaml(record_path, artifact)
    return artifact


def _write_text_artifact(root, run_id, artifact_type, filename, content, produced_by=None):
    artifact_dir = _run_artifact_dir(root, run_id)
    artifact_id = new_id("art")
    path = artifact_dir / f"{artifact_id}-{filename}"
    path.write_text(content, encoding="utf-8")
    artifact = {
        "id": artifact_id,
        "type": artifact_type,
        "path": str(path),
        "run_id": None if run_id == "manual" else run_id,
        "created_at": utc_now(),
        "produced_by": produced_by,
        "hash": content_hash(path),
        "hash_algorithm": "sha256",
        "mime_type": "text/plain",
        "size_bytes": path.stat().st_size,
    }
    write_yaml(artifact_dir / f"{artifact_id}.yaml", artifact)
    return artifact


def tool_exposed_to_agent(tool, agent_id):
    exposed = tool.get("expose_to", [])
    return "*" in exposed or agent_id in exposed


def available_tool_ids(root, agent):
    available = []
    unavailable = []
    for tool_id in agent.get("tool_scope", []):
        tool = load_tool(root, tool_id)
        if tool_exposed_to_agent(tool, agent.get("agent_id")):
            available.append(tool_id)
        else:
            unavailable.append({"tool_id": tool_id, "reason": "tool_not_exposed_to_agent"})
    return available, unavailable


def execute_tool(root, run_id, agent, tool_id, args, source="manual"):
    tool = load_tool(root, tool_id)
    now = utc_now()
    call = {
        "id": new_id("tc"),
        "run_id": run_id,
        "tool_id": tool_id,
        "agent_id": agent["agent_id"],
        "status": "running",
        "created_at": now,
        "updated_at": now,
        "args_ref": args,
        "result_ref": {},
        "risk": tool.get("risk", "unknown"),
        "policy_result": "unknown",
        "artifact_ids": [],
        "executor": "novi_tool_runtime",
        "source": source,
    }

    if tool_id not in agent.get("tool_scope", []):
        call["status"] = "blocked"
        call["policy_result"] = "blocked"
        call["block_reason"] = "tool_not_in_agent_scope"
        call["updated_at"] = utc_now()
        return call

    if not tool_exposed_to_agent(tool, agent.get("agent_id")):
        call["status"] = "blocked"
        call["policy_result"] = "blocked"
        call["block_reason"] = "tool_not_exposed_to_agent"
        call["updated_at"] = utc_now()
        return call

    policy_result = evaluate_policy(tool)
    if policy_result != "allowed":
        call["status"] = "blocked"
        call["policy_result"] = policy_result
        call["block_reason"] = "policy_not_allowed"
        call["updated_at"] = utc_now()
        return call

    if tool_id == "search_stub.query":
        call["status"] = "success"
        call["policy_result"] = "allowed"
        call["result_ref"] = {
            "source": "deterministic_stub",
            "summary": f"No network search was performed for: {args.get('query', '')}",
        }
        call["updated_at"] = utc_now()
        return call

    if tool_id == "filesystem.read":
        try:
            requested = _workspace_path(root, args.get("path", ""), must_exist=True)
        except RuntimeError:
            call["status"] = "blocked"
            call["policy_result"] = "blocked"
            call["block_reason"] = "path_outside_workspace"
            call["updated_at"] = utc_now()
            return call
        except FileNotFoundError:
            call["status"] = "error"
            call["policy_result"] = "allowed"
            call["error"] = f"File not found: {args.get('path', '')}"
            call["updated_at"] = utc_now()
            return call
        if not requested.is_file():
            call["status"] = "error"
            call["policy_result"] = "allowed"
            call["error"] = f"Not a file: {args.get('path', '')}"
            call["updated_at"] = utc_now()
            return call
        content = requested.read_text(encoding="utf-8")
        call["status"] = "success"
        call["policy_result"] = "allowed"
        content, truncated = _truncate(content)
        call["result_ref"] = {
            "path": str(requested.relative_to(Path(root).resolve())),
            "content": content,
            "truncated": truncated,
        }
        call["updated_at"] = utc_now()
        return call

    if tool_id == "filesystem.write":
        try:
            requested = _workspace_path(root, args.get("path", ""))
        except RuntimeError:
            call["status"] = "blocked"
            call["policy_result"] = "blocked"
            call["block_reason"] = "path_outside_workspace"
            call["updated_at"] = utc_now()
            return call
        requested.parent.mkdir(parents=True, exist_ok=True)
        requested.write_text(args.get("content", ""), encoding="utf-8")
        call["status"] = "success"
        call["policy_result"] = "allowed"
        call["result_ref"] = {
            "path": str(requested.relative_to(Path(root).resolve())),
            "bytes_written": requested.stat().st_size,
        }
        call["updated_at"] = utc_now()
        return call

    if tool_id == "filesystem.list":
        try:
            requested = _workspace_path(root, args.get("path", "."), must_exist=True)
        except RuntimeError:
            call["status"] = "blocked"
            call["policy_result"] = "blocked"
            call["block_reason"] = "path_outside_workspace"
            call["updated_at"] = utc_now()
            return call
        except FileNotFoundError:
            call["status"] = "error"
            call["policy_result"] = "allowed"
            call["error"] = f"Path not found: {args.get('path', '')}"
            call["updated_at"] = utc_now()
            return call
        if requested.is_file():
            entries = [requested.name]
        else:
            entries = sorted(path.name + ("/" if path.is_dir() else "") for path in requested.iterdir())
        call["status"] = "success"
        call["policy_result"] = "allowed"
        call["result_ref"] = {
            "path": str(requested.relative_to(Path(root).resolve())),
            "entries": entries[:200],
            "truncated": len(entries) > 200,
        }
        call["updated_at"] = utc_now()
        return call

    if tool_id == "shell.run":
        try:
            cwd = _workspace_path(root, args.get("cwd", "."), must_exist=True)
        except RuntimeError:
            call["status"] = "blocked"
            call["policy_result"] = "blocked"
            call["block_reason"] = "cwd_outside_workspace"
            call["updated_at"] = utc_now()
            return call
        command = args.get("command", "")
        timeout = int(args.get("timeout") or 60)
        allow_failure = _truthy(args.get("allow_failure", False))
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                shell=True,
                text=True,
                capture_output=True,
                timeout=timeout,
            )
            artifact = _write_text_artifact(
                root,
                run_id,
                "shell_output",
                "shell-output.txt",
                f"$ {command}\n\n# stdout\n{result.stdout}\n\n# stderr\n{result.stderr}\n",
                produced_by=agent.get("agent_id"),
            )
            stdout, stdout_truncated = _truncate(result.stdout)
            stderr, stderr_truncated = _truncate(result.stderr)
            call["status"] = "success" if result.returncode == 0 or allow_failure else "error"
            call["policy_result"] = "allowed"
            call["artifact_ids"] = [artifact["id"]]
            call["result_ref"] = {
                "command": command,
                "cwd": str(cwd.relative_to(Path(root).resolve())),
                "returncode": result.returncode,
                "allow_failure": allow_failure,
                "stdout": stdout,
                "stderr": stderr,
                "stdout_truncated": stdout_truncated,
                "stderr_truncated": stderr_truncated,
                "artifact_id": artifact["id"],
            }
        except subprocess.TimeoutExpired:
            call["status"] = "error"
            call["policy_result"] = "allowed"
            call["error"] = f"Command timed out after {timeout}s"
        call["updated_at"] = utc_now()
        return call

    if tool_id == "web.fetch":
        url = args.get("url", "")
        timeout = int(args.get("timeout") or 30)
        if not url.startswith(("http://", "https://")):
            call["status"] = "blocked"
            call["policy_result"] = "blocked"
            call["block_reason"] = "unsupported_url_scheme"
            call["updated_at"] = utc_now()
            return call
        try:
            request = Request(url, headers={"User-Agent": "novi-lab/0.1"})
            with urlopen(request, timeout=timeout) as response:
                body = response.read(1_000_000)
                text = body.decode(response.headers.get_content_charset() or "utf-8", errors="replace")
            artifact = _write_text_artifact(root, run_id, "web_fetch", "web-fetch.txt", text, produced_by=agent.get("agent_id"))
            content, truncated = _truncate(text)
            call["status"] = "success"
            call["policy_result"] = "allowed"
            call["artifact_ids"] = [artifact["id"]]
            call["result_ref"] = {
                "url": url,
                "content": content,
                "truncated": truncated or len(body) >= 1_000_000,
                "artifact_id": artifact["id"],
            }
        except URLError as exc:
            call["status"] = "error"
            call["policy_result"] = "allowed"
            call["error"] = str(exc)
        call["updated_at"] = utc_now()
        return call

    if tool_id == "artifact.save":
        try:
            requested = _workspace_path(root, args.get("path", ""), must_exist=True)
        except RuntimeError:
            call["status"] = "blocked"
            call["policy_result"] = "blocked"
            call["block_reason"] = "path_outside_workspace"
            call["updated_at"] = utc_now()
            return call
        except FileNotFoundError:
            call["status"] = "error"
            call["policy_result"] = "allowed"
            call["error"] = f"File not found: {args.get('path', '')}"
            call["updated_at"] = utc_now()
            return call
        if not requested.is_file():
            call["status"] = "error"
            call["policy_result"] = "allowed"
            call["error"] = f"Not a file: {args.get('path', '')}"
            call["updated_at"] = utc_now()
            return call
        artifact = _save_artifact_record(
            root,
            run_id,
            args.get("artifact_type") or "saved_file",
            requested,
            produced_by=agent.get("agent_id"),
            source_path_label=str(requested.relative_to(Path(root).resolve())),
        )
        call["status"] = "success"
        call["policy_result"] = "allowed"
        call["artifact_ids"] = [artifact["id"]]
        call["result_ref"] = {
            "artifact_id": artifact["id"],
            "path": artifact["path"],
            "source_path": artifact["source_path"],
        }
        call["updated_at"] = utc_now()
        return call

    if tool_id == "git.status":
        result = subprocess.run(
            ["git", "status", "--short", "--branch"],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=10,
        )
        call["policy_result"] = "allowed"
        call["status"] = "success" if result.returncode == 0 else "error"
        call["result_ref"] = {"stdout": result.stdout, "stderr": result.stderr}
        call["updated_at"] = utc_now()
        return call

    call["status"] = "blocked"
    call["policy_result"] = "blocked"
    call["block_reason"] = "executor_not_implemented"
    call["updated_at"] = utc_now()
    return call
