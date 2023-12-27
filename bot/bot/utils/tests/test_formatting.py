import pytest

from bot.utils.formatting import bold, codeblock, final_join, markdown_link


def test_markdown_link_no_description() -> None:
    with pytest.raises(ValueError):
        markdown_link(desc="", link="https://example.com")


def test_markdown_link_no_link() -> None:
    with pytest.raises(ValueError):
        markdown_link(desc="example", link="")


def test_markdown_link_correct_output_no_wrapper() -> None:
    x = markdown_link(desc="example", link="https://example.com")

    assert x == "[example](https://example.com)"


def test_markdown_link_correct_output_with_wrapper() -> None:
    x = markdown_link(desc="example", link="https://example.com", desc_wrapper="`")

    assert x == "[`example`](https://example.com)"


def test_codeblock_no_content() -> None:
    assert codeblock([]) == codeblock("") == "```\n\n```"


def test_codeblock_no_content_with_language() -> None:
    assert codeblock([], language="python") == codeblock("", language="python") == "```python\n\n```"


def test_codeblock_single_line() -> None:
    assert codeblock(["asdf"]) == codeblock("asdf") == "```\nasdf\n```"


def test_codeblock_multiple_lines() -> None:
    assert codeblock(["asdf", "example"]) == codeblock("asdf\nexample") == "```\nasdf\nexample\n```"


def test_codeblock_multiple_lines_with_language() -> None:
    assert (
        codeblock(["asdf", "example"], language="python")
        == codeblock("asdf\nexample", language="python")
        == "```python\nasdf\nexample\n```"
    )


def test_bold_does_bold() -> None:
    assert bold("asdf") == "**asdf**"


def test_final_join_no_items() -> None:
    assert final_join([]) == ""


def test_final_join_one_item() -> None:
    assert final_join(["asdf"]) == "asdf"


def test_final_join_multiple_items_default_kwargs() -> None:
    x = final_join(["example", "asdf"])

    assert x == "example, and asdf"


def test_final_join_multiple_items_modified_kwargs() -> None:
    x = final_join(["example", "asdf"], sep="... ", final_sep="or")

    assert x == "example... or asdf"
