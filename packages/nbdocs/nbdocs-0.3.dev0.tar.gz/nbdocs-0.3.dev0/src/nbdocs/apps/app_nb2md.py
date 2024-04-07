import sys
from dataclasses import dataclass
from pathlib import Path

from argparsecfg import field_argument
from argparsecfg.app import app
from rich import print as rprint

from nbdocs.cfg_tools import get_config
from nbdocs.convert import convert2md, filter_changed
from nbdocs.core import get_nb_names


@dataclass
class AppConfig:
    nb_path: str = field_argument(
        "nb_path",
        help="Path to NB or folder with Nbs to convert",
    )
    dest_path: str = field_argument(
        default=None,
        flag="--dest",
        help="Docs path.",
    )
    images_path: str = field_argument(
        default=None,
        help="Image path at docs.",
    )
    force: bool = field_argument(
        "-F",
        default=False,
        action="store_true",
        help="Force convert all notebooks.",
    )
    silent_mode: bool = field_argument(
        "-s",
        default=False,
        action="store_true",
        help="Run in silent mode.",
    )


@app(
    description="Nb2Md. Convert notebooks to Markdown.",
)
def convert(
    app_cfg: AppConfig,
) -> None:
    """Nb2Md. Convert notebooks to Markdown."""
    nb_names = get_nb_names(app_cfg.nb_path)
    nbs_number = len(nb_names)
    if nbs_number == 0:
        rprint("No files to convert!")
        sys.exit()
    rprint(f"Found {nbs_number} notebooks.")

    cfg = get_config(
        notebooks_path=app_cfg.nb_path,
        docs_path=app_cfg.dest_path,
        images_path=app_cfg.images_path,
    )

    # check logic -> do we need subdir and how to check modified Nbs
    # if convert whole directory, put result to docs subdir.
    if (path := Path(app_cfg.nb_path)).is_dir():
        cfg.docs_path = f"{cfg.docs_path}/{path.name}"
    Path(cfg.docs_path).mkdir(parents=True, exist_ok=True)
    (Path(cfg.docs_path) / cfg.images_path).mkdir(exist_ok=True)

    if not app_cfg.force:
        message = "Filtering notebooks with changes... "
        nb_names = filter_changed(nb_names, cfg)
        if len(nb_names) == nbs_number:
            message += "No changes."
        rprint(message)

    if len(nb_names) == 0:
        rprint("No files with changes to convert!")
        sys.exit()

    if not app_cfg.silent_mode:
        print(f"Files to convert from {nb_names[0].parent}:")
        for fn in nb_names:
            print(f"    {fn.name}")
        print(f"Destination directory: {app_cfg.dest_path},\nImage directory: {cfg.images_path}")

    convert2md(nb_names, cfg)


if __name__ == "__main__":  # pragma: no cover
    convert()
