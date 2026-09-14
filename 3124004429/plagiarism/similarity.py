"""Similarity calculation for the first, baseline implementation."""

from difflib import SequenceMatcher

from plagiarism.normalization import normalize_text


def calculate_similarity(original_text: str, candidate_text: str) -> float:
    """Return the similarity of two documents as a value in ``[0.0, 1.0]``."""

    original = normalize_text(original_text)
    candidate = normalize_text(candidate_text)

    if not original or not candidate:
        return 0.0
    if original == candidate:
        return 1.0

    matcher = SequenceMatcher(None, original, candidate, autojunk=False)
    return float(matcher.ratio())

