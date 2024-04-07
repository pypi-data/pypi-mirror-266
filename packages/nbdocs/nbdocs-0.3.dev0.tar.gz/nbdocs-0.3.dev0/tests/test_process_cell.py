from nbdocs.tests.base import create_code_cell, create_markdown_cell, create_test_outputs

from nbdocs.process_cell import process_code_cell, process_markdown_cell


def test_process_markdown_cell():
    """test process_markdown_cell"""
    cell = create_markdown_cell("test")
    result = process_markdown_cell(cell)
    assert result is cell

    cell = create_markdown_cell("")
    result = process_markdown_cell(cell)
    assert result is None


def test_process_code_cell():
    """test process_code_cell"""
    # just code
    cell = create_code_cell("some code")
    result = process_code_cell(cell)
    assert result is cell
    assert result.source == "some code"

    # empty code
    cell = create_code_cell("")
    result = process_code_cell(cell)
    assert result is None

    # hide cell
    cell = create_code_cell("# hide")
    result = process_code_cell(cell)
    assert result is None

    # hide_output cell
    cell = create_code_cell(
        "# hide_output",
        outputs=create_test_outputs(),
    )
    assert len(cell.outputs) == 3
    result = process_code_cell(cell)
    assert result.outputs == []

    # hide_input cell
    cell = create_code_cell(
        "# hide_input",
        outputs=create_test_outputs(),
    )
    assert len(cell.outputs) == 3
    result = process_code_cell(cell)
    assert len(cell.outputs) == 3
    assert result.source == ""

    # cell with cleaned source -> remove.
    cell = create_code_cell(
        source="Some code",
        outputs=create_test_outputs(),
    )
    assert len(cell.outputs) == 3
    cell.source = ""
    result = process_code_cell(cell)
    assert result is None
