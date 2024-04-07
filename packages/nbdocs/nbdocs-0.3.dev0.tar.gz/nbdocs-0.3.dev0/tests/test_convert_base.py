"""Test converting notebooks.
Convert test_nbs to markdown with base and our converters
"""
import pytest
from pathlib import Path

from nbdocs.core import get_nb_names, read_nb
from nbdocs.convert import MdConverter

converter = MdConverter()

nb_path = Path("tests/test_nbs")
md_base_path = Path("tests/converted_base")

nb_names = get_nb_names(nb_path=nb_path)


def test_files():
    """Read tests notebooks"""
    md_names = tuple(md_base_path.glob("*.md"))
    assert len(nb_names) == 7
    assert len(md_names) == 8  # + README.md


@pytest.mark.parametrize("nb_name", nb_names)
def test_convert_base(nb_name):
    """Test base convert"""
    nb = read_nb(nb_name)
    md, _resources = converter.export2md(nb)
    md_name = md_base_path / nb_name.with_suffix(".md").name
    with open(md_name, "r", encoding="utf-8") as fh:
        md_expected = fh.read()
    assert md == md_expected
