"""Helpers for resolving per-project LLM polishing roles."""
from __future__ import annotations

from typing import Optional

from .models import Project
from .role_config import ROLE_FILTERS


def resolve_polish_role(global_role: Optional[str], project: Project) -> Optional[str]:
    """Decide which role (if any) to use when polishing a project with LLM.

    The resolution strategy follows the project-level role design:
    - Prefer a global role that is explicitly compatible with the project.
    - Fall back to the project's primary role if specified.
    - As a last resort, use the global role even if the project has no hints.
    - If neither provides a valid hint, return None to trigger a non-role-aware prompt.
    """
    allowed_roles = set(ROLE_FILTERS.keys())

    # 1. Normalize inputs
    if global_role not in allowed_roles:
        global_role = None

    primary = project.llm_primary_role if project.llm_primary_role in allowed_roles else None
    secondary = [r for r in (project.llm_secondary_roles or []) if r in allowed_roles]

    # 2. Prefer a compatible combination of overall role + project hints
    if global_role:
        if primary == global_role:
            return global_role
        if global_role in secondary:
            return global_role

    # 3. Fall back to the project's own primary perspective
    if primary:
        return primary

    # 4. Then fall back to the overall role to keep resume tone roughly consistent
    if global_role:
        return global_role

    # 5. No hints at all: disable role-aware polishing for this project
    return None

