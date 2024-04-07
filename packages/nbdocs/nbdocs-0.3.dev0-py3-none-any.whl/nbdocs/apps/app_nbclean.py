import sys
from dataclasses import dataclass

from argparsecfg import field_argument
from argparsecfg.app import app
from rich import print as rprint

from nbdocs.cfg_tools import get_config
from nbdocs.clean import clean_nb_file
from nbdocs.core import get_nb_names


@dataclass
class AppConfig:
    """Config for `app_nbclean`."""

    nb_path: str = field_argument(
        "-p",
        flag="--path",
        default=None,
        help="Path to NB or folder with Nbs to clean. If no path - from cfg.",
    )
    clear_execution_count: bool = field_argument(
        flag="--no-ec",
        default=True,
        action="store_false",
        help="Dont clean execution counts.",
    )


# @app(
#     description="Clean Nb or notebooks at `nb_path` - metadata and execution counts from nbs."
# )
def nbclean(app_cfg: AppConfig) -> None:
    """Clean Nb or notebooks at `nb_path` - metadata and execution counts from nbs."""
    cfg = get_config(notebooks_path=app_cfg.nb_path)

    nb_names = get_nb_names(cfg.notebooks_path)

    if (num_nbs := len(nb_names)) == 0:
        rprint("No files to clean!")
        sys.exit()

    rprint(f"Clean: {cfg.notebooks_path}, found {num_nbs} notebooks.")

    cleaned = clean_nb_file(nb_names, app_cfg.clear_execution_count)
    if len(cleaned) == 0:
        rprint("All notebooks were clean.")


main = app(description="Clean Nb or notebooks at `nb_path` - metadata and execution counts from nbs.")(nbclean)


if __name__ == "__main__":  # pragma: no cover
    # nbclean()
    main()
