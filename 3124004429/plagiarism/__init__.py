"""Core package for the plagiarism-rate checker."""

from plagiarism.similarity import DEFAULT_CONFIG, SimilarityConfig, calculate_similarity

__all__ = ["DEFAULT_CONFIG", "SimilarityConfig", "calculate_similarity"]
