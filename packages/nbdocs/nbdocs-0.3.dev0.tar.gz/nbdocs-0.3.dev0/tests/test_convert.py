from pathlib import Path

from pytest import CaptureFixture
from nbdocs.core import get_nb_names, read_nb, write_nb
from nbdocs.convert import MdConverter, convert2md, filter_changed
from nbdocs.cfg_tools import NbDocsCfg

from nbdocs.tests.base import create_nb, create_test_nb, create_tmp_image_file


def test_MdConverter():
    """test for MdConverter"""
    md_converter = MdConverter()
    # md cell
    nb = create_nb(md_source="test_md")
    md, resources = md_converter.from_nb(nb)
    assert md == "<!-- cell #0 markdown -->\ntest_md\n"
    assert resources["output_extension"] == ".md"
    assert not resources["image_names"]

    # code cell
    nb = create_test_nb(code_source="test_code")
    md, resources = md_converter.from_nb(nb)
    assert "test_code" in md
    # assert "![png](output_0_2.png)" in md
    # assert resources["outputs"] == {"output_0_2.png": b"g"}
    # assert "output_0_2.png" in resources["image_names"]

    # code and markdown, call()
    nb = create_test_nb(
        code_source="test_code",
        md_source="![cat](cat.jpg)",
    )
    md, resources = md_converter.from_nb(nb)
    assert "test_code" in md
    assert "![png](output_1_2.png)" in md
    assert resources["outputs"] == {"output_1_2.png": b"g"}
    # assert "output_0_1.png" in resources["image_names"]
    # assert "cat.jpg" in resources["image_names"]


def test_convert2md(tmp_path: Path, capsys: CaptureFixture[str]):
    """test convert2md"""
    cfg = NbDocsCfg()
    image_name = "t_1.png"
    create_tmp_image_file(tmp_path / image_name)
    cfg.docs_path = str(tmp_path / "dest")
    nb = create_test_nb(
        code_source="test_code",
        md_source=f"![test image]({image_name})\n![wrong name](wrong_name.png)",
    )
    nb_name = "test_nb.ipynb"
    write_nb(nb, tmp_path / nb_name)

    convert2md(tmp_path / nb_name, cfg)
    with open(
        (tmp_path / cfg.docs_path / nb_name).with_suffix(".md"), "r", encoding="utf-8"
    ) as fh:
        md = fh.read()
    assert "test_code" in md
    dest_images = Path(cfg.docs_path) / "images"
    assert dest_images.exists()
    assert (dest_images / "test_nb_files").exists()
    assert (dest_images / image_name).exists()
    assert (dest_images / "test_nb_files" / "output_0_2.png").exists()
    captured = capsys.readouterr()
    assert "Not fixed image names in nb:" in captured.out
    assert "wrong_name.png" in captured.out


def test_filter_not_changed(tmp_path: Path):
    """test filter_not_changed"""
    cfg = NbDocsCfg()
    # create 2 nb for test
    test_nb_names = ["t_1.ipynb", "t_2.ipynb"]
    for name in test_nb_names:
        nb = create_nb(md_source="")
        write_nb(nb, tmp_path / name)
    nb_names = get_nb_names(tmp_path)
    assert len(nb_names) == 2
    # convert to md
    docs_path = tmp_path / "docs_path"
    cfg.docs_path = str(docs_path)
    convert2md(nb_names, cfg)
    md_files = list(docs_path.glob("*.md"))
    assert len(md_files) == 2

    # check no nb to convert
    changed_nbs = filter_changed(nb_names, cfg)
    assert len(changed_nbs) == 0

    # change 1 nb
    nb_to_change = nb_names[0]
    nb = read_nb(nb_to_change)
    nb.cells[0].source = "changed"
    write_nb(nb, nb_to_change)
    nb_names = get_nb_names(tmp_path)
    assert len(nb_names) == 2
    changed_nbs = filter_changed(nb_names, cfg)
    assert len(changed_nbs) == 1
    assert nb_to_change in changed_nbs

    # add new nb
    new_nb_name = "t_3.ipynb"
    nb = create_nb(md_source="nb_3")
    write_nb(nb, tmp_path / new_nb_name)
    nb_names = get_nb_names(tmp_path)
    assert len(nb_names) == 3
    changed_nbs = filter_changed(nb_names, cfg)
    assert len(changed_nbs) == 2  # changed + new
    assert new_nb_name in [nb.name for nb in changed_nbs]
