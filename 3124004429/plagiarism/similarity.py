"""Similarity calculation based on multi-order character n-grams."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from math import sqrt

from plagiarism.normalization import normalize_text


@dataclass(frozen=True)
class SimilarityConfig:
    """Configuration for weighted n-gram cosine similarity."""

    ngram_weights: tuple[tuple[int, float], ...] = (
        (1, 0.15),
        (2, 0.45),
        (3, 0.40),
    )


DEFAULT_CONFIG = SimilarityConfig()


def count_ngrams(text: str, n: int) -> Counter[str]:
    """Count overlapping character n-grams in *text*."""

    if n <= 0:
        raise ValueError("n must be positive")
    if len(text) < n:
        return Counter()
    return Counter(text[index : index + n] for index in range(len(text) - n + 1))


def _cosine_similarity(
    left: Counter[str],
    right: Counter[str],
) -> float:
    """Compute cosine similarity between two sparse count vectors."""

    if not left or not right:
        return 0.0
    if len(left) > len(right):
        left, right = right, left

    dot_product = sum(count * right.get(ngram, 0) for ngram, count in left.items())
    left_norm = sqrt(sum(count * count for count in left.values()))
    right_norm = sqrt(sum(count * count for count in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return dot_product / (left_norm * right_norm)


def _iter_available_ngrams(
    left_length: int,
    right_length: int,
    configured_ngrams: Iterable[tuple[int, float]],
) -> Iterable[tuple[int, float]]:
    """Yield n-gram orders that both documents can produce."""

    shortest_length = min(left_length, right_length)
    for ngram_size, weight in configured_ngrams:
        if weight > 0 and shortest_length >= ngram_size:
            yield ngram_size, weight


def calculate_similarity(
    original_text: str,
    candidate_text: str,
    config: SimilarityConfig = DEFAULT_CONFIG,
) -> float:
    """Return the similarity of two documents as a value in ``[0.0, 1.0]``.

    The score combines unigram, bigram, and trigram cosine similarities.
    Unigrams make the algorithm robust to insertions and deletions, while
    bigrams and trigrams preserve enough ordering information to detect text
    that has merely been shuffled.
    """

    original = normalize_text(original_text)
    candidate = normalize_text(candidate_text)

    if not original or not candidate:
        return 0.0
    if original == candidate:
        return 1.0

    order_weights = list(
        _iter_available_ngrams(
            len(original),
            len(candidate),
            config.ngram_weights,
        )
    )
    if not order_weights:
        return 0.0

    weighted_score = 0.0
    total_weight = 0.0
    for ngram_size, weight in order_weights:
        original_counts = count_ngrams(original, ngram_size)
        candidate_counts = count_ngrams(candidate, ngram_size)
        weighted_score += weight * _cosine_similarity(
            original_counts,
            candidate_counts,
        )
        total_weight += weight

    score = weighted_score / total_weight
    return max(0.0, min(1.0, score))
