from nbdocs.re_tools import (
    generate_flags_string,
    re_flags,
    re_hide,
    re_hide_input,
    re_hide_output,
    re_code_cell_marker,
    re_collapse,
)


def test_generate_flags_string():
    """Generate pattern for flags"""
    flags = ["flag1", "flag2"]
    pattern = generate_flags_string(flags)
    assert pattern == "flag1|flag2"
    flags = ["flag_1", "flag_2"]
    pattern = generate_flags_string(flags)
    assert "flag-1" in pattern
    assert "flag-2" in pattern


def test_re_flags():
    """test search"""
    assert re_flags.search("hide") is None
    assert re_flags.search("hide\n #hide") is not None


def test_predefined_patterns():
    """test predefined patterns"""
    assert re_hide.search("# hide") is not None
    assert re_hide.search("# hide\n") is not None
    assert re_hide.search("#hide") is not None
    assert re_hide.search("# hide_input") is None

    assert re_hide_input.search("# hide_input") is not None
    assert re_hide_input.search("#hide_input") is not None
    assert re_hide_input.search("# hide") is None

    assert re_hide_output.search("# hide_output") is not None
    assert re_hide_output.search("#hide_output") is not None
    assert re_hide_output.search("# hide") is None
    assert re_hide_output.search("# hide_input") is None

    text = "#hide_output\nSome text"
    assert re_hide_output.sub(r"", text).lstrip() == "Some text"


def test_predefined_flags_sub():
    """test predefined flags sub"""
    text = "# hide\nSome text"
    assert re_hide.sub(r"", text).lstrip() == "Some text"
    # assert re_hide.sub(r"", text) == "Some text"

    text = "# hide_input\nSome text"
    assert re_hide_input.sub(r"", text).lstrip() == "Some text"

    text = "# hide_output\nSome text"
    assert re_hide_output.sub(r"", text).lstrip() == "Some text"

    text = "# hide_output\n\nSome text"
    assert re_hide_output.sub(r"", text).lstrip() == "Some text"

    text = "# collapse_output\nSome text"
    assert re_collapse.sub("", text) == "Some text"
    # assert re_collapse.sub("", text).lstrip() == "Some text"


def test_re_code_cell_marker():
    """test re_code_cell_marker"""
    cell = "```python\nSome code\n```\n"
    assert re_code_cell_marker.search(cell)
    assert re_code_cell_marker.sub(r"", cell) == "Some code\n"

    assert re_code_cell_marker.sub(r"", "```\n") == ""
    assert re_code_cell_marker.sub(r"", "```Python\n") == ""
    assert re_code_cell_marker.sub(r"", "```python\n```\n") == ""
