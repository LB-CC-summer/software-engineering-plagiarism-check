"""Profile only the core similarity function, excluding module imports."""

from __future__ import annotations

import argparse
import cProfile
from pathlib import Path
from time import perf_counter

from plagiarism.io_utils import read_document
from plagiarism.similarity import calculate_similarity
from scripts.algorithm_lab import baseline_similarity


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("baseline", "optimized"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--samples-dir", type=Path, default=Path("samples"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    function = baseline_similarity if args.mode == "baseline" else calculate_similarity
    original = read_document(args.samples_dir / "orig.txt")
    candidate = read_document(args.samples_dir / "orig_0.8_dis_10.txt")

    function(original, candidate)
    profiler = cProfile.Profile()
    started_at = perf_counter()
    profiler.enable()
    for _ in range(args.repeat):
        score = function(original, candidate)
    profiler.disable()
    elapsed = perf_counter() - started_at

    args.output.parent.mkdir(parents=True, exist_ok=True)
    profiler.dump_stats(str(args.output))
    print(
        f"mode={args.mode} repeat={args.repeat} seconds={elapsed:.4f} score={score:.4f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
