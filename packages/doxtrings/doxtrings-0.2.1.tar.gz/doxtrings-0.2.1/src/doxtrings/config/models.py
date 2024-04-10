"""
Defines the doXtrings configuration object models
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from typing import List, Optional, Union

from doxtrings.documentable import ALL_DOCUMENTABLE_TYPES, DocumentableType

from .merge import merge_dicts

logger = logging.getLogger(__name__)


@dataclass
class IgnoreRules:
    """
    Stores the ignore rules configuration.
    """

    ignore_prefixes_rules: Optional[List[str]] = None
    """
    A list of prefixes to Documentable's names that will mark them as ignored in the report.
    Defaults to empty list.
    """
    include_prefixes_rules: Optional[List[str]] = None
    """
    A list of Documentable's name prefixes that will NOT be ignored in the report.
    Defaults to an empty list.
    """
    ignore_matches: Optional[List[str]] = None
    """
    A list of Documentable's names that will be ignored in the report.
    Defaults to empty list.
    """
    ignore_typing: Optional[bool] = None
    """
    If set to True, will not require typing information in the docstring.
    Defaults to None. Prefer using `get_ignore_typing` to get the value of this attribute,
    as it will account for `None` values.
    """
    ignore_arguments: Optional[bool] = None
    """
    If set to True, will not require arguments information in the docstring.
    Defaults to None. Prefer using `get_ignore_arguments` to get the value of this attribute,
    as it will account for `None` values.
    """
    ignore_return_type: Optional[bool] = None
    """
    If set to True, will not require return type information in the docstring.
    Defaults to None. Prefer using `get_ignore_return_type` to get the value of this attribute,
    as it will account for `None` values.
    """
    ignore_args_and_kwargs: Optional[bool] = None
    """
    If set to True, will not require *args and **kwargs in the docstring.
    Defaults to None. Prefer using `get_ignore_args_and_kwargs` to get the value of this attribute,
    as it will account for `None` values.
    """

    def get_ignore_typing(self) -> bool:
        """Gets ignore_typing value. Defaults to False if ignore_typing is None.

        Returns:
            bool: the ignore_typing property or False if not set
        """
        return False if self.ignore_typing is None else self.ignore_typing

    def get_ignore_arguments(self) -> bool:
        """Gets ignore_arguments value. Defaults to False if ignore_arguments is None.

        Returns:
            bool: the ignore_arguments property or False if not set
        """
        return False if self.ignore_arguments is None else self.ignore_arguments

    def get_ignore_return(self) -> bool:
        """Gets ignore_return value. Defaults to False if ignore_return is None.

        Returns:
            bool: the ignore_return property or False if not set
        """
        return False if self.ignore_return_type is None else self.ignore_return_type

    def get_ignore_args_and_kwargs(self) -> bool:
        """Gets ignore_args_and_kwargs value. Defaults to False if ignore_args_and_kwargs is None.

        Returns:
            bool: the ignore_args_and_kwargs property or False if not set
        """
        return (
            False
            if self.ignore_args_and_kwargs is None
            else self.ignore_args_and_kwargs
        )


@dataclass
class NodeIgnoreRules:
    """
    A series of IgnoreRules to be applied to specific types.
    """

    default: Optional[IgnoreRules] = None
    """Ignore Rules for all documentables"""
    callables: Optional[IgnoreRules] = None
    """Ignore Rules for all callables (functions and methods)"""
    functions: Optional[IgnoreRules] = None
    """Ignore Rules for all functions"""
    methods: Optional[IgnoreRules] = None
    """Ignore Rules for all methods"""
    classes: Optional[IgnoreRules] = None
    """Ignore Rules for classes"""
    modules: Optional[IgnoreRules] = None
    """Ignore Rules for modules"""
    assignments: Optional[IgnoreRules] = None
    """Ignore Rules for all assignments (attributes, constants and variables)"""
    attributes: Optional[IgnoreRules] = None
    """Ignore Rules for attributes"""
    constants: Optional[IgnoreRules] = None
    """Ignore Rules for constants"""
    variables: Optional[IgnoreRules] = None
    """Ignore Rules for variables"""


@dataclass
class DoXtringsConfig:
    """
    Class that stores all DoXtrings configuration.
    """

    path: str = "./"
    """
    The root directory from where doxtrings will run the scan. Defaults to the current directory.
    """
    exclude_files: Optional[List[str]] = None
    """
    A list of files or directories to be excluded from the scan.
    Defaults to `["env", "venv", ".env", ".venv", "test/"]`
    """
    include_file_extensions: Optional[List[str]] = None
    """
    A list of file extensions that will be scanned.
    Defaults to `[".py"]`
    """
    types_to_check: Optional[List[str]] = None
    """
    A list with the types of Documentables that will be reported. Defaults to the list of all
    the available types (doxtrings.documentable:ALL_DOCUMENTABLE_TYPES)
    """
    docstring_format: Optional[str] = None
    """
    The docstring format to use when parsing the docstring data. Possible values are "google",
    "epydoc", "rest" or "numpydoc". Defaults to "google".
    """

    parsing_depth: Optional[int] = None
    """
    How deep into the AST doxtrings will scan. Default value is 2.
    Using value of depth 2 means it will scan the root of a module and the first level of nesting,
    allowing for methods and attributes in classes to be scanned.
    """
    fail_fast: Optional[bool] = None
    """If set to `True`, the scan will stop at the first difference found. Defaults to `False`"""

    fail_ignored_if_incorrect: Optional[bool] = None
    """
    If set to `True`, documentables marked as ignored will still be added to the report if their
    docstring is not missing but is incorrect. Ignored types will also be added if incorrect.
    Defaults to `True`.
    """

    ignore_rules: Optional[NodeIgnoreRules] = None
    """
    A dictionary of ignore rules specific for each type of documentable where the keys are the
    documentable types and the values are the specific rules. If any rule is specified
    it will override the default ignore rules for that type of documentable.
    """

    def get_ignore_rules(self, type: Union[DocumentableType, str]) -> IgnoreRules:
        """Gets the ignore rules based on the type of documentable

        Args:
            type (Union[DocumentableType, str]): the type of documentable

        Raises:
            ValueError: If `type` is not a valid documentable type

        Returns:
            IgnoreRules: Returns the ignore rules for the specific type
        """
        if type not in ALL_DOCUMENTABLE_TYPES:
            raise ValueError(
                f"Cannot get ignore filter for {type}. Valid types are {ALL_DOCUMENTABLE_TYPES}"
            )
        type_str = type.value if isinstance(type, DocumentableType) else type
        node_rules = self.ignore_rules or NodeIgnoreRules()
        if type_str == DocumentableType.FUNCTION.value:
            return _merge_rules(
                node_rules.functions,
                node_rules.callables,
                node_rules.default,
            )
        elif type_str == DocumentableType.METHOD.value:
            return _merge_rules(
                node_rules.methods,
                node_rules.callables,
                node_rules.default,
            )
        elif type_str == DocumentableType.CLASS.value:
            return _merge_rules(node_rules.classes, node_rules.default)
        elif type_str == DocumentableType.MODULE.value:
            return _merge_rules(node_rules.modules, node_rules.default)
        elif type_str == DocumentableType.ATTRIBUTE.value:
            return _merge_rules(
                node_rules.attributes,
                node_rules.assignments,
                node_rules.default,
            )
        elif type_str == DocumentableType.VARIABLE.value:
            return _merge_rules(
                node_rules.variables,
                node_rules.assignments,
                node_rules.default,
            )
        elif type_str == DocumentableType.CONSTANT.value:
            return _merge_rules(
                node_rules.constants,
                node_rules.assignments,
                node_rules.default,
            )
        else:
            raise NotImplementedError(
                f"Config does not have support for {type}, even though type is valid"
            )


@dataclass
class DoXtringsRootConfig(DoXtringsConfig):
    """
    Class that stores all DoXtrings configuration.
    """

    sub_configs: List[DoXtringsConfig] = field(default_factory=list)
    """
    Sub configurations for different sub-paths.
    """


# TODO remove from models
def _merge_rules(
    base: Optional[IgnoreRules], *mergeables: Optional[IgnoreRules]
) -> IgnoreRules:
    """
    Returns a merged version of the provided IgnoreFilters.
    Merge happens from left to right, meaning values in the leftmost filters will be
    overwritten by the rightmost ones.

    Args:
        base (Optional[IgnoreRules]): the base filter to be merged into the others.
        *mergeables (Optional[IgnoreRules]): the other filters to be merged.

    Returns:
        IgnoreRules: the merged version of the filters.
    """
    not_none = reversed([r for r in (base,) + mergeables if r is not None])
    merged_dicts = merge_dicts(*[asdict(r) for r in not_none])
    return IgnoreRules(**merged_dicts)
