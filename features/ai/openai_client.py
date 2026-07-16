"""Optional OpenAI GPT backend for TabX assistant.

The key is intentionally read from the environment. Do not persist API keys in
TabX local state until a secure keychain-backed storage path exists.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


class OpenAIClientError(RuntimeError):
    """Raised when the GPT backend cannot produce a response."""


class OpenAIGptClient:
    """Small stdlib-only wrapper around the OpenAI Responses API."""

    endpoint = "https://api.openai.com/v1/responses"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "").strip()
        self.model = (model or os.environ.get("OPENAI_MODEL", "gpt-5-mini")).strip()

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def ask(self, prompt: str, page_context: str = "") -> str:
        if not self.is_configured():
            raise OpenAIClientError("OPENAI_API_KEY tanımlı değil.")
        prompt = prompt.strip()
        if not prompt:
            raise OpenAIClientError("Boş istek gönderilemez.")

        input_items = [
            {
                "role": "developer",
                "content": (
                    "Sen TabX tarayıcısının sade, kısa ve kullanıcının kontrolünü "
                    "öne alan sayfa yardımcısısın. Varsayım üretme; verilen bağlam "
                    "yetmiyorsa bunu açıkça söyle. Yanıtı Türkçe ver."
                ),
            },
            {"role": "user", "content": self._compose_user_input(prompt, page_context)},
        ]
        payload = {
            "model": self.model,
            "input": input_items,
            "max_output_tokens": 700,
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise OpenAIClientError(f"OpenAI API hatası ({exc.code}): {detail[:320]}") from exc
        except urllib.error.URLError as exc:
            raise OpenAIClientError(f"OpenAI bağlantısı kurulamadı: {exc.reason}") from exc
        except TimeoutError as exc:
            raise OpenAIClientError("OpenAI isteği zaman aşımına uğradı.") from exc

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            raise OpenAIClientError("OpenAI yanıtı JSON olarak okunamadı.") from exc
        text = self._extract_text(parsed)
        if not text:
            raise OpenAIClientError("OpenAI yanıtında metin bulunamadı.")
        return text.strip()

    def _compose_user_input(self, prompt: str, page_context: str) -> str:
        context = page_context.strip()
        if not context:
            return prompt
        return f"Sayfa bağlamı:\n{context[:7000]}\n\nKullanıcı isteği:\n{prompt}"

    def _extract_text(self, response: dict) -> str:
        output_text = response.get("output_text")
        if isinstance(output_text, str):
            return output_text
        chunks: list[str] = []
        for item in response.get("output", []):
            if not isinstance(item, dict):
                continue
            for content in item.get("content", []):
                if not isinstance(content, dict):
                    continue
                text = content.get("text")
                if isinstance(text, str):
                    chunks.append(text)
        return "\n".join(chunks)
