import atexit
import os
import shutil
import socket
import subprocess
import time
from pathlib import Path
from urllib.parse import urlparse

from .store import require_workspace, update_project_config, utc_now, write_yaml


_PROCESSES = []


def litellm_config_path(root):
    return require_workspace(root) / "litellm" / "config.yaml"


def litellm_start_command(root, port=4000):
    executable = os.environ.get("NOVI_LITELLM_BIN", "litellm")
    return [executable, "--config", str(litellm_config_path(root)), "--port", str(port)]


def write_litellm_proxy_config(
    root,
    model_name,
    upstream_model,
    upstream_api_key_env,
    upstream_base_url=None,
    proxy_api_key_env="LITELLM_PROXY_API_KEY",
    port=4000,
    api_shape="responses",
):
    if "/" not in upstream_model:
        upstream_model = f"openai/{upstream_model}"
    litellm_params = {
        "model": upstream_model,
        "api_key": f"os.environ/{upstream_api_key_env}",
    }
    if upstream_base_url:
        litellm_params["api_base"] = upstream_base_url
    path = litellm_config_path(root)
    config = {
        "model_list": [
            {
                "model_name": model_name,
                "litellm_params": litellm_params,
            }
        ],
        "general_settings": {
            "master_key": f"os.environ/{proxy_api_key_env}",
        },
    }
    write_yaml(path, config)
    update_project_config(
        root,
        model={
            "provider": "litellm_proxy",
            "model": model_name,
            "base_url": f"http://localhost:{port}/v1",
            "api_key": f"os.environ/{proxy_api_key_env}",
            "api_shape": api_shape,
            "auto_start": True,
        },
    )
    return path


def _parsed_host_port(base_url):
    parsed = urlparse(base_url or "")
    if not parsed.hostname:
        return None, None
    if parsed.port:
        return parsed.hostname, parsed.port
    if parsed.scheme == "https":
        return parsed.hostname, 443
    return parsed.hostname, 80


def _is_port_open(host, port):
    if not host or not port:
        return False
    try:
        with socket.create_connection((host, port), timeout=0.1):
            return True
    except OSError:
        return False


def _terminate_processes():
    for process in _PROCESSES:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()


atexit.register(_terminate_processes)


def ensure_litellm_proxy(root, model_config):
    if not model_config.get("auto_start", True):
        return False
    base_url = model_config.get("base_url") or "http://localhost:4000/v1"
    host, port = _parsed_host_port(base_url)
    if not os.environ.get("NOVI_LITELLM_FORCE_START") and _is_port_open(host, port):
        return False
    if not litellm_config_path(root).exists():
        raise RuntimeError("LiteLLM proxy config not found. Run `novi litellm init` first.")
    if not shutil.which(litellm_start_command(root, port=port or 4000)[0]):
        raise RuntimeError("LiteLLM executable not found. Install with `uv sync --extra litellm`.")
    command = litellm_start_command(root, port=port or 4000)
    write_yaml(
        require_workspace(root) / "litellm" / "last_start.yaml",
        {
            "started_at": utc_now(),
            "mode": "auto",
            "command": command,
            "base_url": base_url,
        },
    )
    process = subprocess.Popen(
        command,
        cwd=Path(root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        process.wait(timeout=0.05)
    except subprocess.TimeoutExpired:
        pass
    _PROCESSES.append(process)
    for _ in range(75):
        if process.poll() is not None:
            break
        if _is_port_open(host, port):
            return True
        time.sleep(0.2)
    if process.poll() is not None:
        if process.returncode == 0:
            return True
        raise RuntimeError("LiteLLM proxy exited before accepting connections.")
    return True


def run_litellm_proxy(root, port=4000):
    if not litellm_config_path(root).exists():
        raise RuntimeError("LiteLLM proxy config not found. Run `novi litellm init` first.")
    command = litellm_start_command(root, port=port)
    if not shutil.which(command[0]):
        raise RuntimeError("LiteLLM executable not found. Install with `uv sync --extra litellm`.")
    return subprocess.run(command, cwd=Path(root)).returncode
