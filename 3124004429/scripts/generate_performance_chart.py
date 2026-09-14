"""Render cProfile statistics and benchmark results as PNG charts."""

from __future__ import annotations

import argparse
import io
import pstats
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def load_stats(path: Path) -> pstats.Stats:
    """Load a cProfile data file."""

    return pstats.Stats(str(path))


def format_function_name(key: tuple[str, int, str]) -> str:
    """Create a compact function label for a chart."""

    filename, line_number, function_name = key
    short_file = Path(filename).name
    return f"{function_name} ({short_file}:{line_number})"


def top_functions(
    stats: pstats.Stats,
    limit: int = 10,
) -> list[tuple[str, float]]:
    """Return the slowest functions ordered by cumulative seconds."""

    rows = []
    for key, value in stats.stats.items():
        cumulative_seconds = value[3]
        rows.append((format_function_name(key), cumulative_seconds))
    return sorted(rows, key=lambda item: item[1], reverse=True)[:limit]


def plot_profile(stats: pstats.Stats, title: str, output: Path) -> None:
    """Create a horizontal bar chart for one cProfile report."""

    rows = list(reversed(top_functions(stats)))
    labels = [label for label, _ in rows]
    values = [value for _, value in rows]

    figure, axis = plt.subplots(figsize=(11, 6.5))
    axis.barh(labels, values, color="#2f6f9f")
    axis.set_title(title, fontsize=15, fontweight="bold")
    axis.set_xlabel("Cumulative time (seconds)")
    axis.grid(axis="x", linestyle="--", alpha=0.35)
    figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=160)
    plt.close(figure)


def write_profile_text(stats: pstats.Stats, output: Path) -> None:
    """Write a pstats table and a compact top-function summary."""

    output.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()
    stats.stream = buffer
    stats.sort_stats("cumulative").print_stats(20)
    output.write_text(buffer.getvalue(), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--image-dir", type=Path, default=Path("images"))
    parser.add_argument("--report-dir", type=Path, default=Path("reports"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    before = load_stats(args.before)
    after = load_stats(args.after)

    plot_profile(
        before,
        "Baseline: difflib SequenceMatcher",
        args.image_dir / "performance_before.png",
    )
    plot_profile(
        after,
        "Optimized: weighted character n-gram cosine",
        args.image_dir / "performance_after.png",
    )
    write_profile_text(before, args.report_dir / "profile_before.txt")
    write_profile_text(after, args.report_dir / "profile_after.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
