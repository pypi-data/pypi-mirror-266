from nbdocs.process_md import (
    format_code_cell,
    format_md_cell,
    split_md,
    separate_source_output,
    check_code_cell_empty,
    OUTPUT_CLOSE,
    OUTPUT_OPEN,
    OUTPUT_COLLAPSED,
)

CELL_MARK_CODE = "<!-- cell #0 code -->\n"
CELL_MARK_MD = "<!-- cell #0 markdown -->\n"


def test_split_md():
    """test split_md"""
    # 2 cells
    input_md = "###cell\nThis is cell 1.\n###cell\nThis is cell 2."
    expected_output = ("This is cell 1.\n", "This is cell 2.")
    output = split_md(input_md)
    assert output == expected_output

    # single cell
    input_md = "###cell\nThis is the only cell."
    expected_output = ("This is the only cell.", )
    output = split_md(input_md)
    assert output == expected_output

    # markdown string without cell flag
    input_md = "This is just a string."
    expected_output = ("This is just a string.", )
    output = split_md(input_md)
    assert output == expected_output


def test_split_md_2():
    """test split_md code cells"""
    # one cell
    text = "###cell\n```python\nSome code\n```"
    result = split_md(text)
    assert result == ("```python\nSome code\n```", )

    # two cells
    text = "###cell\n```python\nSome code\n```###cell\n```python\nMore code\n```"
    result = split_md(text)
    assert result == ("```python\nSome code\n```", "```python\nMore code\n```")


def test_separate_source_output():
    """test separate_source_output"""
    cell = "```python\nSome code\n```\n    output\n"
    code, output = separate_source_output(cell)
    assert code == "```python\nSome code\n```\n"
    assert output == "\n    output\n"

    cell = "```\nSome code\n```\n    output\n"
    code, output = separate_source_output(cell)
    assert code == "```\nSome code\n```\n"
    assert output == "\n    output\n"


code_sell = """\
<!-- cell #0 code -->


```python
some_code
```

    output


"""
expected_code = "<!-- cell #0 code -->\n```python\nsome_code\n```\n"
excepted_output = "\n    output\n\n\n"


def test_separate_source_output_2():
    """test separate_source_output"""
    code, output = separate_source_output(code_sell)
    assert code == expected_code
    assert output == excepted_output


def test_check_code_cell_empty():
    """test check_code_cell_empty"""
    assert check_code_cell_empty("```\n```\n")
    assert check_code_cell_empty("```\n\n```\n")
    assert not check_code_cell_empty("```python\nSome code\n```")

    assert check_code_cell_empty(CELL_MARK_CODE + "```\n```\n")
    assert check_code_cell_empty(CELL_MARK_CODE + "```\n\n```\n")
    assert not check_code_cell_empty(CELL_MARK_CODE + "```\nSome code\n```")


EXPECTED_OUTPUT = OUTPUT_OPEN + "\n    output\n" + OUTPUT_CLOSE
EXPECTED_OUTPUT_COLLAPSED = OUTPUT_COLLAPSED + "\n    output\n" + OUTPUT_CLOSE


def test_format_code_cell():
    """test format_code_cell"""
    code_open = "```python\n"
    code_close = "```\n"
    code = "Some code\n"
    output = "\n    output\n"
    result = format_code_cell(code_open + code + code_close + output)
    assert result == code_open + code + code_close + EXPECTED_OUTPUT

    result = format_code_cell(
        CELL_MARK_CODE + "\n\n" + code_open + code + code_close + output
    )
    assert result == CELL_MARK_CODE + code_open + code + code_close + EXPECTED_OUTPUT

    # collapsed
    result = format_code_cell(code_open + "# collapse_output\n" + code + code_close + output)
    assert result == code_open + code + code_close + EXPECTED_OUTPUT_COLLAPSED
    result = format_code_cell(CELL_MARK_CODE + "\n\n" + code_open + "# collapse_output\n" + code + code_close + output)
    assert result == CELL_MARK_CODE + code_open + code + code_close + EXPECTED_OUTPUT_COLLAPSED

    # collapsed, no code
    result = format_code_cell(code_open + "# collapse_output\n" + code + code_close + output)
    assert result == code_open + code + code_close + EXPECTED_OUTPUT_COLLAPSED


md_cell = """\
<!-- cell #0 markdown -->

Markdown text
"""
expected_md = """<!-- cell #0 markdown -->\nMarkdown text\n"""


def test_format_md_cell():
    """test format_md_cell"""
    assert format_md_cell(md_cell) == expected_md
