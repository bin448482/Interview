"""Load runtime configuration from YAML and apply environment shims."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml

DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent / "latest_resumes" / "runtime_config.yaml"
)


def _set_env_var(key: str, value: Any) -> None:
    """Set environment variable ensuring string conversion."""
    if value is None:
        return
    os.environ[key] = str(value)


def apply_env(config: Dict[str, Any]) -> None:
    """Map provider config to standard environment variables."""
    openai_cfg = config.get("openai", {})
    _set_env_var("OPENAI_API_KEY", openai_cfg.get("api_key"))
    _set_env_var("OPENAI_BASE_URL", openai_cfg.get("base_url"))

    zhipu_cfg = config.get("zhipu", {})
    _set_env_var("ZHIPU_API_KEY", zhipu_cfg.get("api_key"))

    ollama_cfg = config.get("ollama", {})
    _set_env_var("OLLAMA_HOST", ollama_cfg.get("host"))
    _set_env_var("OLLAMA_BASE_URL", ollama_cfg.get("host"))
    _set_env_var("OLLAMA_MODEL", ollama_cfg.get("model"))

    extra_env = config.get("env", {})
    for key, value in extra_env.items():
        _set_env_var(key, value)


def load_runtime_config(path: Path | str | None = None, apply: bool = True) -> Dict[str, Any]:
    """Load YAML config and optionally apply environment overrides."""
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not config_path.exists():
        return {}

    with config_path.open("r", encoding="utf-8") as fh:
        config: Dict[str, Any] = yaml.safe_load(fh) or {}

    if apply:
        apply_env(config)
    return config
