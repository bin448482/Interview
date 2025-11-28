"""Base client definition."""
from __future__ import annotations

from typing import Dict


class ModelInvocationError(RuntimeError):
    """Raised when a downstream model invocation fails."""


class BaseModelClient:
    def send_prompt(self, model_name: str, prompt: str, **kwargs) -> Dict[str, object]:  # pragma: no cover - interface
        raise NotImplementedError
