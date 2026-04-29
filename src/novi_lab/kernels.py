def require_deepagents_kernel():
    try:
        import deepagents  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "DeepAgents kernel requires optional dependency. "
            "Install with `uv sync --extra deepagents` and run on Python 3.11+."
        ) from exc
    raise RuntimeError("DeepAgents kernel adapter is not implemented yet.")


def validate_kernel(kernel):
    if kernel == "simple":
        return
    if kernel == "deepagents":
        require_deepagents_kernel()
        return
    raise RuntimeError(f"Unknown kernel: {kernel}")
