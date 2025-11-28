"""Centralized constants for resume generation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
LATEST_RESUMES_DIR = REPO_ROOT / "latest_resumes"
ROLE_GUIDELINE_PATH = REPO_ROOT / ".design_docs" / "role_mapping_guidelines.md"
DOC_TEMPLATE_DIR = REPO_ROOT / "templates" / "docx"
PROMPT_TEMPLATE_DIR = REPO_ROOT / "templates" / "prompts"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "output"
ARTIFACTS_DIR = REPO_ROOT / "artifacts"

SUPPORTED_LOCALES = ("zh-CN", "en-US")
DEFAULT_LOCALE = "zh-CN"
DEFAULT_THEME = "modern"
DEFAULT_USE_CASE = "summary"

ROLE_PERSPECTIVE_ALLOWED = {"developer", "architect", "project_manager", "product_owner", "hybrid"}
DECISION_ACCOUNTABILITY_ALLOWED = {
    "delivery_owner",
    "technical_strategy",
    "people_management",
    "hands_on_build",
    "commercial_strategy",
    "risk_governance",
}
RESPONSIBILITY_FOCUS_ALLOWED = {
    "planning",
    "architecture",
    "implementation",
    "operations",
    "commercialization",
    "stakeholder_management",
    "compliance",
}
BUDGET_LEVEL_ALLOWED = {"lt_100k", "bt_100k_1m", "gt_1m"}


@dataclass(frozen=True)
class ThemeConfig:
    name: str
    font_family: str
    accent_rgb: Tuple[int, int, int]
    heading_color_rgb: Tuple[int, int, int]
    body_font_size: int = 11
    heading_font_size: int = 16
    subheading_font_size: int = 12
    sidebar_width_ratio: float = 0.32  # used for multi-column layout heuristics


THEMES: Dict[str, ThemeConfig] = {
    "modern": ThemeConfig(
        name="modern",
        font_family="Inter",
        accent_rgb=(32, 70, 140),
        heading_color_rgb=(32, 32, 32),
        body_font_size=11,
        heading_font_size=20,
        subheading_font_size=12,
        sidebar_width_ratio=0.33,
    ),
    "minimal": ThemeConfig(
        name="minimal",
        font_family="Source Sans 3",
        accent_rgb=(0, 0, 0),
        heading_color_rgb=(60, 60, 60),
        body_font_size=11,
        heading_font_size=18,
        subheading_font_size=12,
        sidebar_width_ratio=0.0,
    ),
}
