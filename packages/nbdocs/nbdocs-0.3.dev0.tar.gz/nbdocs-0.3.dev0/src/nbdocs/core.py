from __future__ import annotations

import sys
from pathlib import Path

import nbformat
from rich import print as rprint

from nbdocs.typing import Nb, PathOrStr


def read_nb(fn: PathOrStr, as_version: nbformat.Sentinel = nbformat.NO_CONVERT) -> Nb:
    """Read notebook from filename.

    Args:
        fn (Union[str, PosixPath): Notebook filename.
        as_version (int, optional): Version of notebook. Defaults to None, convert from 4.

    Returns:
        Notebook: Jupyter Notebook]
    """
    with Path(fn).open("r", encoding="utf-8") as fh:
        nb: Nb = nbformat.read(fh, as_version=as_version)  # type: ignore
    return nb


def write_nb(
    nb: Nb,
    fn: PathOrStr,
    as_version: nbformat.Sentinel = nbformat.NO_CONVERT,
) -> Path:
    """Write notebook to file

    Args:
        nb (Notebook): Notebook to write
        fn (Union[str, PosixPath]): filename to write
        as_version (_type_, optional): Nbformat version. Defaults to nbformat.NO_CONVERT.
    Returns:
        Path: Filename of written Nb.
    """
    filename = Path(fn)
    if filename.suffix != ".ipynb":
        filename = filename.with_suffix(".ipynb")
    with filename.open("w", encoding="utf-8") as fh:
        nbformat.write(nb, fh, version=as_version)  # type: ignore
    return filename


def get_nb_names(nb_path: PathOrStr | None = None) -> list[Path]:
    """Return list of notebooks from `path`. If no `path` return notebooks from current folder.

    Args:
        nb_path (Union[Path, str, None]): Path for nb or folder with notebooks.

    Raises:
        sys.exit: If filename or dir not exists or not nb file.

    Returns:
        List[Path]: List of notebooks names.
    """
    path = Path(nb_path or ".")

    if not path.exists():
        rprint(f"{path} not exists!")
        sys.exit()

    if path.is_dir():
        return list(path.glob("*.ipynb"))

    if path.suffix != ".ipynb":
        rprint(f"Nb extension must be .ipynb, but got: {path.suffix}")
        sys.exit()

    return [path]


def get_readme_fn(nb_names: list[Path]) -> Path | None:
    """Find notebook for readme. Return filename or None.

    Args:
        nb_names (List[Path]): List of notebooks.

    Returns:
        Path | None: Filename or None.
    """
    for nb_name in nb_names:
        if nb_name.stem == "README":
            return nb_name
    return None


def process_readme(text: str) -> str:
    """Clear readme file - remove YAML Style Meta-Data."""
    if text.startswith("---"):
        text = "".join(text.split("---")[2:]).strip()
    return text
