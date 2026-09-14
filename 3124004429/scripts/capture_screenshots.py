"""Render report text and coverage HTML as real browser screenshots."""

from __future__ import annotations

import argparse
import html
import subprocess
from pathlib import Path

_EDGE_CANDIDATES = (
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
)


def read_report(path: Path) -> str:
    """Read a report encoded by either PowerShell or Python."""

    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def find_browser() -> Path:
    """Return an installed Chromium browser executable."""

    for candidate in _EDGE_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Microsoft Edge or Google Chrome was not found")


def render_terminal_html(title: str, text: str, output: Path) -> None:
    """Write a styled HTML page containing report text."""

    output.parent.mkdir(parents=True, exist_ok=True)
    escaped_title = html.escape(title)
    escaped_text = html.escape(text)
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>{escaped_title}</title>
  <style>
    body {{
      margin: 0;
      padding: 28px;
      background: #101820;
      color: #e8eef2;
      font-family: Consolas, "Cascadia Mono", monospace;
    }}
    h1 {{
      margin: 0 0 18px;
      color: #8fd3ff;
      font-family: "Segoe UI", sans-serif;
      font-size: 22px;
    }}
    pre {{
      margin: 0;
      padding: 22px;
      border: 1px solid #30414f;
      border-radius: 10px;
      background: #071018;
      font-size: 15px;
      line-height: 1.45;
      white-space: pre-wrap;
    }}
  </style>
</head>
<body>
  <h1>{escaped_title}</h1>
  <pre>{escaped_text}</pre>
</body>
</html>
"""
    output.write_text(page, encoding="utf-8")


def capture_page(
    browser: Path,
    page: Path,
    output: Path,
    size: tuple[int, int],
) -> None:
    """Capture a local page with Chromium headless mode."""

    output.parent.mkdir(parents=True, exist_ok=True)
    profile_dir = (output.parent / ".edge-profile").resolve()
    resolved_output = output.resolve()
    command = [
        str(browser),
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-extensions",
        f"--user-data-dir={profile_dir}",
        "--hide-scrollbars",
        "--allow-file-access-from-files",
        f"--window-size={size[0]},{size[1]}",
        f"--screenshot={resolved_output}",
        page.resolve().as_uri(),
    ]
    subprocess.run(command, check=True)


def capture_text_reports(
    browser: Path,
    report_dir: Path,
    image_dir: Path,
    staging_dir: Path,
) -> None:
    """Render all text reports as PNG screenshots."""

    reports = (
        ("pytest.txt", "单元测试与 100% 分支覆盖率", "coverage_and_tests.png", 1500),
        (
            "profile_before.txt",
            "优化前 cProfile：difflib 热点",
            "profile_before_table.png",
            1500,
        ),
        (
            "profile_after.txt",
            "优化后 cProfile：n-gram 热点",
            "profile_after_table.png",
            1500,
        ),
        ("benchmark.md", "基线算法与优化算法性能对比", "benchmark_results.png", 1400),
        ("sample_results.md", "课程样例运行结果", "sample_results.png", 1000),
        ("ruff.txt", "Ruff 代码质量分析：零警告", "ruff_quality.png", 900),
        ("program_run.txt", "程序语法检查与运行截图", "program_run.png", 1000),
    )
    for source_name, title, image_name, height in reports:
        source = report_dir / source_name
        if not source.exists():
            continue
        page = staging_dir / f"{Path(image_name).stem}.html"
        render_terminal_html(title, read_report(source), page)
        capture_page(browser, page, image_dir / image_name, (1500, height))


def capture_coverage_page(
    browser: Path,
    coverage_index: Path,
    output: Path,
) -> None:
    """Capture the generated coverage HTML index."""

    if coverage_index.exists():
        capture_page(browser, coverage_index, output, (1500, 1150))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-dir", type=Path, default=Path("reports"))
    parser.add_argument("--image-dir", type=Path, default=Path("images"))
    parser.add_argument("--staging-dir", type=Path, default=Path("reports/html"))
    parser.add_argument(
        "--coverage-index",
        type=Path,
        default=Path("htmlcov/index.html"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    browser = find_browser()
    capture_text_reports(
        browser,
        args.report_dir,
        args.image_dir,
        args.staging_dir,
    )
    capture_coverage_page(
        browser,
        args.coverage_index,
        args.image_dir / "coverage_html.png",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
