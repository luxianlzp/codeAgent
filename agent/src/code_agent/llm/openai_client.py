from __future__ import annotations

import os
from collections.abc import Iterator
from typing import Any

from code_agent.core.messages import Message


class OpenAICompatibleClient:
    def __init__(self, model: str, base_url: str, timeout_seconds: int = 60) -> None:
        try:
            from openai import OpenAI
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "The openai package is not installed. Install project dependencies first."
            ) from exc

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        if api_key == "your_api_key_here" or "your_api" in api_key:
            raise RuntimeError("OPENAI_API_KEY still contains the example placeholder value.")

        self._client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout_seconds)
        self._model = model

    def complete(self, messages: list[Message]) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[message.to_dict() for message in messages],
                temperature=0,
            )
        except Exception as exc:
            raise RuntimeError(f"Model API request failed: {exc}") from exc

        content = response.choices[0].message.content
        if content is None:
            raise RuntimeError("Model returned an empty message.")
        return content

    def stream_complete(self, messages: list[Message]) -> Iterator[str]:
        try:
            stream = self._client.chat.completions.create(
                model=self._model,
                messages=[message.to_dict() for message in messages],
                temperature=0,
                stream=True,
            )
            for chunk in stream:
                delta = _stream_chunk_content(chunk)
                if delta:
                    yield delta
        except Exception as exc:
            raise RuntimeError(f"Model API stream request failed: {exc}") from exc


def _stream_chunk_content(chunk: Any) -> str | None:
    choices = getattr(chunk, "choices", None) or []
    if not choices:
        return None
    choice = choices[0]
    delta_obj = getattr(choice, "delta", None)
    delta = getattr(delta_obj, "content", None)
    return delta if isinstance(delta, str) and delta else None
