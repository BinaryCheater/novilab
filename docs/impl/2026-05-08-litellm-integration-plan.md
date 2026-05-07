# LiteLLM Integration Plan

Date: 2026-05-08

Branch/worktree: `dev-litellm` at `/Users/cyan/Project/novilab/.worktrees/litellm`

## Context

Novi already has a narrow model provider boundary:

- `.novi/novi.yaml` stores `model.provider`, `model.model`, `model.base_url`, and `model.api_key`.
- `src/novi_lab/model_providers.py` resolves DeepAgents models.
- `openai_chat`, `openai_compatible_chat`, and `siliconflow` currently use `langchain_openai.ChatOpenAI` with `use_responses_api=False`.
- `openai_responses` currently passes a model string through to DeepAgents. Current DeepAgents docs say `openai:` string models are resolved through LangChain `init_chat_model` and use the OpenAI Responses API by default. This means Novi can use Responses through DeepAgents' default string-model path, but Novi does not yet explicitly pass `.novi/novi.yaml` `base_url` and `api_key` into an initialized Responses model object.
- Run artifacts already record `model_provider`, `model_profile`, `model_base_url`, `model_calls.jsonl`, `model_request.yaml`, `deepagents_messages.jsonl`, and model response artifacts.

LiteLLM is relevant because it can sit between Novi and upstream model providers as:

- an OpenAI-compatible proxy endpoint for `/v1/chat/completions` and other endpoints;
- a config-driven gateway using `model_list` and `litellm_params`;
- a router/load-balancer with fallbacks, rate limits, budgets, and provider-specific params;
- a Python SDK with `completion`, `responses`, and routing APIs.

Official docs reviewed:

- LiteLLM proxy config: https://docs.litellm.ai/docs/proxy/configs
- LiteLLM routing/load balancing: https://docs.litellm.ai/docs/routing
- LiteLLM supported endpoints: https://docs.litellm.ai/docs/supported_endpoints
- LiteLLM `/responses`: https://docs.litellm.ai/docs/response_api
- LiteLLM providers: https://docs.litellm.ai/docs/providers
- DeepAgents `create_deep_agent` model behavior: https://reference.langchain.com/python/deepagents/graph/create_deep_agent

## Recommendation

Use an embedded-proxy-config integration.

Phase 1 should not put LiteLLM SDK calls on Novi's model execution hot path. Instead, Novi should own an inspectable LiteLLM proxy config and either let the user start the proxy manually or start it as an attached child process for the current command. LiteLLM then acts as a local model gateway behind Novi's existing OpenAI-compatible model boundary:

```yaml
model:
  provider: litellm_proxy
  model: research-primary
  base_url: http://localhost:4000/v1
  api_key: os.environ/LITELLM_PROXY_API_KEY
```

At runtime, `litellm_proxy` can use either chat-completions or Responses depending on the selected `api_shape`. `model_provider` should be recorded as `litellm_proxy`, `model_base_url` should be the LiteLLM proxy URL, and `model_api_shape` should be `responses` or `chat_completions`.

This gets Novi:

- one stable service path for multiple upstreams;
- LiteLLM model aliases and routing config;
- fallback and provider switching outside Novi's first provider adapter;
- minimal disruption to DeepAgents and existing model traces;
- a project-local, filesystem-readable gateway config that matches Novi's local-first direction.

It also preserves Novi's core boundary: LiteLLM routes model calls, but Novi still owns sessions, runs, tools, artifacts, memory, policy, and audit.

## Proposed Phases

### Phase A: Proxy smoke path with no Novi code changes

Purpose: validate LiteLLM behavior before adding code.

1. Start a LiteLLM proxy manually with a minimal config:

```yaml
model_list:
  - model_name: research-primary
    litellm_params:
      model: openai/gpt-4.1-mini
      api_key: os.environ/OPENAI_API_KEY

general_settings:
  master_key: os.environ/LITELLM_PROXY_API_KEY
```

2. Configure Novi through the existing generic OpenAI-compatible path:

```bash
uv run --extra deepagents novi configure model openai-chat \
  --model research-primary \
  --base-url http://localhost:4000/v1 \
  --api-key "$LITELLM_PROXY_API_KEY"
```

3. Run one non-tool and one tool-using DeepAgents smoke test:

```bash
uv run --extra deepagents novi doctor model
uv run --extra deepagents novi ask "Say one sentence and do not call tools." --kernel deepagents
uv run --extra deepagents novi run start research "Use the search stub once, then summarize." --kernel deepagents
```

4. Inspect `model_calls.jsonl`, `deepagents_messages.jsonl`, and `tool_calls.jsonl`.

Expected result: Novi sees LiteLLM as an OpenAI-compatible chat provider. Tool calls still flow through Novi ToolRuntime.

### Phase B: Embedded LiteLLM proxy config

Purpose: make LiteLLM a first-class local gateway without replacing Novi's model/run ledger.

Files to modify:

- `src/novi_lab/cli.py`
- `src/novi_lab/model_providers.py`
- `src/novi_lab/litellm_proxy.py`
- `docs/guide/configuration.md`
- `docs/guide/yaml-config.md`
- `tests/test_cli_core_loop.py`

Behavior:

- Add `novi configure model litellm-proxy --model <alias> --base-url <url> --api-key <key>`.
- Default `base_url` to `http://localhost:4000/v1` if omitted.
- Add a project-local LiteLLM config at `.novi/litellm/config.yaml`.
- Add a command to initialize or update the config, for example:

```bash
novi litellm init \
  --model-name research-primary \
  --upstream-model openai/gpt-4.1-mini \
  --upstream-api-key-env OPENAI_API_KEY
```

- Add a manual start command printout:

```bash
uv run --extra litellm litellm --config .novi/litellm/config.yaml --port 4000
```

- Add an attached start path, scoped to the current command or explicit foreground process:

```bash
novi litellm start --port 4000
```

- Keep daemon/process supervision minimal: no background service manager in this version.
- Resolve `litellm_proxy` through an explicit API-shape choice:
  - `api_shape: responses`: initialize an OpenAI-compatible model with `use_responses_api=True` against the LiteLLM proxy.
  - `api_shape: chat_completions`: initialize `ChatOpenAI(..., use_responses_api=False)` against the LiteLLM proxy.
- Preserve `model_provider: litellm_proxy` in trace records instead of collapsing it to `openai_chat`.
- Preserve `model_api_shape` in trace records.
- Update `doctor model` to print provider/base URL/key status without exposing secrets.
- Add tests for CLI config, provider resolution, and trace record output.

Implementation note: keep `openai_chat` behavior unchanged. `litellm_proxy` is an alias-plus-trace distinction plus project-local LiteLLM config ownership, not a replacement for Novi's execution stack.

### Phase C: LiteLLM config details

Purpose: make local-first setup inspectable.

Generate this project-local file:

```yaml
model_list:
  - model_name: research-primary
    litellm_params:
      model: openai/gpt-4.1-mini
      api_key: os.environ/OPENAI_API_KEY
  - model_name: coding-primary
    litellm_params:
      model: anthropic/claude-sonnet-4-5
      api_key: os.environ/ANTHROPIC_API_KEY

router_settings:
  routing_strategy: simple-shuffle

general_settings:
  master_key: os.environ/LITELLM_PROXY_API_KEY
```

Do not store upstream provider API keys in Novi project YAML. Prefer environment references in LiteLLM config and only store the LiteLLM proxy key in Novi during the prototype.

### Phase D: Responses path hardening

Purpose: make Responses explicit and auditable rather than relying only on DeepAgents string-model defaults.

Current understanding:

- DeepAgents supports Responses by default for `openai:` model strings.
- Novi's `openai_responses` path does not fall back to compatible chat; it delegates model resolution to DeepAgents.
- Novi does not yet explicitly construct a Responses model with project-local `base_url` and `api_key`.

Required work:

- Add tests that `openai_responses` does not resolve through the compatible-chat `use_responses_api=False` path.
- Add a project-configured Responses path that passes `base_url`, `api_key`, and `use_responses_api=True` explicitly when needed.
- Add `model_api_shape: responses` to request and call records.
- Smoke test tool calling through:
  - direct OpenAI Responses;
  - LiteLLM proxy `/responses`;
  - LiteLLM bridge from `/responses` to `/chat/completions` where upstream lacks Responses.

Recommendation: prefer Responses for OpenAI-native models and for LiteLLM aliases that pass the smoke test. Use chat-completions only for compatible providers/models that do not support Responses or whose Responses tool-call behavior fails.

### Phase E: Optional Python SDK / Router integration

Purpose: only if proxy deployment is too heavy or embedded routing is required.

Risks:

- DeepAgents currently accepts a model object/string through its LangChain-oriented path; LiteLLM SDK calls are function APIs, not automatically a compatible chat model object.
- A direct SDK adapter would need either a LangChain-compatible wrapper or a Novi-owned model adapter path outside DeepAgents.
- In-process routing would move retry/fallback behavior into Novi's process and make trace attribution more complicated.

Recommendation: defer until proxy-first proves insufficient.

## Key Problems To Resolve

1. Tool-call compatibility

   LiteLLM can normalize provider APIs, but provider/model tool-call behavior is still model-specific. Novi should keep a tool-call smoke test per configured model alias and record failures as provider compatibility issues, not ToolRuntime bugs by default.

2. Chat vs Responses semantics

   Novi currently archives `model_messages.jsonl` and DeepAgents messages in a chat-style shape. DeepAgents can use Responses underneath for `openai:` models, but Novi should record the selected API shape explicitly. If richer Responses items become important for audit, add `model_exchange.jsonl` rather than overloading chat message records.

3. Trace fidelity through a gateway

   `model_provider=litellm_proxy` hides the upstream provider unless Novi records LiteLLM alias metadata. Minimum trace fields should include `model_alias`, `gateway_base_url`, and optional `upstream_model` if configured locally.

4. Secret ownership

   LiteLLM config supports environment references and centralized credentials. Novi should not duplicate upstream provider keys in `.novi/novi.yaml`. Prototype storage of the LiteLLM proxy key is acceptable only with the existing warning that project YAML secrets are not final.

5. Service lifecycle

   A proxy introduces a separate process. For this version, Novi can support both manual startup and an attached foreground child process. It should not silently install a background daemon. Later, a `novi doctor model --ping` check can detect proxy availability.

6. Routing and fallback audit

   If LiteLLM retries or falls back internally, Novi may only see one model call. For scientific/replay audit, important fallback metadata should be surfaced either from LiteLLM response headers/logs or from a static alias config captured with the run.

7. Cost and budget policy split

   LiteLLM can enforce budgets and rate limits, but Novi policy still owns whether a run is allowed to call a model/tool. LiteLLM budget failures should be recorded as model-call failures, not Novi approval decisions.

8. Local-first constraints

   LiteLLM proxy is useful, but Novi should still keep the deterministic `simple` kernel and generic `openai_chat` path. LiteLLM must remain optional.

## Minimal Implementation Checklist

- [ ] Add tests for `litellm-proxy` CLI config writing `.novi/novi.yaml`.
- [ ] Add tests for `.novi/litellm/config.yaml` generation.
- [ ] Add tests for `novi litellm start` command construction without launching a real long-running proxy.
- [ ] Add tests for `doctor model` output with `litellm_proxy`.
- [ ] Add tests that `resolve_deepagents_model` maps `litellm_proxy` to the selected API shape with base URL and API key.
- [ ] Add tests that model trace records preserve `model_provider: litellm_proxy` and `model_api_shape`.
- [ ] Add tests that `openai_responses` does not fall back to `use_responses_api=False`.
- [ ] Implement provider parsing in `src/novi_lab/cli.py`.
- [ ] Implement provider resolution in `src/novi_lab/model_providers.py`.
- [ ] Implement LiteLLM config generation and start command support.
- [ ] Update configuration guide and YAML guide.
- [ ] Run `uv run --extra dev pytest`.
- [ ] Manually smoke test against a LiteLLM proxy before calling the integration complete.

## Decision Points Before Coding Beyond Phase B

- Should Novi use LiteLLM proxy only, or also embed LiteLLM SDK later?
- Should `litellm_proxy` default to `http://localhost:4000/v1`?
- Should `.novi/novi.yaml` store LiteLLM alias only, with upstream alias metadata kept in `.novi/litellm/config.yaml`?
- Should `responses` be the default `api_shape` for `litellm_proxy`, with chat-completions as an explicit compatibility mode?
- Should Novi add a `doctor model --ping` network check, or keep `doctor model` non-network for now?
