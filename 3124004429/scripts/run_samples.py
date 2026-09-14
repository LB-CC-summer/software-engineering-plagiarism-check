"""Run the checker against every provided sample and write a result table."""

from __future__ import annotations

import argparse
from pathlib import Path
from time import perf_counter

from plagiarism.io_utils import read_document, write_answer
from plagiarism.similarity import calculate_similarity

_CANDIDATE_NAMES = (
    "orig_0.8_add.txt",
    "orig_0.8_del.txt",
    "orig_0.8_dis_1.txt",
    "orig_0.8_dis_10.txt",
    "orig_0.8_dis_15.txt",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples-dir", type=Path, default=Path("data/samples"))
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("reports/sample_results.md"),
    )
    parser.add_argument(
        "--answer-dir",
        type=Path,
        default=Path("reports/answers"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    original = read_document(args.samples_dir / "orig.txt")
    args.answer_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        "# 课程样例运行结果",
        "",
        "| 抄袭版文件 | 重复率 | 耗时（秒） | 答案文件 |",
        "| --- | ---: | ---: | --- |",
    ]
    for name in _CANDIDATE_NAMES:
        candidate = read_document(args.samples_dir / name)
        started_at = perf_counter()
        score = calculate_similarity(original, candidate)
        elapsed = perf_counter() - started_at
        answer_path = args.answer_dir / name.replace(".txt", "_answer.txt")
        write_answer(answer_path, score)
        lines.append(
            f"| `{name}` | {score:.2f} | {elapsed:.4f} | `{answer_path.as_posix()}` |"
        )

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
