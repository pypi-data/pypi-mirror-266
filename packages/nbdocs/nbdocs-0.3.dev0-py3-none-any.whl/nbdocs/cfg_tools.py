from __future__ import annotations

import configparser
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path

from nbdocs.core import PathOrStr


@dataclass
class NbDocsCfg:
    """Config schema with default settings.
    Use config file for overwrite."""

    cfg_path: Path = Path(".")
    notebooks_path: str = "nbs"
    docs_path: str = "docs"
    images_path: str = "images"


# possible setting file names, section names to put config. If both exists first will be used.
# NAMES = [".nbdocs", "pyproject.toml"]
NAMES = ["nbdocs.ini"]
SECTION_NAME = "nbdocs"


def get_config_name(
    config_path: PathOrStr | None = None,
    config_names: list[str] | None = None,
) -> Path | None:
    """get cfg name"""
    cfg_path = Path(config_path or ".").absolute()
    config_names = config_names or NAMES
    # if at root - return None, no cfg
    if cfg_path == cfg_path.parent:
        return None

    for config_name in config_names:
        result = cfg_path / config_name
        if result.exists():
            return result

    return get_config_name(cfg_path.parent, config_names)


def read_ini_config(config_name: PathOrStr) -> configparser.SectionProxy:
    """return nbdocs config section from INI config."""
    cfg = ConfigParser()
    cfg.read(config_name)
    try:
        section = cfg[SECTION_NAME]
    except KeyError as exc:
        raise KeyError(f"No section {SECTION_NAME} at config file {config_name}") from exc
    return section


# def get_config_toml(config_name: PosixPath):
#     """return nbdocs config section from TOML config."""
#     cfg_tool = toml.load(config_name).get("tool", None)
#     if cfg_tool is not None:
#         return cfg_tool.get(SECTION_NAME, None)


def get_config(
    config_path: PathOrStr | None = None,
    config_names: list[str] | None = None,
    notebooks_path: str | None = None,
    docs_path: str | None = None,
    images_path: str | None = None,
) -> NbDocsCfg:
    """Read nbdocs config.

    Args:
        config_path (PosixPath, optional): Path to start search config. Defaults to None.
        config_names (List[str], optional): List of possible filenames. Defaults to None.

    Returns:
        Config: NbDocsCfg.
    """
    cfg_name = get_config_name(config_path, config_names)
    if cfg_name is not None:
        cfg = NbDocsCfg(**(read_ini_config(cfg_name)), cfg_path=cfg_name.parent)
    else:
        cfg = NbDocsCfg()
    if notebooks_path is not None:
        cfg.notebooks_path = notebooks_path
    if docs_path is not None:
        cfg.docs_path = docs_path
    if images_path is not None:
        cfg.images_path = images_path
    return cfg
