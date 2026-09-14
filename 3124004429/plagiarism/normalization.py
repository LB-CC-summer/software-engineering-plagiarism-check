"""Text normalization helpers."""

import unicodedata


def normalize_text(text: str) -> str:
    """Return a comparison-friendly representation of *text*.

    Unicode compatibility characters are normalized, letters are case-folded,
    and whitespace or punctuation is removed.  The resulting representation is
    intentionally language-independent so that Chinese text can be compared
    without relying on a third-party word segmenter.
    """

    if not text:
        return ""

    normalized = unicodedata.normalize("NFKC", text).casefold()
    return "".join(character for character in normalized if character.isalnum())

