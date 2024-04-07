from pathlib import Path

from nbdocs.clean import clean_nb, clean_nb_file
from nbdocs.core import read_nb, write_nb
from nbdocs.tests.base import (
    create_test_metadata_code,
    create_cell_metadata,
    create_nb_metadata,
    create_test_nb,
    create_test_metadata_nb,
)


def test_clean_nb():
    """test clean_nb"""
    nb = create_test_nb("test code")
    create_nb_metadata(nb, create_test_metadata_nb())
    create_cell_metadata(nb.cells[0], create_test_metadata_code())
    assert nb.metadata
    assert nb.cells[0].metadata
    clean_nb(nb, clear_execution_count=False)
    assert nb.metadata == {"language_info": {"name": "python"}}
    assert nb.cells[0].execution_count == 1
    assert nb.cells[0].outputs[0].execution_count == 1
    assert not nb.cells[0].metadata
    clean_nb(nb)
    assert not nb.cells[0].execution_count
    assert not nb.cells[0].outputs[0].execution_count


def test_clean_nb_file(tmp_path: Path):
    """test clean_nb_file"""
    test_nb_fn = tmp_path / "test_nb.ipynb"
    nb = create_test_nb("test code")
    create_nb_metadata(nb, create_test_metadata_nb())
    create_cell_metadata(nb.cells[0], create_test_metadata_code())
    write_nb(nb, test_nb_fn)

    clean_nb_file(test_nb_fn)
    nb_cleared = read_nb(test_nb_fn)
    assert nb_cleared.metadata == {"language_info": {"name": "python"}}
    assert not nb_cleared.cells[0].execution_count
    assert not nb_cleared.cells[0].outputs[0].execution_count
    assert not nb_cleared.cells[0].metadata
