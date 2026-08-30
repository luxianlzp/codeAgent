from __future__ import annotations

import html
import re


_FENCE_RE = re.compile(r"```([A-Za-z0-9_+.-]*)\n(.*?)```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
_BOLD_RE = re.compile(r"\*\*([^*\n]+)\*\*")

_KEYWORDS = {
    "python": {
        "False", "None", "True", "and", "as", "assert", "async", "await", "break", "class", "continue",
        "def", "del", "elif", "else", "except", "finally", "for", "from", "global", "if", "import", "in",
        "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield",
    },
    "javascript": {
        "async", "await", "break", "case", "catch", "class", "const", "continue", "default", "else",
        "export", "for", "function", "if", "import", "let", "new", "return", "switch", "throw", "try",
        "var", "while",
    },
}
_KEYWORDS["js"] = _KEYWORDS["javascript"]
_KEYWORDS["ts"] = _KEYWORDS["javascript"] | {"interface", "type", "implements", "readonly"}
_KEYWORDS["typescript"] = _KEYWORDS["ts"]


def render_final_markdown_html(markdown: str) -> str:
    """Render final agent output as compact Qt RichText with highlighted fenced code."""
    parts: list[str] = []
    position = 0
    for match in _FENCE_RE.finditer(markdown):
        parts.append(_render_markdown_text(markdown[position:match.start()]))
        parts.append(_render_code_block(match.group(2).rstrip("\n"), match.group(1).strip().lower()))
        position = match.end()
    parts.append(_render_markdown_text(markdown[position:]))
    return "<div>" + "".join(parts) + "</div>"


def _render_markdown_text(text: str) -> str:
    blocks: list[str] = []
    pending_list: list[str] = []

    def flush_list() -> None:
        if pending_list:
            blocks.append("<ul>" + "".join(pending_list) + "</ul>")
            pending_list.clear()

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line:
            flush_list()
            blocks.append("<br/>")
            continue
        if line.startswith("### "):
            flush_list()
            blocks.append(f"<h3>{_render_inline(line[4:])}</h3>")
            continue
        if line.startswith("## "):
            flush_list()
            blocks.append(f"<h2>{_render_inline(line[3:])}</h2>")
            continue
        if line.startswith("# "):
            flush_list()
            blocks.append(f"<h1>{_render_inline(line[2:])}</h1>")
            continue
        if line.startswith("- ") or line.startswith("* "):
            pending_list.append(f"<li>{_render_inline(line[2:])}</li>")
            continue
        flush_list()
        blocks.append(f"<p>{_render_inline(line)}</p>")
    flush_list()
    return "".join(blocks)


def _render_inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = _INLINE_CODE_RE.sub(
        r'<code style="color:#7c3aed; background-color:#f3f4f6;">\1</code>',
        escaped,
    )
    escaped = _BOLD_RE.sub(r"<b>\1</b>", escaped)
    return escaped


def _render_code_block(code: str, language: str) -> str:
    highlighted = _highlight_code(code, language)
    language_badge = f'<span style="color:#8b93a1;">{html.escape(language)}</span><br/>' if language else ""
    return (
        '<pre style="background-color:#f6f8fa; color:#111827; border:1px solid #dfe3ea; '
        'font-family:Courier New; font-size:12px;">'
        f"{language_badge}{highlighted}"
        "</pre>"
    )


def _highlight_code(code: str, language: str) -> str:
    if language in {"html", "xml", "qml"}:
        return _highlight_markup(code)
    if language in {"css"}:
        return _highlight_css(code)
    return _highlight_keyword_language(code, language)


def _highlight_keyword_language(code: str, language: str) -> str:
    keywords = _KEYWORDS.get(language, set())
    token_re = re.compile(r"(#[^\n]*|//[^\n]*|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|\b\d+(?:\.\d+)?\b|\b[A-Za-z_][A-Za-z0-9_]*\b)")
    result: list[str] = []
    position = 0
    for match in token_re.finditer(code):
        result.append(html.escape(code[position:match.start()]))
        token = match.group(0)
        escaped = html.escape(token)
        if token.startswith(("#", "//")):
            result.append(f'<span style="color:#6b7280;">{escaped}</span>')
        elif token.startswith(("'", '"')):
            result.append(f'<span style="color:#047857;">{escaped}</span>')
        elif token[0].isdigit():
            result.append(f'<span style="color:#b45309;">{escaped}</span>')
        elif token in keywords:
            result.append(f'<span style="color:#1d4ed8; font-weight:600;">{escaped}</span>')
        else:
            result.append(escaped)
        position = match.end()
    result.append(html.escape(code[position:]))
    return "".join(result)


def _highlight_markup(code: str) -> str:
    escaped = html.escape(code)
    escaped = re.sub(r"(&lt;/?)([A-Za-z][\w:-]*)", r'\1<span style="color:#1d4ed8;">\2</span>', escaped)
    escaped = re.sub(r"([\w:-]+)(=)", r'<span style="color:#7c3aed;">\1</span>\2', escaped)
    escaped = re.sub(r"(&quot;.*?&quot;)", r'<span style="color:#047857;">\1</span>', escaped)
    return escaped


def _highlight_css(code: str) -> str:
    escaped = html.escape(code)
    escaped = re.sub(r"([.#]?[A-Za-z_-][\w-]*)(\s*\{)", r'<span style="color:#1d4ed8;">\1</span>\2', escaped)
    escaped = re.sub(r"([A-Za-z-]+)(\s*:)", r'<span style="color:#7c3aed;">\1</span>\2', escaped)
    escaped = re.sub(r"(#[0-9A-Fa-f]{3,8}|\b\d+(?:px|rem|em|%)\b)", r'<span style="color:#b45309;">\1</span>', escaped)
    return escaped
