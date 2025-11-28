"""Local Ollama client."""
from __future__ import annotations

import os
from typing import Dict

import requests

from . import base


class OllamaClient(base.BaseModelClient):
    def __init__(self, host: str | None = None, timeout: int = 60) -> None:
        self.host = (host or os.getenv("OLLAMA_HOST") or "http://localhost:11434").rstrip("/")
        self.timeout = timeout

    def send_prompt(self, model_name: str, prompt: str, **kwargs) -> Dict[str, object]:
        url = f"{self.host}/api/generate"
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
        }
        response = requests.post(url, json=payload, timeout=self.timeout)
        if response.status_code >= 400:
            raise base.ModelInvocationError(
                f"Ollama error {response.status_code}: {response.text[:200]}"
            )
        return response.json()
