"""Command-line interface for the plagiarism checker."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

from plagiarism.errors import CommandLineError, PlagiarismError
from plagiarism.io_utils import read_document, write_answer
from plagiarism.similarity import calculate_similarity

USAGE = (
    "usage: python main.py <原文文件绝对路径> <抄袭版文件绝对路径> <答案文件绝对路径>"
)


def parse_args(arguments: Sequence[str]) -> tuple[Path, Path, Path]:
    """Validate and convert the three positional command-line arguments."""

    if len(arguments) != 3:
        raise CommandLineError(USAGE)
    return tuple(Path(argument) for argument in arguments)  # type: ignore[return-value]


def run(arguments: Sequence[str] | None = None) -> int:
    """Run the command-line program and return a process exit code."""

    raw_arguments = list(sys.argv[1:] if arguments is None else arguments)

    try:
        original_path, candidate_path, answer_path = parse_args(raw_arguments)
        original_text = read_document(original_path)
        candidate_text = read_document(candidate_path)
        similarity = calculate_similarity(original_text, candidate_text)
        write_answer(answer_path, similarity)
    except PlagiarismError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"{similarity:.2f}")
    return 0
