"""Tests for the weighted n-gram similarity algorithm."""

from collections import Counter
from itertools import permutations

import pytest

from plagiarism.similarity import (
    SimilarityConfig,
    _cosine_similarity,
    calculate_similarity,
    count_ngrams,
)


def test_identical_texts_have_similarity_one() -> None:
    assert calculate_similarity("今天是星期天", "今天是星期天") == 1.0


@pytest.mark.parametrize("texts", [("", ""), ("", "非空文本"), ("非空文本", "")])
def test_empty_text_has_similarity_zero(texts: tuple[str, str]) -> None:
    assert calculate_similarity(*texts) == 0.0


def test_completely_different_texts_have_low_similarity() -> None:
    score = calculate_similarity(
        "今天是星期天，天气晴朗。",
        "机器学习模型可以从数据中学习规律。",
    )

    assert score < 0.2


def test_added_text_keeps_high_similarity() -> None:
    original = "设计一个论文查重算法，输出原文与抄袭版的重复率。"
    candidate = original + "系统还需要处理错误输入和文件读写异常。"

    assert calculate_similarity(original, candidate) >= 0.65


def test_deleted_text_keeps_high_similarity() -> None:
    original = "设计一个论文查重算法，输出原文与抄袭版的重复率。"
    candidate = "设计一个论文查重算法，输出重复率。"

    assert calculate_similarity(original, candidate) >= 0.65


def test_reordered_text_keeps_meaningful_similarity() -> None:
    original = "今天是星期天天气晴今天晚上我要去看电影"
    candidate = "今晚我要去看电影今天是星期天天气晴"

    assert calculate_similarity(original, candidate) > 0.4


def test_similarity_is_symmetric() -> None:
    left = "软件工程要求使用源代码管理工具。"
    right = "软件工程课程要求使用源代码管理。"

    assert calculate_similarity(left, right) == pytest.approx(
        calculate_similarity(right, left)
    )


def test_synonym_example_is_detected_as_similar() -> None:
    original = "今天是星期天，天气晴，今天晚上我要去看电影。"
    candidate = "今天是周天，天气晴朗，我晚上要去看电影。"

    assert calculate_similarity(original, candidate) > 0.5


def test_all_scores_are_in_valid_range() -> None:
    samples = [
        "短文本",
        "中文文本与 English words 混合。",
        "".join(str(index % 10) for index in range(200)),
    ]

    for left, right in permutations(samples, 2):
        assert 0.0 <= calculate_similarity(left, right) <= 1.0


def test_count_ngrams_handles_short_input() -> None:
    assert count_ngrams("中", 2) == {}


def test_count_ngrams_rejects_non_positive_size() -> None:
    with pytest.raises(ValueError, match="positive"):
        count_ngrams("文本", 0)


def test_custom_configuration_is_respected() -> None:
    config = SimilarityConfig(ngram_weights=((1, 1.0),))

    assert calculate_similarity("甲乙丙", "甲乙丁", config=config) > 0.0


def test_cosine_similarity_handles_empty_or_zero_vectors() -> None:
    assert _cosine_similarity(Counter(), Counter({"a": 1})) == 0.0
    assert _cosine_similarity(Counter({"a": 0}), Counter({"a": 0})) == 0.0


def test_zero_weight_ngrams_are_ignored() -> None:
    config = SimilarityConfig(ngram_weights=((1, 0.0), (2, 0.0)))

    assert calculate_similarity("甲乙丙", "甲乙丁", config=config) == 0.0


def test_zero_weight_is_followed_by_positive_weight() -> None:
    config = SimilarityConfig(ngram_weights=((1, 0.0), (2, 1.0)))

    assert calculate_similarity("甲乙丙", "甲乙丁", config=config) > 0.0
