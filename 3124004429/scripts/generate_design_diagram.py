"""Generate the design and execution-flow diagram used in the blog."""

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
) -> None:
    """Draw one rounded process box."""

    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.02",
        linewidth=1.3,
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
        fontsize=10,
    )


def add_arrow(
    axis: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
) -> None:
    """Draw a directed arrow between two points."""

    axis.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=14,
            linewidth=1.4,
            color="#26343f",
        )
    )


def build_diagram(output: Path) -> None:
    """Create the flow diagram."""

    figure, axis = plt.subplots(figsize=(13, 7))
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")

    add_box(axis, 0.03, 0.76, 0.18, 0.12, "main.py\n解析 3 个路径参数", "#d8ecff")
    add_box(axis, 0.28, 0.76, 0.19, 0.12, "io_utils.py\n读取并按编码解码", "#e6f5d8")
    add_box(
        axis, 0.54, 0.76, 0.19, 0.12, "normalization.py\n提取正文并归一化", "#fff2cc"
    )
    add_box(axis, 0.80, 0.76, 0.17, 0.12, "similarity.py\n生成 1/2/3-gram", "#f7d9e3")
    add_box(axis, 0.66, 0.50, 0.22, 0.12, "稀疏向量余弦相似度\n加权求和", "#f7d9e3")
    add_box(axis, 0.36, 0.24, 0.28, 0.12, "答案文件\n写入两位小数", "#d8ecff")

    add_arrow(axis, (0.21, 0.82), (0.28, 0.82))
    add_arrow(axis, (0.47, 0.82), (0.54, 0.82))
    add_arrow(axis, (0.73, 0.82), (0.80, 0.82))
    add_arrow(axis, (0.885, 0.76), (0.77, 0.62))
    add_arrow(axis, (0.66, 0.56), (0.50, 0.36))

    axis.text(
        0.50,
        0.93,
        "论文查重程序模块与数据流",
        ha="center",
        fontsize=16,
        fontweight="bold",
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
        default=Path("images/design_flow.png"),
    )
    return parser.parse_args()


def main() -> int:
    build_diagram(parse_args().output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
