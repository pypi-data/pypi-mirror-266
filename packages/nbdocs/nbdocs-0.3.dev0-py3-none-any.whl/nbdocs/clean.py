from __future__ import annotations

import nbformat
from nbconvert.exporters.exporter import ResourcesDict
from nbconvert.preprocessors.base import Preprocessor
from nbconvert.preprocessors.clearmetadata import ClearMetadataPreprocessor
from rich.progress import track

from nbdocs.core import PathOrStr, read_nb, write_nb
from nbdocs.typing import Cell, CellAndResources, Nb, NbAndResources, TPreprocessor


class ClearMetadataPreprocessorRes(ClearMetadataPreprocessor):
    """ClearMetadata Preprocessor same as at nbconvert
    but return True at resources.changed if nb changed."""

    def preprocess_cell(
        self,
        cell: Cell,
        resources: ResourcesDict,
        cell_index: int,
    ) -> CellAndResources:
        """
        All the code cells are returned with an empty metadata field.
        """
        if self.clear_cell_metadata:
            if cell.cell_type == "code":
                # Remove metadata
                if cell.metadata:
                    current_metadata = cell.metadata
                    cell, resources = super().preprocess_cell(cell, resources, cell_index)
                    if cell.metadata != current_metadata:
                        resources["changed"] = True
        return cell, resources

    def preprocess(self, nb: Nb, resources: ResourcesDict) -> NbAndResources:
        """
        Preprocessing to apply on each notebook.

        Must return modified nb, resources.

        Parameters
        ----------
        nb : Notebook
            Notebook being converted
        resources : dictionary
            Additional resources used in the conversion process.  Allows
            preprocessors to pass variables into the Jinja engine.
        """
        if self.clear_notebook_metadata:
            if nb.metadata:
                current_metadata = nb.metadata
                nb, resources = super().preprocess(nb, resources)
                if nb.metadata != current_metadata:
                    resources["changed"] = True
        for index, cell in enumerate(nb.cells):
            nb.cells[index], resources = self.preprocess_cell(cell, resources, index)
        return nb, resources


class ClearExecutionCountPreprocessor(Preprocessor):
    """
    Clear execution_count from all code cells in a notebook.
    """

    def preprocess_cell(
        self,
        cell: Cell,
        resources: ResourcesDict,
        index: int,
    ) -> CellAndResources:
        """
        Apply a transformation on each cell. See base.py for details.
        """
        if cell.cell_type == "code":
            if cell.execution_count is not None:
                cell.execution_count = None
                resources["changed"] = True
            for output in cell.outputs:
                if "execution_count" in output:
                    if output.execution_count is not None:
                        output.execution_count = None
                        resources["changed"] = True
        return cell, resources


class MetadataCleaner:
    """Metadata cleaner.
    Wrapper for metadata and execution count preprocessors.
    """

    def __init__(self) -> None:
        self.cleaner_metadata: TPreprocessor = ClearMetadataPreprocessorRes(enabled=True)
        self.cleaner_execution_count: TPreprocessor = ClearExecutionCountPreprocessor(enabled=True)

    def __call__(
        self,
        nb: Nb,
        resources: ResourcesDict | None = None,
        clear_execution_count: bool = True,
    ) -> NbAndResources:
        if resources is None:
            resources = ResourcesDict()
        nb, resources = self.cleaner_metadata(nb, resources)
        if clear_execution_count:
            nb, resources = self.cleaner_execution_count(nb, resources)
        return nb, resources


def clean_nb(nb: Nb, clear_execution_count: bool = True) -> NbAndResources:
    """Clean notebook metadata and execution_count.

    Args:
        nb (Notebook): Notebook to clean.
        clear_execution_count (bool, optional): Clear execution_count. Defaults to True.
    """
    cleaner = MetadataCleaner()
    return cleaner(nb, clear_execution_count=clear_execution_count)


def clean_nb_file(
    fn: PathOrStr | list[PathOrStr],
    clear_execution_count: bool = True,
    as_version: nbformat.Sentinel = nbformat.NO_CONVERT,
    silent: bool = False,
) -> list[PathOrStr]:
    """Clean metadata and execution count from notebook.

    Args:
        fn (Union[str, PosixPath]): Notebook filename or list of names.
        as_version (int, optional): Nbformat version. Defaults to 4.
        clear_execution_count (bool, optional): Clean execution count. Defaults to True.
        silent (bool, optional): Silent mode. Defaults to False.
    """
    cleaner = MetadataCleaner()
    if not isinstance(fn, list):
        fn = [fn]
    cleaned: list[PathOrStr] = []
    for fn_item in track(fn, transient=True):
        nb = read_nb(fn_item, as_version)
        nb, resources = cleaner(nb, clear_execution_count=clear_execution_count)
        if resources["changed"]:
            cleaned.append(fn_item)
            write_nb(nb, fn_item, as_version)
            if not silent:
                print(f"done: {fn_item}")
    return cleaned
