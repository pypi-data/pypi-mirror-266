""" Implements the class responsible for parsing each file into Documentables"""

import ast
import logging
from pathlib import Path
from typing import Dict, Generator, List, Optional, Tuple, Type

from doxtrings.config import DoXtringsConfig, get_config
from doxtrings.core.parser.node_parser import ParsingContext
from doxtrings.documentable import Diff, DiffReasons, Documentable

logger = logging.getLogger(__name__)

from doxtrings.core.parser.node_parser import (
    BaseNodeParser,
    ClassParser,
    FunctionParser,
    ModuleParser,
    VariablesParser,
)

_NodeParserMapping = Dict[Type[ast.AST], List[BaseNodeParser]]
"""Type alias to a mapping of node types to parsers"""


class DoXtringsAstParser:
    """Parser class that reads a file and returns a Generator of Documentables"""

    def __init__(self, config_file: Optional[str]):
        """Initializes the DoXtrings parser

        Args:
            config_file (Optional[str]): the config file, if given
        """
        self._config_file = config_file

    def parse_file(
        self, file: Path
    ) -> Generator[Tuple[Documentable, List[Diff]], None, None]:
        """Parses a file into a list of documentables

        Args:
            file (Path): path of the file to be parsed

        Yields:
            Generator[Tuple[Documentable, List[Diff]], None, None]: generator of tuples
            with documentables and an optional namedtuple with the docstring data.
        """
        logger.info(f"Parsing file {str(file)}")
        self._config = get_config(self._config_file, file)
        self._node_parser_mapping = _get_node_to_parser_mapping(self._config)
        self._filename = file.name
        self._filepath = file
        module = _ast_parse(file)
        return self._parse_ast_node(module)

    def _parse_ast_node(
        self,
        node: ast.AST,
        context: List[Type[ast.AST]] = [],
        next_node: Optional[ast.AST] = None,
        ignored_node: bool = False,
    ) -> Generator[Tuple[Documentable, List[Diff]], None, None]:
        parsers = self._node_parser_mapping.get(type(node), [])
        logger.debug(f"Parsing node {node} with {parsers}")
        for parser in parsers:
            node_data = parser.parse_node(
                node,
                ParsingContext(
                    self._filepath, self._filename, context, next_node, ignored_node
                ),
            )
            # If node is ignored, we mark all the next nodes parsed inside this one as ignored
            if node_data and self._is_documentable_ignored(node_data):
                ignored_node = True

            types_to_check = self._config.types_to_check or []

            if node_data and node_data.documentable_type in types_to_check:
                diffs = parser.get_diffs()
                logger.debug(f"Found data for node {node}")
                if len(diffs) and self._should_report_diffs(diffs, ignored_node):
                    logger.info(f"Found diffs for node {node}, yielding")
                    yield node_data, diffs

        # Traverse all child nodes
        assert (
            self._config.parsing_depth
        ), "Parsing depth must be set in the configuration"
        if len(context) < self._config.parsing_depth:
            for result in self._traverse_ast(
                node, context=context, ignored_node=ignored_node
            ):
                yield result

    def _traverse_ast(
        self, node: ast.AST, context: List[Type[ast.AST]], ignored_node: bool = False
    ) -> Generator[Tuple[Documentable, List[Diff]], None, None]:
        new_context = context + [type(node)]
        for _, value in ast.iter_fields(node):
            if isinstance(value, List):
                # We know nothing about type of item, so we check if item is AST
                # and ignore the type errors pylance complains below
                for i, item in enumerate(value):  # type:ignore
                    if isinstance(item, ast.AST):
                        next_node: Optional[ast.AST] = None
                        if i + 1 < len(value) and isinstance(  # type:ignore
                            value[i + 1], ast.AST
                        ):
                            next_node = value[i + 1]  # type:ignore
                        for result in self._parse_ast_node(
                            item, new_context, next_node, ignored_node  # type:ignore
                        ):
                            yield result

            elif isinstance(value, ast.AST):
                for result in self._parse_ast_node(
                    value, new_context, ignored_node=ignored_node
                ):
                    yield result

    def _is_documentable_ignored(self, documentable: Documentable) -> bool:
        ignore_rules = self._config.get_ignore_rules(documentable.documentable_type)
        ignore_matches = (
            [] if ignore_rules.ignore_matches is None else ignore_rules.ignore_matches
        )
        ignore_prefixes_rules = (
            []
            if ignore_rules.ignore_prefixes_rules is None
            else ignore_rules.ignore_prefixes_rules
        )
        include_prefixes_rules = (
            []
            if ignore_rules.include_prefixes_rules is None
            else ignore_rules.include_prefixes_rules
        )
        return any([documentable.name == ignored for ignored in ignore_matches]) or (
            documentable.name.startswith(tuple(ignore_prefixes_rules))
            and not documentable.name.startswith(tuple(include_prefixes_rules))
        )

    def _should_report_diffs(self, diffs: List[Diff], is_documentable_ignored: bool):
        # If documentable is ignored and config is set
        # not to fail if ignored are incorrect, we do not add it to report in any circumstance
        if is_documentable_ignored and self._config.fail_ignored_if_incorrect is False:
            return False

        # If the documentable is ignored and the only diff found for it is that the docstring
        # is missing, then we should ignore it as well
        if (
            is_documentable_ignored
            and len(diffs) == 1
            and diffs[0].reason == DiffReasons.NO_DOCSTRING
        ):
            return False

        # For all other cases, we do want to yield the diffs
        return True


def _get_node_to_parser_mapping(config: DoXtringsConfig) -> _NodeParserMapping:
    mapping: _NodeParserMapping = {}
    parsers = _load_node_parsers(config)
    for parser in parsers:
        _add_inputs_in_mapping(mapping, parser)
    return mapping


def _add_inputs_in_mapping(
    mapping: _NodeParserMapping,
    parser: BaseNodeParser,
):
    inputs = parser.get_input_types()
    for input in inputs:
        if input not in mapping:
            mapping[input] = []
        mapping[input].append(parser)


def _load_node_parsers(config: DoXtringsConfig) -> Tuple[BaseNodeParser, ...]:
    # TODO make this extensible
    return (
        FunctionParser(config),
        ClassParser(config),
        ModuleParser(config),
        VariablesParser(config),
    )


def _ast_parse(file: Path) -> ast.Module:
    file_content: str
    with file.open("r") as file_input:
        file_content = file_input.read()
    return ast.parse(file_content, file.name)
