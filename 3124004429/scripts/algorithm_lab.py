"""Benchmark the baseline and optimized similarity implementations."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from pathlib import Path
from time import perf_counter
from typing import Callable

from plagiarism.io_utils import read_document
from plagiarism.normalization import normalize_text
from plagiarism.similarity import calculate_similarity

SimilarityFunction = Callable[[str, str], float]


@dataclass(frozen=True)
class BenchmarkResult:
    """One measured algorithm run."""

    algorithm: str
    repeat: int
    characters: int
    seconds: float
    score: float
    runs: int


def baseline_similarity(original_text: str, candidate_text: str) -> float:
    """Return the sequence-matcher baseline used before optimization."""

    original = normalize_text(original_text)
    candidate = normalize_text(candidate_text)
    if not original or not candidate:
        return 0.0
    if original == candidate:
        return 1.0
    return float(SequenceMatcher(None, original, candidate, autojunk=False).ratio())


def optimized_similarity(original_text: str, candidate_text: str) -> float:
    """Return the current weighted n-gram similarity."""

    return calculate_similarity(original_text, candidate_text)


def _measure(
    algorithm: str,
    function: SimilarityFunction,
    original: str,
    candidate: str,
    repeat: int,
    runs: int = 1,
) -> BenchmarkResult:
    measurements: list[tuple[float, float]] = []
    for _ in range(runs):
        started_at = perf_counter()
        score = function(original, candidate)
        measurements.append((perf_counter() - started_at, score))
    elapsed, score = min(measurements, key=lambda item: item[0])
    return BenchmarkResult(
        algorithm=algorithm,
        repeat=repeat,
        characters=len(normalize_text(original)),
        seconds=elapsed,
        score=score,
        runs=runs,
    )


def run_benchmarks(
    samples_dir: Path,
    repeats: tuple[int, ...] = (1, 2, 5),
    runs: int = 3,
) -> list[BenchmarkResult]:
    """Measure both algorithms on the course sample at several sizes."""

    original = read_document(samples_dir / "orig.txt")
    candidate = read_document(samples_dir / "orig_0.8_dis_10.txt")
    algorithms: tuple[tuple[str, SimilarityFunction], ...] = (
        ("baseline-difflib", baseline_similarity),
        ("optimized-ngram", optimized_similarity),
    )

    results: list[BenchmarkResult] = []
    for repeat in repeats:
        scaled_original = original * repeat
        scaled_candidate = candidate * repeat
        for algorithm, function in algorithms:
            results.append(
                _measure(
                    algorithm,
                    function,
                    scaled_original,
                    scaled_candidate,
                    repeat,
                    runs,
                )
            )
    return results


def write_reports(results: list[BenchmarkResult], report_dir: Path) -> None:
    """Write machine-readable and human-readable benchmark reports."""

    report_dir.mkdir(parents=True, exist_ok=True)
    payload = [asdict(result) for result in results]
    (report_dir / "benchmark.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# 性能对比",
        "",
        "| 算法 | 文本规模 | 最佳耗时（秒） | 运行次数 | 重复率 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for result in results:
        lines.append(
            f"| {result.algorithm} | {result.characters} 字符 | "
            f"{result.seconds:.4f} | {result.runs} | {result.score:.4f} |"
        )

    for repeat in sorted({result.repeat for result in results}):
        grouped = {
            result.algorithm: result for result in results if result.repeat == repeat
        }
        if len(grouped) == 2:
            speedup = (
                grouped["baseline-difflib"].seconds / grouped["optimized-ngram"].seconds
            )
            lines.append("")
            lines.append(f"`{repeat}x` 文本下优化算法加速约 **{speedup:.1f}x**。")

    (report_dir / "benchmark.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("benchmark", "baseline", "optimized"),
        default="benchmark",
    )
    parser.add_argument(
        "--samples-dir",
        type=Path,
        default=Path("samples"),
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=Path("reports"),
    )
    parser.add_argument(
        "--repeats",
        default="1,2,5",
        help="comma-separated text repeat factors",
    )
    parser.add_argument(
        "--measure-runs",
        type=int,
        default=3,
        help="number of measurements per algorithm; the best value is kept",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.mode != "benchmark":
        function = (
            baseline_similarity if args.mode == "baseline" else optimized_similarity
        )
        original = read_document(args.samples_dir / "orig.txt")
        candidate = read_document(args.samples_dir / "orig_0.8_dis_10.txt")
        result = _measure(
            args.mode,
            function,
            original,
            candidate,
            repeat=1,
        )
        print(
            f"{result.algorithm:12s} seconds={result.seconds:.4f} "
            f"score={result.score:.4f}"
        )
        return 0

    repeats = tuple(int(value) for value in args.repeats.split(","))
    results = run_benchmarks(
        args.samples_dir,
        repeats=repeats,
        runs=args.measure_runs,
    )
    write_reports(results, args.report_dir)
    for result in results:
        print(
            f"{result.algorithm:18s} repeat={result.repeat} "
            f"chars={result.characters:7d} "
            f"seconds={result.seconds:8.4f} score={result.score:.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
