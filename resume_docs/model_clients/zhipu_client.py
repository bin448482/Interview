"""Zhipu GLM client."""
from __future__ import annotations

import os
from typing import Dict

import requests

from . import base


class ZhipuClient(base.BaseModelClient):
    def __init__(self, api_key: str | None = None, base_url: str | None = None, timeout: int = 60) -> None:
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY")
        self.base_url = (base_url or "https://open.bigmodel.cn/api/paas/v4").rstrip("/")
        self.timeout = timeout

    def send_prompt(self, model_name: str, prompt: str, **kwargs) -> Dict[str, object]:
        if not self.api_key:
            raise base.ModelInvocationError("ZHIPU_API_KEY is not configured")
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are a bilingual resume writer."},
                {"role": "user", "content": prompt},
            ],
            "temperature": kwargs.get("temperature", 0.3),
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        if response.status_code >= 400:
            raise base.ModelInvocationError(
                f"Zhipu API error {response.status_code}: {response.text[:200]}"
            )
        return response.json()
