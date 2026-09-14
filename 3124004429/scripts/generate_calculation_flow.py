"""生成计算模块的类、函数关系和关键流程动画。"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def add_box(
    axis: plt.Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str,
    color: str,
    font_size: int = 10,
) -> None:
    """绘制一个圆角模块框。"""

    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.015",
        linewidth=1.2,
        edgecolor="#26343f",
        facecolor=color,
    )
    axis.add_patch(box)
    axis.text(
        x + width / 2,
        y + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=font_size,
        linespacing=1.45,
    )


def add_arrow(
    axis: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    style: str = "-|>",
    color: str = "#26343f",
) -> None:
    """绘制带箭头的调用关系。"""

    axis.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=13,
            linewidth=1.35,
            color=color,
        )
    )


def build_diagram(output: Path) -> None:
    """绘制双栏图：左侧为模块关系，右侧为核心计算流程。"""

    figure, axis = plt.subplots(figsize=(16, 9))
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")

    axis.text(
        0.5,
        0.965,
        "论文查重计算模块：类、函数关系与关键流程",
        ha="center",
        fontsize=18,
        fontweight="bold",
    )
    axis.text(
        0.03,
        0.925,
        "左侧：模块、类和函数关系",
        ha="left",
        fontsize=13,
        fontweight="bold",
        color="#1e4e79",
    )
    axis.text(
        0.55,
        0.925,
        "右侧：calculate_similarity() 关键流程",
        ha="left",
        fontsize=13,
        fontweight="bold",
        color="#7a3e00",
    )

    add_box(axis, 0.02, 0.81, 0.12, 0.075, "main.py\n命令行入口", "#d9ecff")
    add_box(axis, 0.17, 0.81, 0.18, 0.075, "plagiarism.cli\nrun()", "#d9ecff")
    add_box(axis, 0.39, 0.81, 0.14, 0.075, "parse_args()", "#e8f1fa", 9)

    add_box(axis, 0.17, 0.70, 0.18, 0.075, "read_document()", "#e6f5d8", 9)
    add_box(axis, 0.39, 0.70, 0.16, 0.075, "write_answer()", "#e6f5d8", 9)
    add_box(axis, 0.17, 0.59, 0.22, 0.075, "calculate_similarity()", "#f7d9e3", 10)

    add_box(
        axis,
        0.02,
        0.43,
        0.54,
        0.13,
        "similarity.py\n"
        "SimilarityConfig（dataclass，配置类）\n"
        "calculate_similarity() / count_ngrams()\n"
        "_cosine_similarity() / _iter_available_ngrams()",
        "#f7d9e3",
        10,
    )
    add_box(
        axis,
        0.02,
        0.26,
        0.54,
        0.13,
        "normalization.py\n"
        "extract_embedded_text() -> _VisibleTextParser（HTML 类）\n"
        "normalize_text()：NFKC、casefold、标点过滤",
        "#fff2cc",
        10,
    )
    add_box(
        axis,
        0.02,
        0.09,
        0.54,
        0.13,
        "io_utils.py / errors.py\n"
        "decode_document() -> read_document()\n"
        "write_answer() / 四类 PlagiarismError",
        "#e6f5d8",
        10,
    )

    add_arrow(axis, (0.14, 0.847), (0.17, 0.847))
    add_arrow(axis, (0.35, 0.847), (0.39, 0.847))
    add_arrow(axis, (0.26, 0.81), (0.26, 0.775))
    add_arrow(axis, (0.35, 0.81), (0.45, 0.775))
    add_arrow(axis, (0.26, 0.70), (0.27, 0.665))
    add_arrow(axis, (0.27, 0.59), (0.27, 0.56))
    add_arrow(axis, (0.42, 0.43), (0.42, 0.39))
    add_arrow(axis, (0.42, 0.26), (0.42, 0.22))

    add_box(
        axis,
        0.60,
        0.81,
        0.36,
        0.075,
        "normalize_text(original)\nnormalize_text(candidate)",
        "#fff2cc",
        10,
    )
    add_box(
        axis,
        0.60,
        0.69,
        0.36,
        0.075,
        "若任一为空 -> 0.0\n若完全相同 -> 1.0",
        "#fff2cc",
        10,
    )
    add_box(
        axis,
        0.60,
        0.57,
        0.36,
        0.075,
        "_iter_available_ngrams()\n过滤长度不足或权重为 0 的阶数",
        "#f7d9e3",
        10,
    )
    add_box(
        axis,
        0.60,
        0.45,
        0.36,
        0.075,
        "循环 n = 1, 2, 3",
        "#f7d9e3",
        11,
    )
    add_box(
        axis,
        0.60,
        0.33,
        0.36,
        0.075,
        "count_ngrams(original, n)\ncount_ngrams(candidate, n)",
        "#f7d9e3",
        10,
    )
    add_box(
        axis,
        0.60,
        0.21,
        0.36,
        0.075,
        "_cosine_similarity(left, right)\n点积 / 两个向量范数乘积",
        "#f7d9e3",
        10,
    )
    add_box(
        axis,
        0.60,
        0.09,
        0.36,
        0.075,
        "按 0.15 / 0.45 / 0.40 加权求和\nclamp 到 [0, 1] 并返回",
        "#e6f5d8",
        10,
    )

    for start, end in (
        ((0.78, 0.81), (0.78, 0.765)),
        ((0.78, 0.69), (0.78, 0.645)),
        ((0.78, 0.57), (0.78, 0.525)),
        ((0.78, 0.45), (0.78, 0.405)),
        ((0.78, 0.33), (0.78, 0.285)),
        ((0.78, 0.21), (0.78, 0.165)),
    ):
        add_arrow(axis, start, end, color="#7a3e00")

    add_arrow(axis, (0.60, 0.4875), (0.565, 0.4875), color="#7a3e00")
    axis.text(
        0.585,
        0.505,
        "读取配置",
        ha="right",
        fontsize=9,
        color="#7a3e00",
    )

    axis.text(
        0.05,
        0.035,
        "共 2 个类、11 个主要函数；核心计算时间复杂度 O(n + m)，空间复杂度 O(n + m)。",
        ha="left",
        fontsize=10,
        color="#26343f",
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    figure.tight_layout()
    figure.savefig(output, dpi=160)
    plt.close(figure)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("images/calculation_module_flow.png"),
    )
    return parser.parse_args()


def main() -> int:
    build_diagram(parse_args().output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
