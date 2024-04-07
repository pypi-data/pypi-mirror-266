from pathlib import Path
from pytest import CaptureFixture

from nbdocs.apps.app_nbclean import main as app_nbclean

from nbdocs.apps.app_nb2md import convert as app_nb2md


def test_app_nbclean_def(capsys: CaptureFixture[str]):
    """Test default run"""
    # run without args
    # try:
    app_nbclean([])
    # except SystemExit as e:
    #     assert e.code == 2
    captured = capsys.readouterr()
    out = captured.out
    assert "Clean: nbs, found 1 notebooks." in out
    assert "All notebooks were clean." in out
    error_out = captured.err
    assert "" == error_out


def test_app_nbclean_no_nb(capsys: CaptureFixture[str]):
    """Test if no Nb at path or path not exist"""
    try:
        app_nbclean(["-p", "."])
    except SystemExit as e:
        assert e.code is None

    captured = capsys.readouterr()
    out = captured.out
    assert "No files to clean!" in out
    err_out = captured.err
    assert err_out == ""

    try:
        app_nbclean(["-p", "not_exist_path"])
    except SystemExit as e:  # pragma: no cover
        assert e.code is None
    captured = capsys.readouterr()
    out = captured.out
    assert "not exists!" in out
    err_out = captured.err
    assert err_out == ""


def test_app_nbclean(capsys: CaptureFixture[str]):
    """Test nb folder and file run"""
    try:
        app_nbclean(["--path", "tests/test_nbs"])
    except SystemExit as e:  # pragma: no cover
        assert e.code == 0
    captured = capsys.readouterr()
    out = captured.out
    assert "tests/test_nbs" in out
    err_out = captured.err
    assert err_out == ""

    try:
        app_nbclean(["-p", "tests/test_nbs/code_hide_cells.ipynb"])
    except SystemExit as e:  # pragma: no cover
        assert e.code == 0
    captured = capsys.readouterr()
    out = captured.out
    assert "tests/test_nbs/code_hide_cells.ipynb" in out
    err_out = captured.err
    assert err_out == ""


def test_app_nb2md(tmp_path: Path, capsys: CaptureFixture[str]):
    """test nb2md"""
    # run for one nb
    try:
        app_nb2md(["tests/test_nbs/nb_1.ipynb", "--dest", f"{str(tmp_path)}"])
    except SystemExit as e:  # pragma: no cover
        assert e.code is None

    captured = capsys.readouterr()
    out = captured.out
    assert "Found 1 notebooks." in out
    err_out = captured.err
    assert err_out == ""

    # run for folder w/o nbs, no nb to process.
    try:
        app_nb2md(["tests/", "--dest", f"{tmp_path}"])
    except SystemExit as e:
        assert e.code is None

    captured = capsys.readouterr()
    out = captured.out
    assert "No files to convert!" in out
    err_out = captured.err
    assert err_out == ""

    # run for folder with test nbs.
    try:
        app_nb2md(["tests/test_nbs/", "--dest", f"{tmp_path}"])
    except SystemExit as e:  # pragma: no cover
        assert e.code is None

    captured = capsys.readouterr()
    out = captured.out
    assert "Found 7 notebooks" in out
    err_out = captured.err
    assert err_out == ""
    # check for result

    # run again - no changes in nbs
    try:
        app_nb2md(["tests/test_nbs/", "--dest", f"{tmp_path}"])
    except SystemExit as e:
        assert e.code is None

    captured = capsys.readouterr()
    out = captured.out
    assert "No files with changes to convert!" in out
    err_out = captured.err
    assert err_out == ""
