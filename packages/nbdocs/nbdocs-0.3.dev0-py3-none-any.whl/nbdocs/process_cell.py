from __future__ import annotations

from .typing import Cell, CodeCell, MarkdownCell
from .re_tools import re_hide, re_hide_input, re_hide_output, re_output_code


def process_markdown_cell(cell: MarkdownCell) -> MarkdownCell | None:
    """Process markdown cell. If source is empty - return None.

    Args:
        cell (MarkdownCell): Markdown cell to process.

    Returns:
        MarkdownCell: Processed markdown cell.
    """
    if cell.source == "":
        return None
    return cell


def process_code_cell(cell: CodeCell) -> Cell | None:
    """Process cell.
    If source is empty - return None.
    Mark cell, remove source if hide_input, remove output if hide_output.

    Args:
        cell (Cell): Cell to process.

    Returns:
        Cell | None: Processed cell or None.
    """
    if cell.source == "" or re_hide.search(cell.source) is not None:
        return None
    if re_hide_output.search(cell.source) is not None:
        cell.outputs = []
        cell.source = re_output_code.sub(r"", cell.source).lstrip()
    if re_hide_input.search(cell.source) is not None:
        cell.source = ""
    # TODO: check another flags!!!!
    return cell
