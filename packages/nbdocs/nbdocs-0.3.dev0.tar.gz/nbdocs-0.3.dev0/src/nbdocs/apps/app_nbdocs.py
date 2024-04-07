import sys
from dataclasses import dataclass
from pathlib import Path

from argparsecfg import field_argument
from argparsecfg.app import App
from rich import print as rprint

from nbdocs.apps.app_nbclean import nbclean
from nbdocs.cfg_tools import get_config
from nbdocs.convert import convert2md, filter_changed
from nbdocs.core import get_nb_names, get_readme_fn, process_readme
from nbdocs.default_settings import (
    FOOTER_HTML,
    MATERIAL_BASE,
    MKDOCS_BASE,
    NBDOCS_SETTINGS,
)


app = App(description="NbDocs. Convert notebooks to docs. Default to .md")


@dataclass
class AppConfig:
    force: bool = field_argument(
        "-F",
        default=False,
        action="store_true",
        help="Force convert all notebooks.",
    )


@app.main
def nbdocs(
    app_cfg: AppConfig,
) -> None:
    """NbDocs. Convert notebooks to docs. Default to .md"""
    cfg = get_config()
    # todo - add warning if no cfg
    nb_names = get_nb_names(cfg.notebooks_path)
    nbs_number = len(nb_names)
    if nbs_number == 0:
        rprint("No files to convert!")
        sys.exit()
    rprint(f"Found {nbs_number} notebooks.")
    if not app_cfg.force:
        message = "Filtering notebooks with changes... "
        nb_names = filter_changed(nb_names, cfg)
        if len(nb_names) == nbs_number:
            message += "No changes."
        rprint(message)

    if len(nb_names) == 0:
        rprint("No files to convert!")
        sys.exit()

    rprint(f"To convert: {len(nb_names)} notebooks.")
    convert2md(nb_names, cfg)
    readme_nb = get_readme_fn(nb_names)
    if readme_nb is not None:
        with open(f"{cfg.docs_path}/README.md", "r", encoding="utf-8") as fh:
            readme = fh.read()
        with open(f"{cfg.cfg_path}/README.md", "w", encoding="utf-8") as fh:
            fh.write(process_readme(readme))
        rprint("Readme updated.")


@dataclass
class SetupCfg:
    clean: bool = field_argument(
        "-c",
        default=False,
        action="store_true",
        help="Clean MkDocs setup.",
    )


@app.command
def setup(cfg: SetupCfg) -> None:
    """Initialize config."""
    rprint("Settings up NbDocs.")
    # create nbdocs config - nbdocs.ini
    with open("nbdocs.ini", "w", encoding="utf-8") as f:
        f.write(NBDOCS_SETTINGS)
    # create mkdocs config - mkdocs.yaml
    mkdocs_setup = MKDOCS_BASE
    if not cfg.clean:  # setting mkdocs material
        mkdocs_setup += MATERIAL_BASE
        # create footer with material
        filename = Path("docs/overrides/partials/copyright.html")
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(FOOTER_HTML)
    with open("mkdocs.yaml", "w", encoding="utf-8") as f:
        f.write(mkdocs_setup)
    rprint("Done.")


app.command(nbclean)


if __name__ == "__main__":
    app()
