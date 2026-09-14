"""Text normalization helpers."""

from __future__ import annotations

import re
import unicodedata
from html import unescape
from html.parser import HTMLParser

_GITHUB_BLOB_ROW_RE = re.compile(
    r'<td[^>]*class="[^"]*blob-code[^"]*js-file-line[^"]*"[^>]*>'
    r"(?P<body>.*?)</td>",
    flags=re.IGNORECASE | re.DOTALL,
)
_TAG_RE = re.compile(r"<[^>]+>")
_HTML_MARKERS = ("<!doctype html", "<html")
_SKIPPED_TAGS = {"script", "style", "noscript"}
_BLOCK_TAGS = {
    "br",
    "div",
    "li",
    "p",
    "pre",
    "table",
    "td",
    "th",
    "tr",
}


class _VisibleTextParser(HTMLParser):
    """Small HTML parser that keeps visible text and ignores scripts/styles."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skipped_depth = 0

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        del attrs
        lowered = tag.lower()
        if lowered in _SKIPPED_TAGS:
            self._skipped_depth += 1
        elif lowered in _BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered in _SKIPPED_TAGS and self._skipped_depth:
            self._skipped_depth -= 1
        elif lowered in _BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skipped_depth:
            self._parts.append(data)

    def text(self) -> str:
        return "".join(self._parts)


def extract_embedded_text(text: str) -> str:
    """Extract article text from a page saved as HTML, when necessary.

    Some course samples are browser saves of GitHub text views.  Their actual
    article content is stored in table cells with the class
    ``blob-code blob-code-inner js-file-line``.  Extracting those rows avoids
    comparing the article with navigation menus and JavaScript source code.
    """

    prefix = text[:4096].lower()
    if not any(marker in prefix for marker in _HTML_MARKERS):
        return text

    rows = _GITHUB_BLOB_ROW_RE.findall(text)
    if rows:
        return "\n".join(
            unescape(_TAG_RE.sub("", row))
            for row in rows
        )

    parser = _VisibleTextParser()
    parser.feed(text)
    parser.close()
    return parser.text()


def normalize_text(text: str) -> str:
    """Return a comparison-friendly representation of *text*.

    Unicode compatibility characters are normalized, letters are case-folded,
    and whitespace or punctuation is removed.  The resulting representation is
    intentionally language-independent so that Chinese text can be compared
    without relying on a third-party word segmenter.
    """

    if not text:
        return ""

    source = extract_embedded_text(text)
    normalized = unicodedata.normalize("NFKC", source).casefold()
    return "".join(character for character in normalized if character.isalnum())
