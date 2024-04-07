import configparser
from pathlib import Path
from typing import List

import pytest

from nbdocs.cfg_tools import (
    NAMES,
    get_config,
    read_ini_config,
    get_config_name,
    NbDocsCfg,
)


def create_config(
    config_path: Path, config_name: str, section: str, arg_names: List[str]
) -> None:
    """create config file"""
    with open(config_path / config_name, "w", encoding="utf-8") as fh:
        fh.write(f"[{section}]\n")
        for arg in arg_names:
            fh.write(f"{arg} = test_{arg}\n")


def test_get_config_name_no_config(tmp_path: Path) -> None:
    """test get_config_name no config"""
    config_name = get_config_name(config_path=tmp_path)
    assert config_name is None
    cfg = get_config(config_path=tmp_path)
    assert isinstance(cfg, NbDocsCfg)
    assert cfg == NbDocsCfg()


def test_get_config_name_def():
    """test get_config_name default"""
    # default - load .nbdocs from app root
    config_name = get_config_name()
    assert config_name is not None
    assert config_name.name == NAMES[0]


def test_get_config_name_ini():
    """test get_config_name default"""
    # read config from tests folder
    config_name = get_config_name("tests/")
    assert config_name is not None
    assert config_name.name == NAMES[0]
    cfg = read_ini_config(config_name)
    assert cfg is not None
    assert isinstance(cfg, configparser.SectionProxy)


def test_get_config(tmp_path: Path) -> None:
    """test get_config"""
    # def - toml from root
    cfg = get_config()
    assert isinstance(cfg, NbDocsCfg)
    assert cfg.notebooks_path == "nbs"
    # ini from tests
    cfg = get_config("tests")
    assert isinstance(cfg, NbDocsCfg)
    assert cfg.notebooks_path == "nbs"
    # empty ini
    cfg_name = NAMES[0]
    create_config(tmp_path, cfg_name, "wrong_section", [])
    with pytest.raises(KeyError):
        cfg = get_config(tmp_path)

    create_config(tmp_path, cfg_name, "nbdocs", ["docs_path"])
    cfg = get_config(tmp_path, images_path="tst_images")
    assert cfg.docs_path == "test_docs_path"
    assert cfg.images_path == "tst_images"
