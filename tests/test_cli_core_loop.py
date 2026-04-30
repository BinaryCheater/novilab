import json
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


def test_agent_profile_v2_records_authority_and_binding_hints(tmp_path):
    run_cli(tmp_path, "init")

    result = run_cli(tmp_path, "agent", "show", "agent_orchestrator")

    assert result.returncode == 0, result.stderr
    assert "Authority level: collaborator" in result.stdout
    assert "Interface mode: cli" in result.stdout
    assert "Prompt refs:" in result.stdout
    assert "research.review" in result.stdout
    assert "Kernel binding hints:" in result.stdout
    assert "deepagents_subagent" in result.stdout


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


def test_tool_specs_show_expose_to_routing_metadata(tmp_path):
    run_cli(tmp_path, "init")

    result = run_cli(tmp_path, "tool", "show", "search_stub.query")

    assert result.returncode == 0, result.stderr
    assert "Expose to:" in result.stdout
    assert "agent_orchestrator" in result.stdout


def test_tool_expose_updates_routing_metadata(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "agent", "create", "agent_reader", "--role", "reader")

    expose_result = run_cli(tmp_path, "tool", "expose", "filesystem.read", "agent_reader")
    show_result = run_cli(tmp_path, "tool", "show", "filesystem.read")

    assert expose_result.returncode == 0, expose_result.stderr
    assert "Exposed filesystem.read to agent_reader" in expose_result.stdout
    assert show_result.returncode == 0, show_result.stderr
    assert "agent_reader" in show_result.stdout


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
    run_cli(tmp_path, "tool", "expose", "filesystem.read", "agent_reader")
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
    root_relative = run_cli(
        tmp_path,
        "tool",
        "call",
        "filesystem.read",
        "--agent",
        "agent_reader",
        "--arg",
        "path=/note.md",
    )

    assert blocked.returncode == 0, blocked.stderr
    assert "blocked" in blocked.stdout
    assert "tool_not_in_agent_scope" in blocked.stdout
    assert allowed.returncode == 0, allowed.stderr
    assert "success" in allowed.stdout
    assert "local evidence" in allowed.stdout
    assert root_relative.returncode == 0, root_relative.stderr
    assert "success" in root_relative.stdout
    assert "local evidence" in root_relative.stdout


def test_tool_call_requires_agent_scope_and_exposure(tmp_path):
    run_cli(tmp_path, "init")
    (tmp_path / "note.md").write_text("local evidence", encoding="utf-8")
    run_cli(tmp_path, "agent", "create", "agent_reader", "--role", "reader")
    run_cli(tmp_path, "agent", "grant-tool", "agent_reader", "filesystem.read")

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

    assert blocked.returncode == 0, blocked.stderr
    assert "blocked" in blocked.stdout
    assert "tool_not_exposed_to_agent" in blocked.stdout


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
    assert "agent_model_profile: deterministic-local" in request_text
    assert "model_provider: deepagents_default" in request_text
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


def test_deepagents_kernel_without_api_is_actionable(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "deepagents run")

    result = run_cli(tmp_path, "run", "start", "research", "try deepagents", "--kernel", "deepagents")

    assert result.returncode == 1
    assert (
        "DeepAgents kernel requires optional dependency" in result.stderr
        or "DeepAgents execution failed" in result.stderr
    )


def test_deepagents_kernel_invokes_adapter_and_archives_response(tmp_path):
    (tmp_path / "deepagents.py").write_text(
        "\n".join(
            [
                "class FakeMessage:",
                "    def __init__(self, content):",
                "        self.content = content",
                "",
                "class FakeAgent:",
                "    def __init__(self, model, tools, system_prompt, name=None, **kwargs):",
                "        self.model = model",
                "        self.tools = tools",
                "        self.system_prompt = system_prompt",
                "        self.name = name",
                "",
                "    def invoke(self, payload):",
                "        tool_result = self.tools[0](query='adapter smoke')",
                "        return {",
                "            'messages': [FakeMessage('deepagents response\\n' + tool_result)],",
                "            'files': {'/notes.md': {'content': 'deepagents working file'}}",
                "        }",
                "",
                "def create_deep_agent(model, tools=None, system_prompt=None, name=None, **kwargs):",
                "    return FakeAgent(model, tools or [], system_prompt, name=name, **kwargs)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "deepagents adapter run")

    result = run_cli(tmp_path, "run", "start", "research", "invoke adapter", "--kernel", "deepagents")

    assert result.returncode == 0, result.stderr
    assert "Response:" in result.stdout
    assert "deepagents response" in result.stdout
    run_id = parse_id(result.stdout, "run_")
    run_dir = tmp_path / ".novi" / "runs" / run_id
    response_text = (run_dir / "response.md").read_text()
    model_calls = (run_dir / "model_calls.jsonl").read_text()
    tool_calls = (run_dir / "tool_calls.jsonl").read_text()
    deepagents_messages = (run_dir / "deepagents_messages.jsonl").read_text()
    exported_file = run_dir / "deepagents_files" / "notes.md"

    assert "deepagents response" in response_text
    assert exported_file.read_text() == "deepagents working file"
    assert "deepagents_files/notes.md" in (run_dir / "run.yaml").read_text()
    assert '"content": "deepagents response' in deepagents_messages
    assert '"status": "success"' in model_calls
    assert '"kernel": "deepagents"' in model_calls
    assert '"tool_id": "search_stub.query"' in tool_calls
    assert "adapter smoke" in tool_calls
    assert '"source": "runner_preflight"' in tool_calls
    assert '"source": "deepagents_model"' in tool_calls

    output_result = run_cli(tmp_path, "run", "output", "latest")
    trace_result = run_cli(tmp_path, "run", "trace", "latest")

    assert output_result.returncode == 0, output_result.stderr
    assert "deepagents response" in output_result.stdout
    assert trace_result.returncode == 0, trace_result.stderr
    assert "Model calls:" in trace_result.stdout
    assert "DeepAgents messages:" in trace_result.stdout
    assert "deepagents_model" in trace_result.stdout


def test_doctor_model_reports_provider_without_secrets(tmp_path, monkeypatch):
    monkeypatch.setenv("NOVI_MODEL_PROVIDER", "openai_chat")
    monkeypatch.setenv("NOVI_MODEL", "Pro/zai-org/GLM-4.7")
    monkeypatch.setenv("NOVI_API_BASE", "https://api.siliconflow.cn/v1")
    monkeypatch.setenv("NOVI_API_KEY", "secret-test-key")
    run_cli(tmp_path, "init")

    result = run_cli(tmp_path, "doctor", "model")

    assert result.returncode == 0, result.stderr
    assert "Provider: openai_chat" in result.stdout
    assert "Model: Pro/zai-org/GLM-4.7" in result.stdout
    assert "Base URL: https://api.siliconflow.cn/v1" in result.stdout
    assert "API key: set" in result.stdout
    assert "secret-test-key" not in result.stdout


def test_configure_model_writes_project_config_without_printing_secret(tmp_path):
    run_cli(tmp_path, "init")

    result = run_cli(
        tmp_path,
        "configure",
        "model",
        "siliconflow",
        "--model",
        "Pro/zai-org/GLM-4.7",
        "--api-key",
        "secret-config-key",
    )
    doctor = run_cli(tmp_path, "doctor", "model")
    config_text = (tmp_path / ".novi" / "novi.yaml").read_text()

    assert result.returncode == 0, result.stderr
    assert "Configured model provider: openai_chat" in result.stdout
    assert "secret-config-key" not in result.stdout
    assert "provider: openai_chat" in config_text
    assert "model: Pro/zai-org/GLM-4.7" in config_text
    assert "base_url: https://api.siliconflow.cn/v1" in config_text
    assert "api_key: secret-config-key" in config_text
    assert doctor.returncode == 0, doctor.stderr
    assert "Provider: openai_chat" in doctor.stdout
    assert "Model: Pro/zai-org/GLM-4.7" in doctor.stdout
    assert "Base URL: https://api.siliconflow.cn/v1" in doctor.stdout
    assert "API key: set" in doctor.stdout
    assert "secret-config-key" not in doctor.stdout


def test_ask_records_messages_and_includes_recent_context(tmp_path):
    (tmp_path / "deepagents.py").write_text(
        "\n".join(
            [
                "import json",
                "",
                "class FakeMessage:",
                "    def __init__(self, content):",
                "        self.content = content",
                "",
                "class FakeAgent:",
                "    def __init__(self, model, tools, system_prompt, name=None, **kwargs):",
                "        self.system_prompt = system_prompt",
                "",
                "    def invoke(self, payload):",
                "        with open('captured_payloads.jsonl', 'a', encoding='utf-8') as handle:",
                "            handle.write(json.dumps({'system_prompt': self.system_prompt, 'messages': payload['messages']}, sort_keys=True) + '\\n')",
                "        user = payload['messages'][-1]['content']",
                "        marker = any(message.get('content') == 'first question' for message in payload['messages'][:-1])",
                "        return {'messages': [FakeMessage(f'answer to {user}; saw_first={marker}')]}",
                "",
                "def create_deep_agent(model, tools=None, system_prompt=None, name=None, **kwargs):",
                "    return FakeAgent(model, tools or [], system_prompt, name=name, **kwargs)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    run_cli(tmp_path, "init")
    session_result = run_cli(tmp_path, "session", "create", "ask session")
    session_id = parse_id(session_result.stdout, "sess_")

    first = run_cli(tmp_path, "ask", "first question", "--kernel", "deepagents")
    second = run_cli(tmp_path, "ask", "second question", "--kernel", "deepagents")

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert "answer to second question; saw_first=True" in second.stdout
    messages_text = (tmp_path / ".novi" / "sessions" / session_id / "messages.jsonl").read_text()
    assert '"role": "user"' in messages_text
    assert '"content": "first question"' in messages_text
    assert '"role": "assistant"' in messages_text
    assert "answer to first question" in messages_text
    latest_run = sorted((tmp_path / ".novi" / "runs").glob("run_*"))[-1]
    recent_messages = latest_run / "prompt_parts" / "70-recent-messages.jsonl"
    assert recent_messages.exists()
    assert "first question" in recent_messages.read_text()
    assert "runner_preflight" not in (latest_run / "tool_calls.jsonl").read_text()
    payloads = [
        json.loads(line)
        for line in (tmp_path / "captured_payloads.jsonl").read_text().splitlines()
    ]
    second_payload = payloads[-1]
    assert second_payload["messages"] == [
        {"content": "first question", "role": "user"},
        {"content": "answer to first question; saw_first=False", "role": "assistant"},
        {"content": "second question", "role": "user"},
    ]
    assert "first question" not in second_payload["system_prompt"]
    assert "second question" not in second_payload["system_prompt"]
    request_text = (latest_run / "model_request.yaml").read_text()
    assert "model_messages_path:" in request_text


def test_prompt_lists_deepagents_callable_tool_names(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "tool protocol run")
    run_cli(tmp_path, "agent", "grant-tool", "agent_orchestrator", "filesystem.read")

    result = run_cli(tmp_path, "run", "start", "research", "explain tools", "--kernel", "simple")

    assert result.returncode == 0, result.stderr
    run_id = parse_id(result.stdout, "run_")
    tools_prompt = tmp_path / ".novi" / "runs" / run_id / "prompt_parts" / "40-tools.md"
    tools_text = tools_prompt.read_text()
    assert "Callable name: search_stub_query" in tools_text
    assert "Callable name: filesystem_read" in tools_text
    assert "Call the tool function when tool output is needed" in tools_text


def test_deepagents_kernel_supports_openai_chat_compatible_provider(tmp_path, monkeypatch):
    (tmp_path / "deepagents.py").write_text(
        "\n".join(
            [
                "class FakeMessage:",
                "    def __init__(self, content):",
                "        self.content = content",
                "",
                "class FakeAgent:",
                "    def __init__(self, model, tools, system_prompt, name=None, **kwargs):",
                "        self.model = model",
                "",
                "    def invoke(self, payload):",
                "        return {'messages': [FakeMessage(",
                "            f'model={self.model.model}; base_url={self.model.base_url}; responses={self.model.use_responses_api}'",
                "        )]}",
                "",
                "def create_deep_agent(model, tools=None, system_prompt=None, name=None, **kwargs):",
                "    return FakeAgent(model, tools or [], system_prompt, name=name, **kwargs)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    package_dir = tmp_path / "langchain_openai"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text(
        "\n".join(
            [
                "class ChatOpenAI:",
                "    def __init__(self, model, api_key=None, base_url=None, use_responses_api=None):",
                "        self.model = model",
                "        self.api_key = api_key",
                "        self.base_url = base_url",
                "        self.use_responses_api = use_responses_api",
                "",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("NOVI_MODEL_PROVIDER", "openai_chat")
    monkeypatch.setenv("NOVI_MODEL", "Qwen/QwQ-32B")
    monkeypatch.setenv("NOVI_API_BASE", "https://api.siliconflow.com/v1")
    monkeypatch.setenv("NOVI_API_KEY", "test-key")
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "siliconflow compatible run")

    result = run_cli(tmp_path, "run", "start", "research", "invoke compatible chat", "--kernel", "deepagents")

    assert result.returncode == 0, result.stderr
    run_id = parse_id(result.stdout, "run_")
    run_dir = tmp_path / ".novi" / "runs" / run_id
    response_text = (run_dir / "response.md").read_text()
    model_calls = (run_dir / "model_calls.jsonl").read_text()

    assert "model=Qwen/QwQ-32B" in response_text
    assert "base_url=https://api.siliconflow.com/v1" in response_text
    assert "responses=False" in response_text
    assert '"model_provider": "openai_chat"' in model_calls


def test_deepagents_kernel_uses_project_model_config_without_env(tmp_path, monkeypatch):
    (tmp_path / "deepagents.py").write_text(
        "\n".join(
            [
                "class FakeMessage:",
                "    def __init__(self, content):",
                "        self.content = content",
                "",
                "class FakeAgent:",
                "    def __init__(self, model, tools, system_prompt, name=None, **kwargs):",
                "        self.model = model",
                "",
                "    def invoke(self, payload):",
                "        return {'messages': [FakeMessage(",
                "            f'model={self.model.model}; base_url={self.model.base_url}; responses={self.model.use_responses_api}'",
                "        )]}",
                "",
                "def create_deep_agent(model, tools=None, system_prompt=None, name=None, **kwargs):",
                "    return FakeAgent(model, tools or [], system_prompt, name=name, **kwargs)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    package_dir = tmp_path / "langchain_openai"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text(
        "\n".join(
            [
                "class ChatOpenAI:",
                "    def __init__(self, model, api_key=None, base_url=None, use_responses_api=None):",
                "        self.model = model",
                "        self.api_key = api_key",
                "        self.base_url = base_url",
                "        self.use_responses_api = use_responses_api",
                "",
            ]
        ),
        encoding="utf-8",
    )
    for name in ["NOVI_MODEL_PROVIDER", "NOVI_MODEL", "NOVI_API_BASE", "NOVI_API_KEY", "OPENAI_API_BASE", "OPENAI_API_KEY"]:
        monkeypatch.delenv(name, raising=False)
    run_cli(tmp_path, "init")
    run_cli(
        tmp_path,
        "configure",
        "model",
        "siliconflow",
        "--model",
        "Pro/zai-org/GLM-4.7",
        "--api-key",
        "secret-config-key",
    )
    run_cli(tmp_path, "session", "create", "project config model run")

    result = run_cli(tmp_path, "run", "start", "research", "invoke configured model", "--kernel", "deepagents")

    assert result.returncode == 0, result.stderr
    run_id = parse_id(result.stdout, "run_")
    run_dir = tmp_path / ".novi" / "runs" / run_id
    response_text = (run_dir / "response.md").read_text()
    model_calls = (run_dir / "model_calls.jsonl").read_text()
    request_text = (run_dir / "model_request.yaml").read_text()

    assert "model=Pro/zai-org/GLM-4.7" in response_text
    assert "base_url=https://api.siliconflow.cn/v1" in response_text
    assert "responses=False" in response_text
    assert '"model_provider": "openai_chat"' in model_calls
    assert '"model_base_url": "https://api.siliconflow.cn/v1"' in model_calls
    assert "model_provider: openai_chat" in request_text
    assert "model_base_url: https://api.siliconflow.cn/v1" in request_text
    assert "secret-config-key" not in request_text


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


def test_run_archives_compiled_kernel_bindings(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "binding run")

    result = run_cli(tmp_path, "run", "start", "research", "inspect bindings")

    assert result.returncode == 0, result.stderr
    run_id = parse_id(result.stdout, "run_")
    run_dir = tmp_path / ".novi" / "runs" / run_id
    binding_text = (run_dir / "kernel_bindings.jsonl").read_text()
    inspect_result = run_cli(tmp_path, "run", "inspect", run_id)
    trace_result = run_cli(tmp_path, "run", "trace", run_id)

    assert '"agent_id": "agent_orchestrator"' in binding_text
    assert '"authority_level": "collaborator"' in binding_text
    assert '"kernel": "simple"' in binding_text
    assert '"tool_names": ["search_stub_query"]' in binding_text
    assert "Kernel bindings:" in inspect_result.stdout
    assert "agent_orchestrator simple" in inspect_result.stdout
    assert "Kernel bindings:" in trace_result.stdout


def test_kernel_binding_filters_unexposed_tools(tmp_path):
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "agent", "create", "agent_reader", "--role", "reader")
    run_cli(tmp_path, "agent", "grant-tool", "agent_reader", "filesystem.read")
    run_cli(tmp_path, "session", "create", "routing run")

    result = run_cli(tmp_path, "run", "start", "research", "inspect routing", "--agent", "agent_reader")

    assert result.returncode == 0, result.stderr
    run_id = parse_id(result.stdout, "run_")
    binding_text = (tmp_path / ".novi" / "runs" / run_id / "kernel_bindings.jsonl").read_text()

    assert '"agent_id": "agent_reader"' in binding_text
    assert '"tool_ids": []' in binding_text
    assert '"unavailable_tool_ids": ["filesystem.read"]' in binding_text
    assert '"tool_not_exposed_to_agent"' in binding_text


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
