"""Tests for document decoding, reading, and writing."""

from pathlib import Path
from unittest.mock import patch

import pytest

from plagiarism.errors import AnswerWriteError, DocumentDecodeError, DocumentReadError
from plagiarism.io_utils import decode_document, read_document, write_answer


def test_read_document_accepts_utf8_with_bom(tmp_path: Path) -> None:
    path = tmp_path / "utf8.txt"
    path.write_bytes(b"\xef\xbb\xbf" + "中文文本".encode())

    assert read_document(path) == "中文文本"


def test_read_document_falls_back_to_gb18030(tmp_path: Path) -> None:
    path = tmp_path / "gb.txt"
    path.write_bytes("中文文本".encode("gb18030"))

    assert read_document(path) == "中文文本"


def test_missing_document_raises_read_error(tmp_path: Path) -> None:
    with pytest.raises(DocumentReadError, match="不存在"):
        read_document(tmp_path / "missing.txt")


def test_directory_as_document_raises_read_error(tmp_path: Path) -> None:
    with pytest.raises(DocumentReadError, match="不是文件"):
        read_document(tmp_path)


def test_malformed_utf16_bom_raises_decode_error(tmp_path: Path) -> None:
    path = tmp_path / "bad-utf16.txt"
    path.write_bytes(b"\xff\xfe\x00")

    with pytest.raises(DocumentDecodeError, match="UTF-16"):
        decode_document(path.read_bytes(), path)


def test_write_answer_uses_two_decimal_places(tmp_path: Path) -> None:
    answer = tmp_path / "answer.txt"

    write_answer(answer, 0.756)

    assert answer.read_text(encoding="utf-8") == "0.76\n"


def test_write_answer_to_directory_raises_write_error(tmp_path: Path) -> None:
    with pytest.raises(AnswerWriteError, match="无法写入"):
        write_answer(tmp_path, 0.5)


def test_read_error_is_wrapped(tmp_path: Path) -> None:
    path = tmp_path / "document.txt"
    path.write_text("text", encoding="utf-8")

    with patch("pathlib.Path.read_bytes", side_effect=OSError("boom")):
        with pytest.raises(DocumentReadError, match="无法读取"):
            read_document(path)


def test_unsupported_encoding_raises_decode_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "plagiarism.io_utils._SUPPORTED_ENCODINGS",
        ("ascii",),
    )

    with pytest.raises(DocumentDecodeError, match="无法识别"):
        decode_document(b"\xff", tmp_path / "unknown.txt")
