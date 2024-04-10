"""
Helper functions for merging dictionaries
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def merge_dicts(*dicts: Optional[dict[Any, Any]]) -> dict[Any, Any]:
    """Merges a list of dictionaries

    Args:
        *dicts (Optional[dict[Any, Any]]): the list of dictionaries to be merged

    Returns:
        dict[Any, Any]: the merged dict
    """
    if len(dicts) == 0:
        return {}
    elif len(dicts) == 1:
        return dicts[0] if dicts[0] is not None else {}
    base, other = dicts[0], dicts[1:]
    if base is None:
        base = {}
    for o in other:
        base = _merge_dict(base, o)
    return base


def _merge_dict(
    base: dict[Any, Any], other: Optional[dict[Any, Any]]
) -> dict[Any, Any]:
    if other is None:
        return base
    new_dict: dict[Any, Any] = {}
    # Ignore type. Value type is partially unknown but we just need it to be a dict.
    all_keys = set().union(base.keys()).union(other.keys())  # type: ignore
    for key in all_keys:  # type: ignore
        if key not in other:
            new_dict[key] = base[key]
        elif key not in base:
            new_dict[key] = other[key]
        elif isinstance(base[key], dict):
            new_dict[key] = _merge_dict(base[key], other[key])  # type: ignore
        else:
            new_dict[key] = other[key] if other[key] is not None else base[key]
    return new_dict
