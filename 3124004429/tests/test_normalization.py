"""Tests for normalization and embedded-HTML extraction."""

from plagiarism.normalization import extract_embedded_text, normalize_text


def test_normalize_removes_case_whitespace_and_punctuation() -> None:
    assert normalize_text("Hello, 世界！\n\tPython 3.12") == "hello世界python312"


def test_normalize_uses_unicode_compatibility_characters() -> None:
    assert normalize_text("ＡＢＣ１２３") == "abc123"


def test_normalize_empty_text() -> None:
    assert normalize_text("") == ""


def test_extract_github_blob_rows() -> None:
    page = """
    <html><body>
      <script>ignore this script</script>
      <table>
        <tr>
          <td class="blob-num">1</td>
          <td class="blob-code blob-code-inner js-file-line">第一行</td>
        </tr>
        <tr>
          <td class="blob-num">2</td>
          <td class="blob-code blob-code-inner js-file-line">第二行</td>
        </tr>
      </table>
    </body></html>
    """

    assert extract_embedded_text(page).strip() == "第一行\n第二行"


def test_extract_generic_visible_html_text() -> None:
    page = "<html><body><p>甲</p><script>bad()</script><p>乙</p></body></html>"
    visible = extract_embedded_text(page)

    assert "甲" in visible
    assert "乙" in visible
    assert "bad()" not in visible


def test_plain_text_is_not_modified() -> None:
    assert extract_embedded_text("普通文本") == "普通文本"
