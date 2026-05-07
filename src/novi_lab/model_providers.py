import os

from .litellm_proxy import ensure_litellm_proxy
from .store import project_config


def _env(name, fallback=None):
    value = os.environ.get(name)
    if value:
        return value
    return fallback


def _resolve_secret(value):
    if isinstance(value, str) and value.startswith("os.environ/"):
        return os.environ.get(value.split("/", 1)[1])
    return value


def _project_model_config(root):
    return project_config(root).get("model", {}) or {}


def model_profile_from_participant(root, participant):
    config = _project_model_config(root)
    model_profile = participant.get("model_profile") or "openai:gpt-4.1-mini"
    if model_profile == "deterministic-local":
        return config.get("model") or _env("NOVI_MODEL", "openai:gpt-4.1-mini")
    return model_profile


def _strip_openai_provider(model_profile):
    if model_profile.startswith("openai:"):
        return model_profile.split(":", 1)[1]
    return model_profile


def configured_model_record(root, participant):
    config = _project_model_config(root)
    provider = config.get("provider") or _env("NOVI_MODEL_PROVIDER", "deepagents_default")
    model_profile = model_profile_from_participant(root, participant)
    if provider in {"openai_chat", "openai_compatible_chat", "siliconflow"}:
        return {
            "model_provider": "openai_chat",
            "model_profile": _strip_openai_provider(model_profile),
            "model_base_url": config.get("base_url") or _env("NOVI_API_BASE", _env("OPENAI_API_BASE")),
        }
    if provider == "openai_responses":
        return {
            "model_provider": "openai_responses",
            "model_profile": _strip_openai_provider(model_profile),
            "model_base_url": config.get("base_url") or _env("NOVI_API_BASE", _env("OPENAI_API_BASE")),
            "model_api_shape": "responses",
        }
    if provider == "litellm_proxy":
        return {
            "model_provider": "litellm_proxy",
            "model_profile": _strip_openai_provider(model_profile),
            "model_base_url": config.get("base_url") or _env("NOVI_API_BASE", "http://localhost:4000/v1"),
            "model_api_shape": config.get("api_shape", "responses"),
            "litellm_auto_start": bool(config.get("auto_start", True)),
        }
    return {
        "model_provider": provider,
        "model_profile": model_profile,
        "model_base_url": config.get("base_url") or _env("NOVI_API_BASE", _env("OPENAI_API_BASE")),
        "model_api_shape": config.get("api_shape"),
    }


def resolve_deepagents_model(root, participant):
    config = _project_model_config(root)
    provider = config.get("provider") or _env("NOVI_MODEL_PROVIDER", "deepagents_default")
    model_profile = model_profile_from_participant(root, participant)

    if provider == "deepagents_default":
        return model_profile, configured_model_record(root, participant)

    if provider in {"openai_chat", "openai_compatible_chat", "siliconflow", "litellm_proxy", "openai_responses"}:
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as exc:
            raise RuntimeError(
                "OpenAI-compatible chat provider requires `langchain-openai`. "
                "Install with `uv sync --extra deepagents`."
            ) from exc

        model_name = _strip_openai_provider(model_profile)
        base_url = config.get("base_url") or _env("NOVI_API_BASE", _env("OPENAI_API_BASE"))
        api_key = _resolve_secret(config.get("api_key")) or _env("NOVI_API_KEY", _env("OPENAI_API_KEY"))
        if provider == "litellm_proxy":
            base_url = base_url or "http://localhost:4000/v1"
            api_key = api_key or _env("LITELLM_PROXY_API_KEY")
            ensure_litellm_proxy(root, config)
        if not base_url:
            raise RuntimeError("OpenAI-compatible chat provider requires NOVI_API_BASE or OPENAI_API_BASE.")
        if not api_key:
            raise RuntimeError("OpenAI-compatible chat provider requires NOVI_API_KEY or OPENAI_API_KEY.")
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            use_responses_api=provider == "openai_responses" or (provider == "litellm_proxy" and config.get("api_shape", "responses") == "responses"),
        ), configured_model_record(root, participant)

    raise RuntimeError(f"Unknown model provider: {provider}")
