"""Resume document generation toolkit."""

from importlib import resources
from pathlib import Path

from .role_filter import RoleFilter

__all__ = ["package_path", "RoleFilter"]


def package_path() -> Path:
    """Return the root path of the resume_docs package."""
    return Path(resources.files(__name__))
