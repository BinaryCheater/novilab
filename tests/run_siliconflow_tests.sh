#!/usr/bin/env bash
# =============================================================================
# SiliconFlow API Integration Test Script for Novi Lab
# =============================================================================
# This script tests the full Novi → SiliconFlow pipeline, both direct and via
# LiteLLM proxy. It requires uv and a valid SiliconFlow API key.
#
# Usage:
#   SILICONFLOW_API_KEY=sk-... bash tests/run_siliconflow_tests.sh
#
# Or with LiteLLM proxy tests:
#   SILICONFLOW_API_KEY=sk-... LITELLM_PROXY_API_KEY=your-key bash tests/run_siliconflow_tests.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# ── Config ──────────────────────────────────────────────────────────────────
SILICONFLOW_BASE_URL="${SILICONFLOW_BASE_URL:-https://api.siliconflow.cn/v1}"
SILICONFLOW_API_KEY="${SILICONFLOW_API_KEY:-}"
LITELLM_PROXY_API_KEY="${LITELLM_PROXY_API_KEY:-test-proxy-key}"
DEFAULT_MODEL="${NOVI_TEST_MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
ALT_MODEL="${NOVI_TEST_ALT_MODEL:-MiniMaxAI/MiniMax-M2.5}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass_count=0
fail_count=0

pass() { echo -e "${GREEN}PASS${NC} $1"; pass_count=$((pass_count + 1)); }
fail() { echo -e "${RED}FAIL${NC} $1: $2"; fail_count=$((fail_count + 1)); }

# ── Pre-flight checks ──────────────────────────────────────────────────────

echo "=== Novi Lab SiliconFlow Integration Tests ==="
echo ""
echo "Base URL: $SILICONFLOW_BASE_URL"
echo "Default model: $DEFAULT_MODEL"
echo "Alt model: $ALT_MODEL"
echo ""

if [ -z "$SILICONFLOW_API_KEY" ]; then
    echo -e "${RED}ERROR: SILICONFLOW_API_KEY is not set.${NC}"
    echo "Usage: SILICONFLOW_API_KEY=sk-... bash tests/run_siliconflow_tests.sh"
    exit 1
fi

if ! command -v uv &>/dev/null; then
    echo -e "${RED}ERROR: uv is not installed.${NC}"
    exit 1
fi

echo -e "${YELLOW}[preflight] Checking dependencies...${NC}"
uv run --extra deepagents python -c "import deepagents, langchain_openai; print('deepagents + langchain_openai OK')" || {
    echo -e "${RED}ERROR: deepagents dependencies not installed. Run: uv sync --extra deepagents${NC}"
    exit 1
}

# ── Step 1: Run unit tests (no network) ────────────────────────────────────

echo ""
echo -e "${YELLOW}[step 1] Running unit tests (no network)...${NC}"
uv run --extra dev pytest tests/test_cli_core_loop.py -x -q 2>&1 | tail -5
echo ""

# ── Step 2: Run integration tests (non-network config tests) ───────────────

echo -e "${YELLOW}[step 2] Running integration config tests...${NC}"
uv run --extra dev pytest tests/test_siliconflow_integration.py -v \
    -k "not api_key and not direct and not e2e and not chat_completion" \
    --tb=short 2>&1
echo ""

# ── Step 3: Direct ChatOpenAI test ─────────────────────────────────────────

echo -e "${YELLOW}[step 3] Testing direct ChatOpenAI → SiliconFlow...${NC}"
uv run --extra deepagents python << 'PYEOF'
import os, sys
from langchain_openai import ChatOpenAI

model_name = os.environ.get("NOVI_TEST_MODEL", "deepseek-ai/DeepSeek-V4-Flash")
api_key = os.environ["SILICONFLOW_API_KEY"]
base_url = os.environ.get("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")

print(f"[direct] Model: {model_name}")
print(f"[direct] Base URL: {base_url}")

model = ChatOpenAI(
    model=model_name,
    api_key=api_key,
    base_url=base_url,
    use_responses_api=False,
)

try:
    result = model.invoke("Say hello in exactly one word.")
    content = result.content.strip() if hasattr(result, "content") else str(result).strip()
    print(f"[direct] PASS: Response = '{content}'")
except Exception as e:
    print(f"[direct] FAIL: {e}")
    sys.exit(1)
PYEOF
echo ""

# ── Step 4: Direct ChatOpenAI with alternate model ─────────────────────────

echo -e "${YELLOW}[step 4] Testing alternate model (MiniMax)...${NC}"
uv run --extra deepagents python << PYEOF
import os, sys
from langchain_openai import ChatOpenAI

alt_model = os.environ.get("NOVI_TEST_ALT_MODEL", "MiniMaxAI/MiniMax-M2.5")
api_key = os.environ["SILICONFLOW_API_KEY"]
base_url = os.environ.get("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")

model = ChatOpenAI(
    model=alt_model,
    api_key=api_key,
    base_url=base_url,
    use_responses_api=False,
)

try:
    result = model.invoke("Say the word 'hello' and nothing else.")
    content = result.content.strip() if hasattr(result, "content") else str(result).strip()
    print(f"[alt-model] PASS: {alt_model} → '{content}'")
except Exception as e:
    print(f"[alt-model] FAIL: {e}")
    sys.exit(1)
PYEOF
echo ""

# ── Step 5: Direct ChatOpenAI multi-turn conversation ──────────────────────

echo -e "${YELLOW}[step 5] Testing multi-turn conversation...${NC}"
uv run --extra deepagents python << 'PYEOF'
import os, sys
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

model_name = os.environ.get("NOVI_TEST_MODEL", "deepseek-ai/DeepSeek-V4-Flash")
api_key = os.environ["SILICONFLOW_API_KEY"]
base_url = os.environ.get("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")

model = ChatOpenAI(
    model=model_name,
    api_key=api_key,
    base_url=base_url,
    use_responses_api=False,
)

messages = [
    HumanMessage(content="My name is TestBot. Remember it."),
    AIMessage(content="Nice to meet you, TestBot! I'll remember your name."),
    HumanMessage(content="What is my name?"),
]

try:
    result = model.invoke(messages)
    content = result.content.strip() if hasattr(result, "content") else str(result).strip()
    if "TestBot" in content:
        print(f"[multi-turn] PASS: Model remembered name → '{content}'")
    else:
        print(f"[multi-turn] PARTIAL: Response didn't contain 'TestBot' → '{content}'")
except Exception as e:
    print(f"[multi-turn] FAIL: {e}")
    sys.exit(1)
PYEOF
echo ""

# ── Step 6: List available models ──────────────────────────────────────────

echo -e "${YELLOW}[step 6] Listing available models...${NC}"
uv run --extra deepagents python << PYEOF
import os, sys, httpx

api_key = os.environ["SILICONFLOW_API_KEY"]
base_url = os.environ.get("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")

client = httpx.Client(timeout=30)
try:
    r = client.get(
        f"{base_url}/models",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    if r.status_code != 200:
        print(f"[models] FAIL: HTTP {r.status_code}: {r.text[:300]}")
        sys.exit(1)
    data = r.json()
    models = data.get("data", [])
    model_ids = [m["id"] for m in models]
    ds = [m for m in model_ids if "deepseek" in m.lower()]
    mm = [m for m in model_ids if "minimax" in m.lower()]
    print(f"[models] Total: {len(models)}")
    print(f"[models] DeepSeek: {ds[:10]}")
    print(f"[models] MiniMax: {mm[:10]}")
    print("[models] PASS")
except Exception as e:
    print(f"[models] FAIL: {e}")
    sys.exit(1)
finally:
    client.close()
PYEOF
echo ""

# ── Step 7: Novi CLI ask via direct connection ─────────────────────────────

echo -e "${YELLOW}[step 7] Testing Novi CLI ask (direct SiliconFlow)...${NC}"
TEST_DIR=$(mktemp -d)
cleanup() { rm -rf "$TEST_DIR"; }
trap cleanup EXIT

export PYTHONPATH="$REPO_ROOT/src:$PYTHONPATH"

# Init workspace
uv run --extra deepagents python -m novi_lab.cli init 2>&1 >/dev/null

# Configure model
uv run --extra deepagents python -m novi_lab.cli configure model siliconflow \
    --model "$DEFAULT_MODEL" \
    --api-key "$SILICONFLOW_API_KEY" 2>&1 >/dev/null

# Create session
uv run --extra deepagents python -m novi_lab.cli session create "api test" 2>&1 >/dev/null

# Ask a simple question
ask_result=$(uv run --extra deepagents python -m novi_lab.cli ask \
    --kernel deepagents \
    "Say hello in exactly one sentence. Do not call any tools." 2>&1)
ask_rc=$?

if [ $ask_rc -eq 0 ]; then
    echo "[novi-ask] PASS"
    echo "$ask_result"
else
    echo "[novi-ask] FAIL: $ask_result"
fi
echo ""

# ── Step 8: Novi CLI ask with tool call ────────────────────────────────────

echo -e "${YELLOW}[step 8] Testing Novi CLI ask with tool call...${NC}"
tool_result=$(uv run --extra deepagents python -m novi_lab.cli ask \
    --kernel deepagents \
    "Use the search_stub.query tool to look up 'novi lab project', then summarize your findings in one sentence." 2>&1)
tool_rc=$?

if [ $tool_rc -eq 0 ]; then
    echo "[novi-tool-ask] PASS"
    echo "$tool_result"
else
    echo "[novi-tool-ask] FAIL: $tool_result"
fi
echo ""

# ── Step 9: Run full pytest integration suite ──────────────────────────────

echo -e "${YELLOW}[step 9] Running full pytest integration suite...${NC}"
SILICONFLOW_API_KEY="$SILICONFLOW_API_KEY" \
LITELLM_PROXY_API_KEY="$LITELLM_PROXY_API_KEY" \
    uv run --extra dev pytest tests/test_siliconflow_integration.py -v --tb=short 2>&1
echo ""

# ── Step 10: LiteLLM proxy smoke test (if litellm available) ───────────────

echo -e "${YELLOW}[step 10] Testing LiteLLM proxy setup...${NC}"
if command -v litellm &>/dev/null; then
    LITELLM_DIR=$(mktemp -d)
    trap "rm -rf $LITELLM_DIR; cleanup" EXIT
    cd "$LITELLM_DIR"

    uv run --extra deepagents python -m novi_lab.cli init 2>&1 >/dev/null
    uv run --extra deepagents python -m novi_lab.cli litellm init \
        --model-name "research-primary" \
        --upstream-model "$DEFAULT_MODEL" \
        --upstream-api-key-env "SILICONFLOW_API_KEY" \
        --upstream-base-url "$SILICONFLOW_BASE_URL" \
        --proxy-api-key-env "LITELLM_PROXY_API_KEY" \
        --api-shape "responses" \
        --port 41999 2>&1 >/dev/null

    echo "[litellm-setup] Config generated:"
    cat .novi/litellm/config.yaml
    echo ""

    # Start proxy in background
    echo "[litellm-setup] Starting proxy..."
    export LITELLM_PROXY_API_KEY
    litellm --config .novi/litellm/config.yaml --port 41999 &
    PROXY_PID=$!
    echo "[litellm-setup] Proxy PID: $PROXY_PID"

    # Wait for proxy
    for i in $(seq 1 30); do
        if curl -s -o /dev/null "http://localhost:41999/health" 2>/dev/null; then
            echo "[litellm-setup] Proxy ready on port 41999"
            break
        fi
        sleep 1
    done

    # Configure Novi to use proxy
    uv run --extra deepagents python -m novi_lab.cli configure model litellm-proxy \
        --model "research-primary" \
        --base-url "http://localhost:41999/v1" \
        --api-key "$LITELLM_PROXY_API_KEY" \
        --api-shape "responses" \
        --no-auto-start 2>&1 >/dev/null

    uv run --extra deepagents python -m novi_lab.cli session create "litellm test" 2>&1 >/dev/null

    proxy_result=$(uv run --extra deepagents python -m novi_lab.cli ask \
        --kernel deepagents \
        "Say 'litellm works' and nothing else. Do not call tools." 2>&1)
    proxy_rc=$?

    kill $PROXY_PID 2>/dev/null || true

    if [ $proxy_rc -eq 0 ]; then
        echo "[litellm-e2e] PASS"
        echo "$proxy_result"
    else
        echo "[litellm-e2e] FAIL: $proxy_result"
    fi
    cd "$REPO_ROOT"
else
    echo "[litellm-setup] SKIP: litellm executable not found"
    echo "[litellm-setup] Install with: uv sync --extra litellm"
fi
echo ""

# ── Summary ─────────────────────────────────────────────────────────────────

echo ""
echo "=== Test Summary ==="
echo "All tests completed."
echo "Run full pytest suite for detailed results:"
echo "  SILICONFLOW_API_KEY=sk-... uv run pytest tests/ -v"
