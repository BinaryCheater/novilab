import os


def _env(name, fallback=None):
    value = os.environ.get(name)
    if value:
        return value
    return fallback


def model_profile_from_participant(participant):
    model_profile = participant.get("model_profile") or "openai:gpt-4.1-mini"
    if model_profile == "deterministic-local":
        return _env("NOVI_MODEL", "openai:gpt-4.1-mini")
    return model_profile


def _strip_openai_provider(model_profile):
    if model_profile.startswith("openai:"):
        return model_profile.split(":", 1)[1]
    return model_profile


def resolve_deepagents_model(participant):
    provider = _env("NOVI_MODEL_PROVIDER", "deepagents_default")
    model_profile = model_profile_from_participant(participant)

    if provider in {"deepagents_default", "openai_responses"}:
        return model_profile, {
            "model_provider": provider,
            "model_profile": model_profile,
            "model_base_url": None,
        }

    if provider in {"openai_chat", "openai_compatible_chat", "siliconflow"}:
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as exc:
            raise RuntimeError(
                "OpenAI-compatible chat provider requires `langchain-openai`. "
                "Install with `uv sync --extra deepagents`."
            ) from exc

        model_name = _strip_openai_provider(model_profile)
        base_url = _env("NOVI_API_BASE", _env("OPENAI_API_BASE"))
        api_key = _env("NOVI_API_KEY", _env("OPENAI_API_KEY"))
        if not base_url:
            raise RuntimeError("OpenAI-compatible chat provider requires NOVI_API_BASE or OPENAI_API_BASE.")
        if not api_key:
            raise RuntimeError("OpenAI-compatible chat provider requires NOVI_API_KEY or OPENAI_API_KEY.")
        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            use_responses_api=False,
        ), {
            "model_provider": "openai_chat",
            "model_profile": model_name,
            "model_base_url": base_url,
        }

    raise RuntimeError(f"Unknown model provider: {provider}")
