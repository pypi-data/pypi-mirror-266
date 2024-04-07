from pathlib import Path

import pytest
from nbformat.notebooknode import NotebookNode

from nbdocs.cfg_tools import get_config
from nbdocs.core import get_nb_names, get_readme_fn, process_readme, read_nb, write_nb

nb_path = Path("tests/test_nbs")
nb_name = "nb_1.ipynb"
nb_filename = nb_path / nb_name


def test_read_nb():
    """Read nb"""
    nb = read_nb(nb_filename)
    assert isinstance(nb, NotebookNode)
    assert nb.nbformat == 4
    assert nb.cells[0].cell_type == "markdown"
    assert nb.cells[1].cell_type == "code"
    nb = read_nb(nb_filename, as_version=3)  # type: ignore
    assert nb.nbformat == 3


def test_write_nb(tmp_path: Path):
    """Write nb"""
    nb = read_nb(nb_filename)
    dest_name = tmp_path / nb_name
    write_nb(nb, dest_name)
    assert nb_filename.stat().st_size == dest_name.stat().st_size
    assert dest_name.exists()
    nb_written = read_nb(dest_name)
    assert nb == nb_written

    # name w/out extension
    new_name = "tmp"
    dest_name = tmp_path / new_name
    written_name = write_nb(nb, dest_name)
    expected_name = dest_name.with_suffix(".ipynb")
    assert written_name == expected_name
    assert expected_name.exists()
    assert nb_filename.stat().st_size == expected_name.stat().st_size
    nb_written = read_nb(expected_name)
    assert nb == nb_written


def test_get_nb_names():
    """get_nb_names"""
    # default
    nb_names = get_nb_names()
    assert len(nb_names) == 0  # no nbs at test dir

    # check return None from get_readme_fn
    readme_fn = get_readme_fn(nb_names)
    assert readme_fn is None

    # Nbs dir - 1 nb yet
    cfg = get_config()
    nb_names = get_nb_names(cfg.notebooks_path)
    assert len(nb_names) == 1  # later will be more nbs
    names = [fn.name for fn in nb_names]
    assert "README.ipynb" in names

    # test get_readme_fn
    readme_fn = get_readme_fn(nb_names)
    assert isinstance(readme_fn, Path)
    assert readme_fn.name == "README.ipynb"

    # one file
    nb_names = get_nb_names(nb_filename)
    assert len(nb_names) == 1
    assert nb_names[0].name == nb_name

    # dir
    nb_names = get_nb_names(nb_path)
    assert len(nb_names) == 7
    names = [fn.name for fn in nb_names]
    assert nb_name in names

    # wrong name
    with pytest.raises(SystemExit):
        nb_names = get_nb_names(nb_path / "nb_1")

    # file not nb
    with pytest.raises(SystemExit):
        nb_names = get_nb_names(nb_path / "images/cat.jpg")


text = """\
---
title: "test"
---
# Header
"""


def test_process_readme():
    """test process_readme"""
    result = process_readme(text)
    assert result == "# Header"
