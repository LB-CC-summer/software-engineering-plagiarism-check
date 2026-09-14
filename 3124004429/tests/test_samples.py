"""Integration tests against the provided course samples."""

from pathlib import Path
from time import perf_counter

import pytest

from plagiarism.io_utils import read_document
from plagiarism.similarity import calculate_similarity

SAMPLES = Path(__file__).parents[1] / "samples"


@pytest.mark.parametrize(
    ("name", "lower_bound", "upper_bound"),
    [
        ("orig_0.8_add.txt", 0.75, 0.90),
        ("orig_0.8_del.txt", 0.75, 0.90),
        ("orig_0.8_dis_1.txt", 0.90, 1.00),
        ("orig_0.8_dis_10.txt", 0.78, 0.92),
        ("orig_0.8_dis_15.txt", 0.55, 0.72),
    ],
)
def test_sample_score_is_in_expected_range(
    name: str,
    lower_bound: float,
    upper_bound: float,
) -> None:
    original = read_document(SAMPLES / "orig.txt")
    candidate = read_document(SAMPLES / name)

    score = calculate_similarity(original, candidate)

    assert lower_bound <= score <= upper_bound


def test_sample_calculation_is_fast() -> None:
    original = read_document(SAMPLES / "orig.txt")
    candidate = read_document(SAMPLES / "orig_0.8_dis_15.txt")

    started_at = perf_counter()
    calculate_similarity(original, candidate)
    elapsed = perf_counter() - started_at

    assert elapsed < 1.0
