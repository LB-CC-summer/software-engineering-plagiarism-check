"""File input and output helpers."""

import codecs
from pathlib import Path

from plagiarism.errors import AnswerWriteError, DocumentDecodeError, DocumentReadError

_SUPPORTED_ENCODINGS = ("utf-8-sig", "gb18030")
_UTF16_BOMS = (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)


def decode_document(raw: bytes, source: Path) -> str:
    """Decode bytes read from a supported text document."""

    if raw.startswith(_UTF16_BOMS):
        try:
            return raw.decode("utf-16")
        except UnicodeDecodeError as exc:
            raise DocumentDecodeError(f"无法按 UTF-16 解码文件：{source}") from exc

    for encoding in _SUPPORTED_ENCODINGS:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue

    raise DocumentDecodeError(f"无法识别文件编码：{source}")


def read_document(path: Path) -> str:
    """Read a document from *path* or raise a user-facing error."""

    if not path.exists():
        raise DocumentReadError(f"输入文件不存在：{path}")
    if not path.is_file():
        raise DocumentReadError(f"输入路径不是文件：{path}")

    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise DocumentReadError(f"无法读取输入文件：{path}") from exc

    return decode_document(raw, path)


def write_answer(path: Path, similarity: float) -> None:
    """Write the similarity score with exactly two decimal places."""

    try:
        path.write_text(f"{similarity:.2f}\n", encoding="utf-8")
    except OSError as exc:
        raise AnswerWriteError(f"无法写入答案文件：{path}") from exc
