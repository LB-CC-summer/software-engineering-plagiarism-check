"""Tests for the command-line workflow."""

from pathlib import Path

from plagiarism.cli import parse_args, run


def test_parse_args_returns_three_paths() -> None:
    paths = parse_args(["orig.txt", "copy.txt", "answer.txt"])

    assert paths == (Path("orig.txt"), Path("copy.txt"), Path("answer.txt"))


def test_cli_requires_exactly_three_arguments(capsys) -> None:
    exit_code = run(["only-one.txt"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "usage:" in captured.err


def test_cli_writes_answer_and_prints_score(tmp_path: Path, capsys) -> None:
    original = tmp_path / "orig.txt"
    candidate = tmp_path / "copy.txt"
    answer = tmp_path / "answer.txt"
    original.write_text("今天是星期天，天气晴。", encoding="utf-8")
    candidate.write_text("今天是星期天，天气晴朗。", encoding="utf-8")

    exit_code = run([str(original), str(candidate), str(answer)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert answer.read_text(encoding="utf-8").strip() == captured.out.strip()
    assert len(answer.read_text(encoding="utf-8").strip().split(".")[-1]) == 2


def test_cli_reports_missing_input(tmp_path: Path, capsys) -> None:
    candidate = tmp_path / "copy.txt"
    candidate.write_text("文本", encoding="utf-8")
    answer = tmp_path / "answer.txt"

    exit_code = run([str(tmp_path / "missing.txt"), str(candidate), str(answer)])

    assert exit_code == 2
    assert "输入文件不存在" in capsys.readouterr().err
    assert not answer.exists()


def test_cli_reports_decode_error(tmp_path: Path, capsys) -> None:
    original = tmp_path / "orig.txt"
    candidate = tmp_path / "copy.txt"
    answer = tmp_path / "answer.txt"
    original.write_bytes(b"\xff\xfe\x00")
    candidate.write_text("文本", encoding="utf-8")

    exit_code = run([str(original), str(candidate), str(answer)])

    assert exit_code == 2
    assert "UTF-16" in capsys.readouterr().err


def test_cli_reports_output_error(tmp_path: Path, capsys) -> None:
    original = tmp_path / "orig.txt"
    candidate = tmp_path / "copy.txt"
    original.write_text("文本", encoding="utf-8")
    candidate.write_text("文本", encoding="utf-8")

    exit_code = run([str(original), str(candidate), str(tmp_path)])

    assert exit_code == 2
    assert "无法写入答案文件" in capsys.readouterr().err
