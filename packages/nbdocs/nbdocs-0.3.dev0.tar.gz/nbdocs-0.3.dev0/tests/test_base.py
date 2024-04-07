from pathlib import Path

from nbformat.notebooknode import NotebookNode

from nbdocs.tests.base import (
    create_cell_metadata,
    create_nb,
    create_nb_metadata,
    create_test_metadata_code,
    create_test_metadata_nb,
    create_test_nb,
    create_tmp_image_file,
)


def test_create_nb():
    """test for create_nb"""
    # empty nb
    nb = create_nb()
    assert isinstance(nb, NotebookNode)
    assert len(nb.cells) == 0
    # only code cell
    nb = create_nb("test code")
    assert len(nb.cells) == 1
    assert nb.cells[0].cell_type == "code"
    assert nb.cells[0].source == "test code"
    # only md cell
    nb = create_nb(md_source="test md")
    assert len(nb.cells) == 1
    assert nb.cells[0].cell_type == "markdown"
    assert nb.cells[0].source == "test md"
    # code and markdown
    nb = create_nb(code_source="test code", md_source="test md")
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == "code"
    assert nb.cells[0].source == "test code"
    assert nb.cells[1].cell_type == "markdown"
    assert nb.cells[1].source == "test md"


def test_create_test_nb():
    """test for create_test_nb"""
    # empty nb
    nb = create_test_nb()
    assert isinstance(nb, NotebookNode)
    assert len(nb.cells) == 0
    # only code cell
    nb = create_test_nb("test code")
    assert len(nb.cells) == 1
    assert nb.cells[0].cell_type == "code"
    assert nb.cells[0].source == "test code"
    assert len(nb.cells[0].outputs) == 3
    # only md cell
    nb = create_test_nb(md_source="test md")
    assert len(nb.cells) == 1
    assert nb.cells[0].cell_type == "markdown"
    assert nb.cells[0].source == "test md"
    # code and markdown
    nb = create_test_nb(code_source="test code", md_source="test md")
    assert len(nb.cells) == 2
    assert nb.cells[0].cell_type == "code"
    assert nb.cells[0].source == "test code"
    assert nb.cells[1].cell_type == "markdown"
    assert nb.cells[1].source == "test md"


def test_create_cell_metadata():
    """create_cell_metadata"""
    nb = create_nb("test code")
    assert nb.cells[0].execution_count is None
    assert not nb.cells[0].metadata

    create_cell_metadata(nb.cells[0], create_test_metadata_code(), execution_count=1)
    assert nb.cells[0].execution_count == 1
    assert nb.cells[0].metadata["test_field"] == "test_value"

    nb = create_nb("test code")
    test_metadata = {"test_meta_field": "test_meta_value"}
    create_cell_metadata(nb.cells[0], metadata=test_metadata, execution_count=2)
    assert nb.cells[0].metadata["test_meta_field"] == "test_meta_value"
    assert nb.cells[0].execution_count == 2


def test_create_nb_metadata():
    """test create_nb_metadata"""
    nb = create_nb()
    assert not nb.metadata

    metadata = create_test_metadata_nb()
    create_nb_metadata(nb, create_test_metadata_nb())
    assert nb.metadata.language_info == metadata["language_info"]
    assert nb.metadata.kernelspec == metadata["kernelspec"]


def test_create_tmp_image_file(tmp_path: Path):
    """test create_tmp_image_file"""
    fn = "test.png"
    create_tmp_image_file(tmp_path / fn)
    assert (tmp_path / fn).exists()
