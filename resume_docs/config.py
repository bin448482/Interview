"""Configuration helpers for resume document generation."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional

import yaml

from . import constants


@dataclass
class GenerationConfig:
    template: str = constants.DEFAULT_THEME
    locale: str = constants.DEFAULT_LOCALE
    include_contact: bool = False
    models: List[str] = field(default_factory=list)
    prompt_use_case: str = constants.DEFAULT_USE_CASE
    output_dir: Path = constants.DEFAULT_OUTPUT_DIR
    dry_run: bool = False
    skip_docx: bool = False
    skip_prompts: bool = False
    invoke_models: bool = False

    @property
    def output_dir_path(self) -> Path:
        return Path(self.output_dir)

    def validate(self) -> None:
        if self.template not in constants.THEMES:
            raise ValueError(f"Unknown template '{self.template}'. Options: {sorted(constants.THEMES)}")
        if self.locale not in constants.SUPPORTED_LOCALES:
            raise ValueError(f"Unsupported locale '{self.locale}'. Options: {constants.SUPPORTED_LOCALES}")


def load_config_file(path: Optional[Path]) -> dict:
    if not path:
        return {}
    config_path = Path(path)
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config file {config_path} must contain a YAML mapping")
    return data


def create_config(
    cli_args: Optional[dict] = None,
    config_file: Optional[Path] = None,
) -> GenerationConfig:
    base = load_config_file(config_file)
    merged = {**base, **(cli_args or {})}
    config = GenerationConfig(
        template=merged.get("template", constants.DEFAULT_THEME),
        locale=merged.get("locale", constants.DEFAULT_LOCALE),
        include_contact=bool(merged.get("include_contact", False)),
        models=list(merged.get("models", [])),
        prompt_use_case=merged.get("prompt_use_case", constants.DEFAULT_USE_CASE),
        output_dir=Path(merged.get("output_dir", constants.DEFAULT_OUTPUT_DIR)),
        dry_run=bool(merged.get("dry_run", False)),
        skip_docx=bool(merged.get("skip_docx", False)),
        skip_prompts=bool(merged.get("skip_prompts", False)),
        invoke_models=bool(merged.get("invoke_models", False)),
    )
    config.validate()
    return config
