from __future__ import annotations

from types import SimpleNamespace

from code_agent.llm.openai_client import _stream_chunk_content


def test_stream_chunk_content_ignores_empty_choices() -> None:
    chunk = SimpleNamespace(choices=[])

    assert _stream_chunk_content(chunk) is None


def test_stream_chunk_content_reads_delta_content() -> None:
    chunk = SimpleNamespace(
        choices=[
            SimpleNamespace(
                delta=SimpleNamespace(content="hello"),
            )
        ]
    )

    assert _stream_chunk_content(chunk) == "hello"

