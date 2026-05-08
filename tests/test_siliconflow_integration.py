"""
Integration tests for SiliconFlow API via Novi Lab.

These tests make real network calls to SiliconFlow API and optionally
through a local LiteLLM proxy. They require valid API credentials.

Usage:
    # Direct connection tests only
    SILICONFLOW_API_KEY=sk-... uv run pytest tests/test_siliconflow_integration.py -v

    # With LiteLLM proxy tests
    SILICONFLOW_API_KEY=sk-... LITELLM_PROXY_API_KEY=test-key uv run pytest tests/test_siliconflow_integration.py -v

    # With custom model
    SILICONFLOW_API_KEY=sk-... NOVI_TEST_MODEL=deepseek-ai/DeepSeek-V4-Flash uv run pytest tests/test_siliconflow_integration.py -v
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"
SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY", "")
LITELLM_PROXY_API_KEY = os.environ.get("LITELLM_PROXY_API_KEY", "test-proxy-key")
DEFAULT_MODEL = os.environ.get("NOVI_TEST_MODEL", "deepseek-ai/DeepSeek-V4-Flash")
ALT_MODEL = os.environ.get("NOVI_TEST_ALT_MODEL", "MiniMaxAI/MiniMax-M2.5")

# Skip all integration tests if no API key is provided
needs_api_key = pytest.mark.skipif(
    not SILICONFLOW_API_KEY,
    reason="SILICONFLOW_API_KEY environment variable not set",
)


def run_cli(cwd, *args, env=None):
    """Run the Novi CLI as a subprocess."""
    base_env = os.environ.copy()
    base_env["PYTHONPATH"] = str(REPO_ROOT / "src")
    if env:
        base_env.update(env)
    return subprocess.run(
        [sys.executable, "-m", "novi_lab.cli", *args],
        cwd=cwd,
        env=base_env,
        text=True,
        capture_output=True,
    )


# ── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def workspace(tmp_path):
    """Create a fresh Novi workspace with a session."""
    run_cli(tmp_path, "init")
    run_cli(tmp_path, "session", "create", "integration test")
    return tmp_path


@pytest.fixture
def siliconflow_workspace(workspace):
    """Workspace configured with SiliconFlow direct connection."""
    run_cli(
        workspace,
        "configure",
        "model",
        "siliconflow",
        "--model", DEFAULT_MODEL,
        "--api-key", SILICONFLOW_API_KEY,
    )
    return workspace


# ── Test 1: Direct ChatOpenAI via SiliconFlow ─────────────────────────────

@needs_api_key
def test_direct_chatopenai_simple_completion():
    """Verify langchain_openai.ChatOpenAI can call SiliconFlow directly."""
    from langchain_openai import ChatOpenAI

    model = ChatOpenAI(
        model=DEFAULT_MODEL,
        api_key=SILICONFLOW_API_KEY,
        base_url=SILICONFLOW_BASE_URL,
        use_responses_api=False,
    )
    result = model.invoke("Say hello in exactly one word.")
    content = result.content.strip() if hasattr(result, "content") else str(result).strip()

    assert len(content) > 0, "Model returned empty response"
    print(f"[direct] Model: {DEFAULT_MODEL}")
    print(f"[direct] Response: {content}")


@needs_api_key
def test_direct_chatopenai_with_alternate_model():
    """Verify alternate model works via SiliconFlow."""
    from langchain_openai import ChatOpenAI

    model = ChatOpenAI(
        model=ALT_MODEL,
        api_key=SILICONFLOW_API_KEY,
        base_url=SILICONFLOW_BASE_URL,
        use_responses_api=False,
    )
    result = model.invoke("Say the word 'hello' and nothing else.")
    content = result.content.strip() if hasattr(result, "content") else str(result).strip()

    assert len(content) > 0, "Model returned empty response"
    print(f"[direct-alt] Model: {ALT_MODEL}")
    print(f"[direct-alt] Response: {content}")


@needs_api_key
def test_direct_chatopenai_multi_turn_conversation():
    """Verify multi-turn conversation works via SiliconFlow."""
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, AIMessage

    model = ChatOpenAI(
        model=DEFAULT_MODEL,
        api_key=SILICONFLOW_API_KEY,
        base_url=SILICONFLOW_BASE_URL,
        use_responses_api=False,
    )
    messages = [
        HumanMessage(content="My name is TestBot. Remember it."),
        AIMessage(content="Nice to meet you, TestBot! I'll remember your name."),
        HumanMessage(content="What is my name?"),
    ]
    result = model.invoke(messages)
    content = result.content.strip() if hasattr(result, "content") else str(result).strip()

    assert len(content) > 0, "Model returned empty response"
    assert "TestBot" in content, f"Model didn't remember the name. Response: {content}"
    print(f"[multi-turn] Response: {content}")


# ── Test 2: Novi CLI via SiliconFlow ──────────────────────────────────────

@needs_api_key
def test_novi_doctor_model_siliconflow(siliconflow_workspace):
    """Verify `novi doctor model` reports SiliconFlow config correctly."""
    result = run_cli(siliconflow_workspace, "doctor", "model")

    assert result.returncode == 0, result.stderr
    assert "Provider: openai_chat" in result.stdout
    assert f"Model: {DEFAULT_MODEL}" in result.stdout
    assert "Base URL: https://api.siliconflow.cn/v1" in result.stdout
    assert "API key: set" in result.stdout
    print(f"[doctor] {result.stdout.strip()}")


@needs_api_key
def test_novi_ask_simple_question(siliconflow_workspace):
    """Verify `novi ask` completes a simple question via SiliconFlow."""
    result = run_cli(
        siliconflow_workspace,
        "ask",
        "--kernel", "deepagents",
        "Say hello in exactly one sentence. Do not call any tools.",
    )

    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert "Run:" in result.stdout
    print(f"[ask] {result.stdout}")


@needs_api_key
def test_novi_ask_with_tool_call(siliconflow_workspace):
    """Verify `novi ask` can use the search_stub tool via SiliconFlow."""
    result = run_cli(
        siliconflow_workspace,
        "ask",
        "--kernel", "deepagents",
        "Use the search_stub.query tool to look up 'quantum computing', then summarize what you found in one sentence.",
    )

    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert "Run:" in result.stdout
    print(f"[ask-tool] {result.stdout}")


@needs_api_key
def test_novi_ask_records_model_calls(siliconflow_workspace):
    """Verify model_calls.jsonl is properly recorded after an ask."""
    result = run_cli(
        siliconflow_workspace,
        "ask",
        "--kernel", "deepagents",
        "Say 'record test' and nothing else. Do not call tools.",
    )

    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    import re
    run_match = re.search(r"Run: (run_\S+)", result.stdout)
    assert run_match, f"Could not find run ID in: {result.stdout}"
    run_id = run_match.group(1)
    run_dir = siliconflow_workspace / ".novi" / "runs" / run_id

    assert (run_dir / "model_calls.jsonl").exists(), "model_calls.jsonl missing"
    assert (run_dir / "response.md").exists(), "response.md missing"

    model_calls = [
        json.loads(line) for line in (run_dir / "model_calls.jsonl").read_text().splitlines() if line.strip()
    ]
    assert len(model_calls) > 0, "No model calls recorded"
    call = model_calls[0]
    assert call["status"] == "success", f"Model call failed: {call.get('error')}"
    assert call["model_provider"] in {"openai_chat", "siliconflow"}, f"Unexpected provider: {call['model_provider']}"
    assert call["model_base_url"] == SILICONFLOW_BASE_URL

    print(f"[record] model_provider={call['model_provider']}")
    print(f"[record] model_profile={call['model_profile']}")
    print(f"[record] model_base_url={call['model_base_url']}")


# ── Test 3: LiteLLM Proxy Setup ──────────────────────────────────────────

def test_litellm_config_generation_for_siliconflow(workspace):
    """Verify litellm config for SiliconFlow upstream is generated correctly."""
    result = run_cli(
        workspace,
        "litellm",
        "init",
        "--model-name", "research-primary",
        "--upstream-model", DEFAULT_MODEL,
        "--upstream-api-key-env", "SILICONFLOW_API_KEY",
        "--upstream-base-url", SILICONFLOW_BASE_URL,
        "--proxy-api-key-env", "LITELLM_PROXY_API_KEY",
        "--api-shape", "responses",
    )

    assert result.returncode == 0, result.stderr
    litellm_config = workspace / ".novi" / "litellm" / "config.yaml"
    novi_config = workspace / ".novi" / "novi.yaml"

    assert litellm_config.exists(), "Litellm config not created"
    litellm_text = litellm_config.read_text()
    assert f"model: {DEFAULT_MODEL}" in litellm_text
    assert f"api_base: {SILICONFLOW_BASE_URL}" in litellm_text
    assert "api_key: os.environ/SILICONFLOW_API_KEY" in litellm_text
    assert "master_key: os.environ/LITELLM_PROXY_API_KEY" in litellm_text

    novi_text = novi_config.read_text()
    assert "provider: litellm_proxy" in novi_text
    assert "model: research-primary" in novi_text
    assert "base_url: http://localhost:4000/v1" in novi_text
    assert "api_shape: responses" in novi_text

    print(f"[litellm-config] Litellm config: {litellm_config}")
    print(f"[litellm-config] {litellm_text}")


def test_litellm_start_command_generation(workspace):
    """Verify `novi litellm start --print-command` prints correct command."""
    run_cli(
        workspace,
        "litellm",
        "init",
        "--model-name", "research-primary",
        "--upstream-model", DEFAULT_MODEL,
        "--upstream-api-key-env", "SILICONFLOW_API_KEY",
        "--upstream-base-url", SILICONFLOW_BASE_URL,
        "--port", "41997",
    )
    result = run_cli(workspace, "litellm", "start", "--port", "41997", "--print-command")

    assert result.returncode == 0, result.stderr
    assert "litellm --config" in result.stdout
    assert ".novi/litellm/config.yaml" in result.stdout
    assert "--port 41997" in result.stdout
    print(f"[litellm-cmd] {result.stdout.strip()}")


# ── Test 4: LiteLLM Proxy End-to-End ─────────────────────────────────────

@pytest.mark.skipif(
    not SILICONFLOW_API_KEY,
    reason="SILICONFLOW_API_KEY not set",
)
def test_litellm_proxy_e2e_flow(tmp_path):
    """
    End-to-end test: start LiteLLM proxy, configure Novi to use it, run ask.

    This test starts a real LiteLLM proxy process, waits for it to be ready,
    runs a Novi ask through it, and then tears down the proxy.
    """
    import shutil

    if not shutil.which("litellm"):
        pytest.skip("litellm executable not found on PATH")

    # Setup workspace
    run_cli(tmp_path, "init")
    run_cli(
        tmp_path,
        "litellm",
        "init",
        "--model-name", "research-primary",
        "--upstream-model", DEFAULT_MODEL,
        "--upstream-api-key-env", "SILICONFLOW_API_KEY",
        "--upstream-base-url", SILICONFLOW_BASE_URL,
        "--proxy-api-key-env", "LITELLM_PROXY_API_KEY",
        "--api-shape", "responses",
        "--port", "41998",
    )

    # Configure Novi to use the LiteLLM proxy (disable auto-start)
    run_cli(
        tmp_path,
        "configure",
        "model",
        "litellm-proxy",
        "--model", "research-primary",
        "--base-url", "http://localhost:41998/v1",
        "--api-key", LITELLM_PROXY_API_KEY,
        "--api-shape", "responses",
        "--no-auto-start",
    )

    # Start LiteLLM proxy in background
    litellm_config = tmp_path / ".novi" / "litellm" / "config.yaml"
    env = os.environ.copy()
    env["SILICONFLOW_API_KEY"] = SILICONFLOW_API_KEY
    env["LITELLM_PROXY_API_KEY"] = LITELLM_PROXY_API_KEY
    proxy_process = subprocess.Popen(
        ["litellm", "--config", str(litellm_config), "--port", "41998"],
        cwd=tmp_path,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        # Wait for proxy to be ready
        import socket
        ready = False
        for _ in range(50):
            try:
                with socket.create_connection(("localhost", 41998), timeout=0.2):
                    ready = True
                    break
            except OSError:
                time.sleep(0.3)
        assert ready, "LiteLLM proxy did not start within timeout"

        # Create session
        run_cli(tmp_path, "session", "create", "litellm e2e test")

        # Run ask through the proxy
        result = run_cli(
            tmp_path,
            "ask",
            "--kernel", "deepagents",
            "Say 'proxy works' and nothing else. Do not call tools.",
            env={"LITELLM_PROXY_API_KEY": LITELLM_PROXY_API_KEY},
        )

        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        # Verify records
        import re
        run_match = re.search(r"Run: (run_\S+)", result.stdout)
        assert run_match, f"Could not find run ID in: {result.stdout}"
        run_id = run_match.group(1)
        run_dir = tmp_path / ".novi" / "runs" / run_id

        model_calls = (run_dir / "model_calls.jsonl").read_text()
        assert '"model_provider": "litellm_proxy"' in model_calls
        assert '"model_api_shape": "responses"' in model_calls

        response = (run_dir / "response.md").read_text()
        assert "proxy works" in response.lower()

        print(f"[litellm-e2e] Run: {run_id}")
        print(f"[litellm-e2e] Model calls: {model_calls.strip()}")
        print(f"[litellm-e2e] Response: {response.strip()}")

    finally:
        proxy_process.terminate()
        try:
            proxy_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proxy_process.kill()


# ── Test 5: Provider resolution and trace fidelity ───────────────────────

def test_configured_model_record_siliconflow_maps_to_openai_chat(workspace):
    """Verify internal model record maps siliconflow correctly."""
    run_cli(
        workspace,
        "configure",
        "model",
        "siliconflow",
        "--model", "deepseek-ai/DeepSeek-V4-Flash",
        "--api-key", "test-key",
    )

    from novi_lab.model_providers import configured_model_record
    participant = {"model_profile": "deterministic-local"}
    record = configured_model_record(str(workspace), participant)

    assert record["model_provider"] == "openai_chat"
    assert record["model_base_url"] == "https://api.siliconflow.cn/v1"
    assert "model_api_shape" not in record  # chat provider, not responses


def test_configured_model_record_litellm_proxy_preserves_shape(workspace):
    """Verify litellm_proxy records preserve api_shape."""
    run_cli(
        workspace,
        "configure",
        "model",
        "litellm-proxy",
        "--model", "research-primary",
        "--base-url", "http://localhost:4000/v1",
        "--api-key", "sk-test",
        "--api-shape", "chat_completions",
    )

    from novi_lab.model_providers import configured_model_record
    participant = {"model_profile": "deterministic-local"}
    record = configured_model_record(str(workspace), participant)

    assert record["model_provider"] == "litellm_proxy"
    assert record["model_api_shape"] == "chat_completions"
    assert record["litellm_auto_start"] is True


def test_configured_model_record_litellm_proxy_defaults_to_responses(workspace):
    """Verify litellm_proxy defaults to responses shape."""
    run_cli(
        workspace,
        "configure",
        "model",
        "litellm-proxy",
        "--model", "coding-primary",
        "--base-url", "http://localhost:4000/v1",
        "--api-key", "sk-test",
        # no --api-shape, should default to responses
    )

    from novi_lab.model_providers import configured_model_record
    participant = {"model_profile": "deterministic-local"}
    record = configured_model_record(str(workspace), participant)

    assert record["model_api_shape"] == "responses"


# ── Test 6: API key and base_url checking ─────────────────────────────────

@needs_api_key
def test_siliconflow_api_key_is_valid():
    """Verify the SiliconFlow API key is valid by listing models."""
    import httpx

    client = httpx.Client(timeout=30)
    try:
        r = client.get(
            f"{SILICONFLOW_BASE_URL}/models",
            headers={"Authorization": f"Bearer {SILICONFLOW_API_KEY}"},
        )
        assert r.status_code == 200, f"API returned {r.status_code}: {r.text[:500]}"
        data = r.json()
        models = data.get("data", [])
        model_ids = [m["id"] for m in models]

        # Check our test models are available
        print(f"[api-check] Available models count: {len(models)}")
        ds_models = [m for m in model_ids if "deepseek" in m.lower()]
        mm_models = [m for m in model_ids if "minimax" in m.lower()]
        print(f"[api-check] DeepSeek models: {ds_models[:5]}")
        print(f"[api-check] MiniMax models: {mm_models[:5]}")

        assert any("deepseek" in m.lower() for m in model_ids), \
            f"No DeepSeek model found in available models. First 10: {model_ids[:10]}"
    finally:
        client.close()


@needs_api_key
def test_siliconflow_chat_completion_endpoint():
    """Verify the /v1/chat/completions endpoint works."""
    import httpx

    client = httpx.Client(timeout=60)
    try:
        r = client.post(
            f"{SILICONFLOW_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": DEFAULT_MODEL,
                "messages": [
                    {"role": "user", "content": "Reply with exactly: OK"}
                ],
                "max_tokens": 20,
            },
        )
        assert r.status_code == 200, f"API returned {r.status_code}: {r.text[:500]}"
        data = r.json()
        assert "choices" in data, f"Unexpected response: {json.dumps(data, indent=2)[:500]}"
        content = data["choices"][0]["message"]["content"]
        print(f"[chat-completion] Model: {data.get('model')}")
        print(f"[chat-completion] Content: {content}")
        assert len(content.strip()) > 0
    finally:
        client.close()


# ── Test 7: Print test summary ───────────────────────────────────────────

def test_print_integration_summary():
    """Non-test helper that prints the integration test setup instructions."""
    print("\n" + "=" * 60)
    print("SiliconFlow Integration Test Setup")
    print("=" * 60)
    print(f"Base URL: {SILICONFLOW_BASE_URL}")
    print(f"Default model: {DEFAULT_MODEL}")
    print(f"Alternate model: {ALT_MODEL}")
    print(f"API key set: {bool(SILICONFLOW_API_KEY)}")
    print()
    print("To run all integration tests:")
    print(f"  SILICONFLOW_API_KEY=sk-... uv run pytest tests/test_siliconflow_integration.py -v")
    print()
    print("To run direct connection tests only:")
    print(f"  SILICONFLOW_API_KEY=sk-... uv run pytest tests/test_siliconflow_integration.py -v -k 'direct'")
    print()
    print("To run with LiteLLM proxy E2E:")
    print(f"  SILICONFLOW_API_KEY=sk-... LITELLM_PROXY_API_KEY=test-key uv run pytest tests/test_siliconflow_integration.py -v -k 'e2e'")
    print("=" * 60)
