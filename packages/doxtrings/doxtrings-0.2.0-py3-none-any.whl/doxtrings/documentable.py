"""
Defines the Documentable class, used to represent any documentable code object
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, List, NamedTuple, Optional, Union


class DocumentableType(str, Enum):
    """Enumeration of the possible types of a Documentable"""

    FUNCTION = "function"
    """Functions"""
    CLASS = "class"
    """Classes"""
    METHOD = "method"
    """Class Methods"""
    ATTRIBUTE = "attribute"
    """Class Attributes"""
    CONSTANT = "constant"
    """Constants"""
    VARIABLE = "variable"
    """Variables"""
    MODULE = "module"
    """Modules"""


class Documentable(NamedTuple):
    """NamedTuple containing all the information of a code element that can be documented"""

    file: Path
    """The path to the file where this documentable is defined"""
    line: int
    """The line number where this documentable is defined"""
    name: str
    """The name of the documentable"""
    documentable_type: DocumentableType
    """The type of the documentable"""


ALL_DOCUMENTABLE_TYPES = tuple(
    doc_type.value for _, doc_type in DocumentableType.__members__.items()
)
"""A tuple containing all of the DocumentableTypes"""


class DiffReasons(str, Enum):
    """Enumeration of the possible reasons for a difference"""

    NO_DOCSTRING = "no docstring"
    """When there is no docstring"""
    MISSING = "missing"
    """When the docstring is missing any information found in the code"""
    EXTRA = "extra"
    """When the docstring has more information than found in the code"""
    CONFLICTING_VALUE = "conflicting values"
    """When the docstring and the code information are conflicting"""


class Diff(NamedTuple):
    """A named tuple used as the difference between the code and docstring data"""

    reason: DiffReasons
    """The reason for the difference."""
    location: List[Union[str, int]]
    """The location in the data where the difference was found."""
    code_value: Optional[Any] = None
    """The value found in the code at the Diff's location."""
    docstring_value: Optional[Any] = None
    """The value found in docstring at the Diff's location."""
