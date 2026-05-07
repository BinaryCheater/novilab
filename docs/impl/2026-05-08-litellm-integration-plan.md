# LiteLLM Integration Plan

Date: 2026-05-08

Branch/worktree: `dev-litellm` at `/Users/cyan/Project/novilab/.worktrees/litellm`

## Context

Novi already has a narrow model provider boundary:

- `.novi/novi.yaml` stores `model.provider`, `model.model`, `model.base_url`, and `model.api_key`.
- `src/novi_lab/model_providers.py` resolves DeepAgents models.
- `openai_chat`, `openai_compatible_chat`, and `siliconflow` currently use `langchain_openai.ChatOpenAI` with `use_responses_api=False`.
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

## Recommendation

Use a proxy-first integration.

Phase 1 should not embed LiteLLM SDK inside Novi. Instead, treat LiteLLM as an external model gateway behind Novi's existing `openai_chat` provider shape:

```yaml
model:
  provider: litellm_proxy
  model: research-primary
  base_url: http://localhost:4000/v1
  api_key: os.environ/LITELLM_PROXY_API_KEY
```

At runtime, `litellm_proxy` should resolve to the same `ChatOpenAI` path as `openai_chat`, with `model_provider` recorded as `litellm_proxy` and `model_base_url` recorded as the local or remote LiteLLM proxy URL.

This gets Novi:

- one stable service path for multiple upstreams;
- LiteLLM model aliases and routing config;
- fallback and provider switching outside Novi's first provider adapter;
- minimal disruption to DeepAgents and existing model traces.

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

### Phase B: First-class `litellm-proxy` provider

Purpose: make the supported path explicit without adding LiteLLM as an in-process dependency.

Files to modify:

- `src/novi_lab/cli.py`
- `src/novi_lab/model_providers.py`
- `docs/guide/configuration.md`
- `docs/guide/yaml-config.md`
- `tests/test_cli_core_loop.py`

Behavior:

- Add `novi configure model litellm-proxy --model <alias> --base-url <url> --api-key <key>`.
- Default `base_url` to `http://localhost:4000/v1` if omitted.
- Resolve `litellm_proxy` through `ChatOpenAI(..., use_responses_api=False)`.
- Preserve `model_provider: litellm_proxy` in trace records instead of collapsing it to `openai_chat`.
- Update `doctor model` to print provider/base URL/key status without exposing secrets.
- Add tests for CLI config, provider resolution, and trace record output.

Implementation note: keep `openai_chat` behavior unchanged. `litellm_proxy` is an alias-plus-trace distinction, not a separate model execution stack.

### Phase C: LiteLLM config helper

Purpose: make local-first setup inspectable.

Add a command or documented template for a LiteLLM proxy config file, probably under `docs/guide/` first:

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

Do not store provider API keys in Novi project YAML. Prefer environment references in LiteLLM config and only store the LiteLLM proxy key in Novi during the prototype.

### Phase D: Responses API spike

Purpose: decide whether Novi should expose `openai_responses` through LiteLLM.

Questions to test:

- Can the current DeepAgents/LangChain path use `ChatOpenAI(use_responses_api=True)` against LiteLLM proxy reliably?
- Does LiteLLM `/responses` preserve tool-call semantics that DeepAgents/LangChain can parse?
- When LiteLLM bridges `/responses` to `/chat/completions`, are response items, reasoning traces, and tool messages still auditable enough for Novi?
- Does provider-specific state leak into LiteLLM rather than Novi run records?

Recommendation: keep `openai_responses` reserved until a smoke matrix passes. Novi's current model-message archive is chat-shaped, and the run ledger should not pretend to have Responses semantics until request/response records are explicit.

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

   Novi currently archives `model_messages.jsonl` and DeepAgents messages in a chat-style shape. `/responses` adds a different event/item model. Supporting it properly may require a new `model_exchange.jsonl` schema rather than overloading chat message records.

3. Trace fidelity through a gateway

   `model_provider=litellm_proxy` hides the upstream provider unless Novi records LiteLLM alias metadata. Minimum trace fields should include `model_alias`, `gateway_base_url`, and optional `upstream_model` if configured locally.

4. Secret ownership

   LiteLLM config supports environment references and centralized credentials. Novi should not duplicate upstream provider keys in `.novi/novi.yaml`. Prototype storage of the LiteLLM proxy key is acceptable only with the existing warning that project YAML secrets are not final.

5. Service lifecycle

   A proxy introduces a separate process. For v0, Novi should document how to run it rather than silently managing a daemon. Later, a `novi doctor model --ping` check can detect proxy availability.

6. Routing and fallback audit

   If LiteLLM retries or falls back internally, Novi may only see one model call. For scientific/replay audit, important fallback metadata should be surfaced either from LiteLLM response headers/logs or from a static alias config captured with the run.

7. Cost and budget policy split

   LiteLLM can enforce budgets and rate limits, but Novi policy still owns whether a run is allowed to call a model/tool. LiteLLM budget failures should be recorded as model-call failures, not Novi approval decisions.

8. Local-first constraints

   LiteLLM proxy is useful, but Novi should still keep the deterministic `simple` kernel and generic `openai_chat` path. LiteLLM must remain optional.

## Minimal Implementation Checklist

- [ ] Add tests for `litellm-proxy` CLI config writing `.novi/novi.yaml`.
- [ ] Add tests for `doctor model` output with `litellm_proxy`.
- [ ] Add tests that `resolve_deepagents_model` maps `litellm_proxy` to `ChatOpenAI` with base URL and API key.
- [ ] Add tests that model trace records preserve `model_provider: litellm_proxy`.
- [ ] Implement provider parsing in `src/novi_lab/cli.py`.
- [ ] Implement provider resolution in `src/novi_lab/model_providers.py`.
- [ ] Update configuration guide and YAML guide.
- [ ] Run `uv run --extra dev pytest`.
- [ ] Manually smoke test against a LiteLLM proxy before calling the integration complete.

## Decision Points Before Coding Beyond Phase B

- Should Novi use LiteLLM proxy only, or also embed LiteLLM SDK later?
- Should `litellm_proxy` default to `http://localhost:4000/v1`?
- Should `.novi/novi.yaml` store LiteLLM alias only, or also a local copy of upstream alias metadata for audit?
- Should `openai_responses` remain reserved until DeepAgents proves compatible with LiteLLM `/responses`?
- Should Novi add a `doctor model --ping` network check, or keep `doctor model` non-network for now?
