"""
Defines the functions to build the configuration
"""

from __future__ import annotations

import json
import logging
from dataclasses import fields
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple, Union

import tomli

from doxtrings.config.merge import merge_dicts
from doxtrings.config.models import DoXtringsConfig, IgnoreRules, NodeIgnoreRules
from doxtrings.documentable import ALL_DOCUMENTABLE_TYPES

_DEFAULT_CONFIG_FILES = (
    "pyproject.toml",
    "doxtrings.toml",
    ".doxtrings.toml",
    "doxtrings.json",
    ".doxtrings.json",
)

logger = logging.getLogger(__name__)

"""

- get_config(path, extras)
    - full_dict = _get_full_config() # cached
    - default_config = _get_default_config()
    - root_cfg = _get_root_config() # cached dict
    - path_cfg = _get_config_for_path() # cached dict
    - merged = merge_dicts()
    -

"""


def _get_default_config_dict():
    return {
        "exclude_files": ["env", "venv", ".env", ".venv", "test/"],
        "include_file_extensions": [".py"],
        "types_to_check": list(ALL_DOCUMENTABLE_TYPES),
        "docstring_format": "google",
        "parsing_depth": 2,
        "fail_fast": False,
        "fail_ignored_if_incorrect": True,
        "ignore_rules": {
            "default": None,
            "callables": None,
            "functions": None,
            "methods": None,
            "classes": None,
            "modules": None,
            "assignments": None,
            "attributes": None,
            "constants": None,
            "variables": None,
        },
    }


_CONFIG_FIELDS = tuple(f.name for f in fields(DoXtringsConfig))
_IGNORE_RULES_FIELDS = tuple(f.name for f in fields(IgnoreRules))
_NODE_IGNORE_RULES_FIELDS = tuple(f.name for f in fields(NodeIgnoreRules))


class InvalidConfigFileTypeError(Exception):
    """Exception raised if configuration file is in invalid format"""


def get_config(
    config_file: Union[Path, str, None], path: Union[Path, str, None] = None
) -> DoXtringsConfig:
    """Gets the DoXtrings config based on a config file and the current path

    Args:
        config_file (Union[Path, str, None]): the configuration file.
        path (Union[Path, str, None], optional): The current path. This is needed to resolve the subconfigs.
            If None, will ignore subconfigs. Defaults to None.

    Returns:
        DoXtringsConfig: the config
    """
    default_config = _get_default_config_dict()
    # Full config is cached, we must get a copy to avoid modifying the cached version
    full_cfg = _read_full_config(config_file).copy()
    sub_configs = full_cfg.pop("sub_configs", [])
    path_configs = _get_path_configs(sub_configs, path) if path else []
    merged = merge_dicts(default_config, full_cfg, *path_configs)
    return _build_config(merged)


@lru_cache()
def _read_full_config(config_file: Union[Path, str, None] = None) -> Dict[str, Any]:
    if config_file:
        if not Path(config_file).is_file():
            raise FileNotFoundError(f"File {config_file} does not exist")
    config_files = (
        [Path(config_file)]
        if config_file is not None
        else [Path(f) for f in _DEFAULT_CONFIG_FILES]
    )
    for file_path in config_files:
        logger.info(f"Looking for config file at {str(file_path)}")
        cfg_dict = _load_cfg_if_exists(file_path)
        if cfg_dict is not None:
            logger.info(f"Read config file {str(file_path)}")
            return cfg_dict
    return {}


def _get_path_configs(
    sub_configs: List[Dict[str, Any]], path: Union[Path, str]
) -> List[Dict[str, Any]]:
    assert isinstance(sub_configs, List), "Sub configurations must be a list"
    current_path = Path(path).resolve()
    found_subconfigs: Dict[int, Dict[str, Any]] = {}
    for cfg in sub_configs:
        if "path" not in cfg:
            raise TypeError("Missing `path` attribute for sub configuration")
        absolute_path = Path(cfg["path"]).resolve()
        if _is_path_relative_to(absolute_path, current_path):
            specificity_level = len(absolute_path.parents)
            found_subconfigs[specificity_level] = cfg
    return [t[1] for t in sorted(found_subconfigs.items())]


def _build_config(
    cfg_dict: Dict[str, Any],
) -> DoXtringsConfig:
    _check_fields(cfg_dict, valid_fields=_CONFIG_FIELDS)
    ignore_rules_rules_dict = cfg_dict.pop("ignore_rules") or {}
    _check_fields(
        ignore_rules_rules_dict,
        valid_fields=_NODE_IGNORE_RULES_FIELDS,
        field_prefix="ignore_rules.",
    )
    ignore_rules_rules_kwargs: Dict[str, IgnoreRules] = {}
    for field in _NODE_IGNORE_RULES_FIELDS:
        ignore_dict: Dict[str, Any] = ignore_rules_rules_dict.get(field) or {}
        _check_fields(
            ignore_dict,
            valid_fields=_IGNORE_RULES_FIELDS,
            field_prefix=f"ignore_rules.{field}.",
        )
        ignore_rules_rules_kwargs[field] = IgnoreRules(**ignore_dict)
    ignore_rules_rules = NodeIgnoreRules(**ignore_rules_rules_kwargs)

    return DoXtringsConfig(
        **cfg_dict,
        ignore_rules=ignore_rules_rules,
    )


def _check_fields(
    cfg_dict: Dict[str, Any], valid_fields: Tuple[str, ...], field_prefix: str = ""
):
    invalid_fields: List[str] = []
    for key in cfg_dict.keys():
        if key not in valid_fields:
            invalid_fields.append(field_prefix + key)
    if len(invalid_fields) > 0:
        raise TypeError(
            f"Unexpected DoXtringsConfig fields: {', '.join(sorted(invalid_fields))}"
        )


def _load_cfg_if_exists(cfg_path: Path) -> Optional[Dict[str, Any]]:
    if cfg_path.exists() and cfg_path.is_file():
        parsed_dict = _parse_file(cfg_path)
        # If file is pyproject.toml, get only the correct section
        if cfg_path.name == "pyproject.toml":
            logger.info(
                f"Config file is pyproject.toml, will look for specific section"
            )
            toml_dict = _get_pyproject_toml_section(parsed_dict)
            if toml_dict is None:
                logger.info(f"doxtrings config not found in pyproject.toml")
                return None
            else:
                parsed_dict = toml_dict
        return parsed_dict
    else:
        return None


def _parse_file(cfg_path: Path) -> Dict[str, Any]:
    parser_module = _get_parser_module(cfg_path)
    with cfg_path.open("rb") as cfg_file:
        parsed_dict: Dict[str, Any] = parser_module.load(cfg_file)

        return parsed_dict


def _get_parser_module(cfg_file: Path) -> ModuleType:
    if cfg_file.suffix == ".toml":
        return tomli
    elif cfg_file.suffix == ".json":
        return json
    else:
        raise InvalidConfigFileTypeError(
            f"Allowed config types are '.toml' and '.json', but found '{cfg_file.suffix}'"
        )


def _get_pyproject_toml_section(
    parsed_dict: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    try:
        return parsed_dict["tool"]["doxtrings"]
    except:
        return None


def _is_path_relative_to(parent: Path, child: Path) -> bool:
    # python 3.8 does not support is_relative_to, so we need this workaround
    return parent == child or parent in child.parents
