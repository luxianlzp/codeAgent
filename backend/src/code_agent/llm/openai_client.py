from __future__ import annotations

import os

from code_agent.core.messages import Message


class OpenAICompatibleClient:
    def __init__(self, model: str, base_url: str) -> None:
        try:
            from openai import OpenAI
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "The openai package is not installed. Install backend dependencies first."
            ) from exc

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        if api_key == "your_api_key_here" or "your_api" in api_key:
            raise RuntimeError("OPENAI_API_KEY still contains the example placeholder value.")

        self._client = OpenAI(api_key=api_key, base_url=base_url)
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
