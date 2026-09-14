"""性能分析脚本：统计并打印查重算法的 cProfile 结果。"""

from __future__ import annotations

import cProfile
import io
import pstats
from pathlib import Path

from plagiarism.io_utils import read_document
from plagiarism.similarity import calculate_similarity


def main() -> int:
    """运行 10 次查重并输出累计耗时最高的函数。"""

    project_dir = Path(__file__).resolve().parent
    samples_dir = project_dir / "samples"
    original = read_document(samples_dir / "orig.txt")
    candidate = read_document(samples_dir / "orig_0.8_dis_10.txt")

    calculate_similarity(original, candidate)
    profiler = cProfile.Profile()
    profiler.enable()
    for _ in range(10):
        score = calculate_similarity(original, candidate)
    profiler.disable()

    profile_path = project_dir / "profile.prof"
    profiler.dump_stats(str(profile_path))

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumulative").print_stats(15)
    report = stream.getvalue()
    print(report)
    print(f"重复率：{score:.4f}")
    print(f"性能文件：{profile_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
