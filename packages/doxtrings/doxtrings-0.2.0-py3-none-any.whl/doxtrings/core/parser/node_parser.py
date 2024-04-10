""" Implements classes capable of parsing both the AST nodes and the docstrings into Documentables"""

import ast
import logging
from abc import ABC, abstractmethod
from difflib import SequenceMatcher
from itertools import zip_longest
from pathlib import Path
from typing import Any, List, NamedTuple, Optional, Set, Tuple, Type, Union

import docstring_parser as dp

from doxtrings.config import DoXtringsConfig, IgnoreRules
from doxtrings.documentable import Diff, DiffReasons, Documentable, DocumentableType

logger = logging.getLogger(__name__)


class EmptyTuple(NamedTuple):
    """An empty tuple used when there is no relevant data to be stored"""


class ParsingContext(NamedTuple):
    """
    This is a context regarding a node that is being parsed.
    Includes the filename and the parent nodes. This is useful to determine if a function is a
    method, for instance.
    """

    filepath: Path
    """The path to the file being parsed"""
    filename: str
    """The name of the file being parsed"""
    parent_node_types: List[Type[ast.AST]]
    """A list with the types of the parent nodes of the current node being parsed"""
    next_node: Optional[ast.AST]
    """The node next to this one, if there is any"""
    is_ignored: bool
    """Wether this node is marked as ignored"""


class BaseNodeParser(ABC):
    """Defines the base interface for a node parser"""

    _input: ast.AST
    _context: ParsingContext
    _name: str
    _documentable_type: Optional[DocumentableType]
    _lineno: int

    def __init__(self, config: DoXtringsConfig):
        """Initializes the parser

        Args:
            config (DoXtringsConfig): the DoXtrings configuration

        """
        self._config = config

    @classmethod
    @abstractmethod
    def get_input_types(cls) -> Set[Type[ast.AST]]:
        """Returns a set with the AST types this parser can parse from

        Returns:
            Set[Type[ast.AST]]: the set of AST types this parser class can parse from
        """

    @classmethod
    @abstractmethod
    def get_output_types(cls) -> Set[DocumentableType]:
        """Returns a set with the DocumentableTypes this parser can parse to

        Returns:
            Set[DocumentableType]: a set with the DocumentableTypes this parser can parse to
        """

    def parse_node(
        self,
        input: ast.AST,
        context: ParsingContext,
    ) -> Optional[Documentable]:
        """Concrete method an AST node into a Documentable. Usually should not be overwritten by
        child classes. Child classes should instead implement `_parse_node`.

        Args:
            input (ast.AST): the AST node to be parsed
            context (ParsingContext): the parsing context for this node

        Returns:
            Optional[Documentable]: the parsed Documentable. Might be None if the parser could
            not parse the input.
        """
        self._input = input
        self._context = context
        self._name = self._get_node_name()
        self._documentable_type = self._get_documentable_type()
        self._lineno = input.lineno if hasattr(input, "lineno") else 0
        if self._documentable_type:
            self._code_data = self._parse_node()
            self._docstring_data = self._parse_docstring()
            return Documentable(
                file=self._context.filepath,
                line=self._lineno,
                name=self._name,
                documentable_type=self._documentable_type,
            )
        else:
            self._code_data = None
            self._docstring_data = None

    def get_diffs(self) -> List[Diff]:
        """Gets the list of diffs for the node

        Returns:
            List[Diff]: List of Diffs for the node
        """
        if self._docstring_data is None:
            return [
                Diff(DiffReasons.NO_DOCSTRING, location=[], code_value=self._code_data)
            ]
        elif self._docstring_data != self._code_data:
            return [
                Diff(
                    DiffReasons.CONFLICTING_VALUE,
                    location=[],
                    code_value=self._code_data,
                    docstring_value=self._docstring_data,
                )
            ]
        else:
            return []

    def _get_error_location_msg(self):
        return (
            f"Error found at {self._documentable_type} {self._name} at "
            f"{self._context.filepath}:{self._lineno}. "
        )

    def _get_node_name(self) -> str:
        """Gets the name of the input node.

        Returns:
            str: the name of the documentable
        """
        if hasattr(self._input, "name"):
            return str(self._input.name)  # type: ignore (we just checked for this attribute)
        else:
            raise NotImplementedError(
                self._get_error_location_msg()
                + f"`_get_node_name` not implemented for {type(self)} and default implementation failed"
            )

    def _get_documentable_type(self) -> Optional[DocumentableType]:
        """Determines the input node's type of the Documentable

        Returns:
            Optional[DocumentableType]: the documentable type.
                If None, this means this parser could not parse the node.
        """
        outputs = self.get_output_types()
        if len(outputs) == 1:
            return outputs.pop()
        else:
            raise NotImplementedError(
                self._get_error_location_msg()
                + f"`_get_documentable_type` not implemented for {self} and default implementation failed"
            )

    def _parse_node(
        self,
    ) -> NamedTuple:
        """Parses the AST node into a NamedTuple.

        Returns:
            NamedTuple: the parsed NamedTuple. Might be None if
            the parser could not parse the input.
        """
        return EmptyTuple()

    @abstractmethod
    def _parse_docstring(self) -> Optional[NamedTuple]:
        """Parses the node's docstring into a NamedTuple.

        Returns:
            Optional[NamedTuple]: the parsed NamedTuple. Might be None if there is no docstring.
        """


class ModuleParser(BaseNodeParser):
    """Parser for module nodes"""

    @classmethod
    def get_input_types(cls) -> Set[Type[ast.AST]]:
        """Returns a set with the AST types this parser can parse from.

        Returns:
            Set[Type[ast.AST]]: returns `set([ast.Module])`
        """
        return set([ast.Module])

    @classmethod
    def get_output_types(cls) -> Set[DocumentableType]:
        """Returns a set with the DocumentableTypes this parser can parse to

        Returns:
            Set[DocumentableType]: returns `set([DocumentableType.MODULE])`
        """
        return set([DocumentableType.MODULE])

    def _get_node_name(self) -> str:
        """
        Gets the name of the module. Because module nodes do not have a name attribute,
        we get the name from the context's filename

        Returns:
            str: the name of the documentable
        """
        return self._context.filename.rpartition(".")[0]

    def _parse_docstring(self) -> Optional[EmptyTuple]:
        """
        Parses the node's docstring into an EmptyTuple. There is no relevant data to be checked in
        the module docstring, so we just return the EmptyTuple if we find a docstring.

        Returns:
            Optional[EmptyTuple]: returns an EmptyTuple if there is a docstring for the module.
        """
        assert isinstance(self._input, ast.Module)
        docstring = ast.get_docstring(self._input)
        if docstring and len(docstring.strip()):
            return EmptyTuple()
        return None


class VariablesParser(BaseNodeParser):
    """Parser for attribute nodes"""

    @classmethod
    def get_input_types(cls) -> Set[Type[ast.AST]]:
        """Returns a set with the AST types this parser can parse from.

        Returns:
            Set[Type[ast.AST]]: returns `set([ast.ClassDef])`
        """
        return set([ast.Assign, ast.AnnAssign])

    @classmethod
    def get_output_types(cls) -> Set[DocumentableType]:
        """Returns a set with the DocumentableTypes this parser can parse to

        Returns:
            Set[DocumentableType]: returns `set([DocumentableType.CLASS])`
        """
        return set(
            [
                DocumentableType.CONSTANT,
                DocumentableType.ATTRIBUTE,
                DocumentableType.VARIABLE,
            ]
        )

    def _parse_docstring(self) -> Optional[EmptyTuple]:
        """
        Parses the node's docstring into an EmptyTuple. There is no relevant data to be checked in
        the variable's docstring, so we just return the EmptyTuple if we find a docstring.

        Returns:
            Optional[EmptyTuple]: returns an EmptyTuple if there is a docstring for the class.
        """
        assert isinstance(self._input, (ast.Assign, ast.AnnAssign))
        docstring = VariablesParser._get_variable_docstring(self._context.next_node)
        if docstring and len(docstring.strip()):
            return EmptyTuple()
        return None

    def _get_node_name(self) -> str:
        """Gets the name of the input node.

        Returns:
            str: the name of the documentable
        """
        opt_name = self._get_node_name_opt()
        return opt_name if opt_name else ""

    def _get_node_name_opt(self) -> Optional[str]:
        """Gets the optional name of the input node.

        Returns:
            Optional[str]: the name of the documentable or `None` if it is not a valid documentable
        """
        assert isinstance(self._input, (ast.Assign, ast.AnnAssign))
        ann_assign_name = VariablesParser._get_ann_assign_name(self._input)
        assign_name = VariablesParser._get_assign_name(self._input)
        return ann_assign_name if ann_assign_name else assign_name

    def _get_documentable_type(self) -> Optional[DocumentableType]:
        """Determines the input node's type of the Documentable

        Returns:
            Optional[DocumentableType]: the documentable type.
                If None, this means this parser could not parse the node.
        """
        name = self._get_node_name_opt()
        if not name:
            return None

        # Constants and Variables are only considered when in the root of the module
        if len(self._context.parent_node_types) == 1:
            # Here, what what differs a constant from a variable is only the case of the name
            if name == name.upper():
                return DocumentableType.CONSTANT
            else:
                return DocumentableType.VARIABLE
        elif self._context.parent_node_types[-1] == ast.ClassDef:
            return DocumentableType.ATTRIBUTE
        else:
            return None

    @staticmethod
    def _get_ann_assign_name(node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            return node.target.id
        else:
            return None

    @staticmethod
    def _get_assign_name(node: ast.AST) -> Optional[str]:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            return node.targets[0].id
        else:
            return None

    @staticmethod
    def _get_variable_docstring(next_node: Optional[ast.AST]):
        if (
            next_node
            and isinstance(next_node, ast.Expr)
            and isinstance(next_node.value, ast.Constant)
            and isinstance(next_node.value.value, str)
        ):
            return next_node.value.value
        else:
            return None


class ClassParser(BaseNodeParser):
    """Parser for class nodes"""

    @classmethod
    def get_input_types(cls) -> Set[Type[ast.AST]]:
        """Returns a set with the AST types this parser can parse from.

        Returns:
            Set[Type[ast.AST]]: returns `set([ast.ClassDef])`
        """
        return set([ast.ClassDef])

    @classmethod
    def get_output_types(cls) -> Set[DocumentableType]:
        """Returns a set with the DocumentableTypes this parser can parse to

        Returns:
            Set[DocumentableType]: returns `set([DocumentableType.CLASS])`
        """
        return set([DocumentableType.CLASS])

    def _parse_docstring(self) -> Optional[EmptyTuple]:
        """
        Parses the node's docstring into an EmptyTuple. There is no relevant data to be checked in
        the class docstring, so we just return the EmptyTuple if we find a docstring.

        Returns:
            Optional[EmptyTuple]: returns an EmptyTuple if there is a docstring for the class.
        """
        assert isinstance(self._input, ast.ClassDef)
        docstring = ast.get_docstring(self._input)
        if docstring and len(docstring.strip()):
            return EmptyTuple()
        return None


class FunctionArgument(NamedTuple):
    """relevant data of a function argument"""

    name: str
    """Name of the function argument"""
    type_hint: Optional[str]
    """Function argument type hint"""


class FunctionData(NamedTuple):
    """Relevant data for a function"""

    arguments: Tuple[FunctionArgument, ...]
    """The function arguments as a tuple of FunctionArgument"""
    return_type: Optional[str]
    """the return type of the function"""


class FunctionParser(BaseNodeParser):
    """Parser for function nodes"""

    _code_data: FunctionData
    _docstring_data: Optional[FunctionData]

    # TODO move this to config
    _DOCSTRING_STYLES = {
        "google": dp.DocstringStyle.GOOGLE,
        "epydoc": dp.DocstringStyle.EPYDOC,
        "rest": dp.DocstringStyle.REST,
        "numpydoc": dp.DocstringStyle.NUMPYDOC,
    }

    @classmethod
    def get_input_types(cls) -> Set[Type[ast.AST]]:
        """Returns a set with the AST types this parser can parse from.

        Returns:
            Set[Type[ast.AST]]: returns `set([ast.FunctionDef, ast.AsyncFunctionDef])`
        """
        return set([ast.FunctionDef, ast.AsyncFunctionDef])

    @classmethod
    def get_output_types(cls) -> Set[DocumentableType]:
        """Returns a set with the DocumentableTypes this parser can parse to

        Returns:
            Set[DocumentableType]: returns `set([DocumentableType.FUNCTION, DocumentableType.METHOD])`
        """
        return set([DocumentableType.FUNCTION, DocumentableType.METHOD])

    def _get_documentable_type(self) -> Optional[DocumentableType]:
        """Determines the input node's type of the Documentable

        Returns:
            Optional[DocumentableType]: the documentable type.
                If None, this means this parser could not parse the node.
        """
        return (
            DocumentableType.METHOD
            if self._context.parent_node_types[-1] == ast.ClassDef
            else DocumentableType.FUNCTION
        )

    def _parse_node(
        self,
    ) -> FunctionData:
        assert isinstance(self._input, (ast.FunctionDef, ast.AsyncFunctionDef))
        is_method = self._documentable_type == DocumentableType.METHOD
        ordered_args = (
            self._input.args.posonlyargs
            + self._input.args.args
            + FunctionParser._prepare_vararg(self._input.args.vararg, "*")
            + self._input.args.kwonlyargs
            + FunctionParser._prepare_vararg(self._input.args.kwarg, "**")
        )

        if is_method and len(ordered_args):
            # Removing self or cls from docstrings
            if ordered_args[0].arg == "self" or ordered_args[0].arg == "cls":
                ordered_args.pop(0)

        function_args = tuple(self._get_arg_data(arg) for arg in ordered_args)
        return_type = self._get_type_annotation(self._input.returns)
        return FunctionData(arguments=function_args, return_type=return_type)

    @staticmethod
    def _prepare_vararg(arg: Optional[ast.arg], prefix: str) -> List[ast.arg]:
        if arg is None:
            return []
        arg.arg = prefix + arg.arg
        return [arg]

    def _get_arg_data(self, arg: ast.arg) -> FunctionArgument:
        return FunctionArgument(
            name=arg.arg, type_hint=self._get_type_annotation(arg.annotation)
        )

    def _get_type_annotation(
        self, annotation_node: Optional[ast.expr]
    ) -> Optional[str]:
        type_hint: Optional[str] = None
        if annotation_node is None:
            return type_hint
        elif isinstance(annotation_node, ast.Name):
            type_hint = str(annotation_node.id)
        elif isinstance(annotation_node, ast.Constant):
            type_hint = self._get_constant_string_value(annotation_node.value)

        # Recursive methods
        elif isinstance(annotation_node, ast.Subscript):
            type_hint = self._get_subscript_type_hint(annotation_node)
        elif isinstance(annotation_node, ast.Call):
            type_hint = self._get_call_type_hint(annotation_node)
        elif isinstance(annotation_node, ast.keyword):
            type_hint = self._get_keyword_type_hint(annotation_node)
        elif isinstance(annotation_node, ast.BinOp):
            type_hint = self._get_binop_type_hint(annotation_node)
        elif isinstance(annotation_node, ast.UnaryOp):
            type_hint = self._get_unop_type_hint(annotation_node)
        elif isinstance(annotation_node, ast.Tuple):
            type_hint = self._get_tuple_type_hint(annotation_node)
        elif isinstance(annotation_node, ast.List):
            type_hint = self._get_list_type_hint(annotation_node)
        elif isinstance(annotation_node, ast.Attribute):
            type_hint = self._get_attribute_type_hint(annotation_node)
        elif isinstance(annotation_node, ast.Index):
            # ast.Index was deprecated in python 3.9
            # Since we want to support python 3.8, we need to ignore typing for this special case
            type_hint = self._get_type_annotation(annotation_node.value)  # type: ignore
        else:
            raise NotImplementedError(
                self._get_error_location_msg()
                + f"Type {type(annotation_node)} is not a valid type annotation. "
                + "This means you should probably change the type annotation to a valid one. "
                + "If you think it is a valid type annotation raise an issue in doXtrings repo."
            )
        return type_hint

    def _get_constant_string_value(self, value: Any) -> str:
        if value is None or isinstance(value, (int, float, bool)):
            return str(value)
        if isinstance(value, str):
            return f'"{value}"'
        elif value == Ellipsis:
            return "..."
        else:
            raise NotImplementedError(
                self._get_error_location_msg()
                + f"Type hint parsing not implemented for constant type {value}"
            )

    def _get_subscript_type_hint(self, annotation_node: ast.Subscript):
        outer_value = self._get_type_annotation(annotation_node.value)
        inner_value = self._get_type_annotation(annotation_node.slice)

        return f"{outer_value}[{inner_value}]"

    def _get_call_type_hint(self, annotation_node: ast.Call):
        outer_value = self._get_type_annotation(annotation_node.func)
        args = [self._get_type_annotation(a) for a in annotation_node.args]
        keywords = [self._get_keyword_type_hint(k) for k in annotation_node.keywords]
        inner_values = args + keywords
        inner_value_string = ", ".join([v for v in inner_values if v is not None])

        return f"{outer_value}({inner_value_string})"

    def _get_keyword_type_hint(self, annotation_node: ast.keyword):
        return (
            f"{annotation_node.arg}={self._get_type_annotation(annotation_node.value)}"
        )

    def _get_unop_type_hint(self, annotation_node: ast.UnaryOp):
        operand = self._get_type_annotation(annotation_node.operand)
        if isinstance(annotation_node.op, ast.USub):
            operator = "-"
        elif isinstance(annotation_node.op, ast.UAdd):
            operator = "+"
        elif isinstance(annotation_node.op, ast.Not):
            operator = "not "
        elif isinstance(annotation_node.op, ast.Invert):
            operator = "~"
        else:
            raise ValueError(
                self._get_error_location_msg()
                + f"Unknown Unary operator type {type(annotation_node.op)}"
            )

        return f"{operator}{operand}"

    def _get_binop_type_hint(self, annotation_node: ast.BinOp):
        left_value = self._get_type_annotation(annotation_node.left)
        right_value = self._get_type_annotation(annotation_node.right)

        return f"{left_value} | {right_value}"

    def _get_tuple_type_hint(self, annotation_node: ast.Tuple) -> str:
        annotations = [self._get_type_annotation(elt) for elt in annotation_node.elts]
        return ", ".join(["None" if ann is None else ann for ann in annotations])

    def _get_list_type_hint(self, annotation_node: ast.List) -> str:
        annotations = [self._get_type_annotation(elt) for elt in annotation_node.elts]
        return (
            "["
            + ", ".join(["None" if ann is None else ann for ann in annotations])
            + "]"
        )

    def _get_attribute_type_hint(self, annotation_node: ast.Attribute):
        outer_value = self._get_type_annotation(annotation_node.value)

        return f"{outer_value}.{annotation_node.attr}"

    def _parse_docstring(self) -> Optional[FunctionData]:
        """
        Parses the node's docstring into a FunctionData tuple.

        Returns:
            Optional[FunctionData]: returns the parsed FunctionData if there is a docstring for
                the class.
        """
        assert isinstance(self._input, (ast.FunctionDef, ast.AsyncFunctionDef))
        docstring = ast.get_docstring(self._input)
        if docstring and docstring != "":
            style = self._get_parsing_style()
            parsed_docstring = None
            try:
                parsed_docstring = dp.parse(docstring, style=style)
            except dp.ParseError as e:
                raise ValueError(
                    self._get_error_location_msg()
                    + f"Failed to parse docstring using {style} style."
                ) from e

            return FunctionParser._get_docstring_data(parsed_docstring)
        else:
            return None

    def get_diffs(self) -> List[Diff]:
        """Gets the list of diffs for the node

        Returns:
            List[Diff]: List of Diffs for the node
        """
        if self._docstring_data is None:
            return [
                Diff(DiffReasons.NO_DOCSTRING, location=[], code_value=self._code_data)
            ]

        if self._docstring_data == self._code_data:
            return []

        assert self._documentable_type
        ignore_config = self._config.get_ignore_rules(self._documentable_type)
        diffs = self._get_arguments_list_diff(ignore_config)

        return_type_diff = self._get_type_diff(
            self._code_data.return_type,
            self._docstring_data.return_type,
            ["return_type"],
        )
        if return_type_diff:
            should_ignore = (
                ignore_config.get_ignore_return()
                and not self._config.fail_ignored_if_incorrect
            ) or (
                ignore_config.get_ignore_return()
                and return_type_diff.reason == DiffReasons.MISSING
            )
            if not should_ignore:
                diffs.append(return_type_diff)
        return diffs

    def _get_arguments_list_diff(self, ignore_config: IgnoreRules) -> List[Diff]:
        assert self._docstring_data
        if (
            ignore_config.get_ignore_arguments()
            and len(self._docstring_data.arguments) == 0
        ) or (
            ignore_config.get_ignore_arguments()
            and not self._config.fail_ignored_if_incorrect
        ):
            return []
        matcher = SequenceMatcher()
        diffs: List[Diff] = []
        matcher.set_seqs(
            [a.name for a in self._docstring_data.arguments],
            [a.name for a in self._code_data.arguments],
        )
        docstring_shift = 0
        for _, i_doc, j_doc, i_code, j_code in matcher.get_opcodes():
            doc_args = self._docstring_data.arguments[i_doc:j_doc]
            code_args = self._code_data.arguments[i_code:j_code]
            for i, (code_arg, doc_arg) in enumerate(
                zip_longest(code_args, doc_args, fillvalue=None)
            ):
                index = i + i_doc + docstring_shift
                if not (code_arg and doc_arg):
                    if (
                        code_arg
                        and code_arg.name in ("*args", "**kwargs")
                        and ignore_config.ignore_args_and_kwargs
                    ):
                        continue
                    diffs.append(
                        Diff(
                            FunctionParser._get_element_diff_reason(code_arg, doc_arg),
                            location=["arguments", index],
                            code_value=code_arg,
                            docstring_value=doc_arg,
                        )
                    )
                else:
                    if code_arg.name != doc_arg.name:
                        diffs.append(
                            Diff(
                                DiffReasons.CONFLICTING_VALUE,
                                location=["arguments", index, "name"],
                                code_value=code_arg.name,
                                docstring_value=doc_arg.name,
                            )
                        )
                    type_diff = self._get_type_diff(
                        code_arg.type_hint,
                        doc_arg.type_hint,
                        ["arguments", index, "type_hint"],
                    )
                    if type_diff:
                        diffs.append(type_diff)
            shift = len(code_args) - len(doc_args)
            docstring_shift += shift if shift > 0 else 0
        return diffs

    def _get_type_diff(
        self,
        code_value: Optional[str],
        doc_value: Optional[str],
        location: List[Union[str, int]] = [],
    ) -> Optional[Diff]:
        assert self._documentable_type

        # We replace all new lines with spaces. It is fine to have multiline types.
        code_value = code_value.replace("\n", " ") if code_value else None
        doc_value = doc_value.replace("\n", " ") if doc_value else None
        # For the code value we strip quotes because those can be omitted in docstring
        # (and its fine)
        no_quotes_code_value = code_value.replace('"', "") if code_value else None
        if code_value != doc_value and no_quotes_code_value != doc_value:
            reason = FunctionParser._get_element_diff_reason(code_value, doc_value)
            ignore_config = self._config.get_ignore_rules(self._documentable_type)
            should_ignore = (
                ignore_config.get_ignore_typing()
                and not self._config.fail_ignored_if_incorrect
            ) or (ignore_config.get_ignore_typing() and reason == DiffReasons.MISSING)
            if not should_ignore:
                return Diff(
                    reason=reason,
                    location=location,
                    code_value=code_value,
                    docstring_value=doc_value,
                )

    @staticmethod
    def _get_element_diff_reason(code: Any, doc: Any):
        if doc is None:
            return DiffReasons.MISSING
        if code is None:
            return DiffReasons.EXTRA
        return DiffReasons.CONFLICTING_VALUE

    def _get_parsing_style(self) -> dp.DocstringStyle:
        assert (
            self._config.docstring_format
        ), "Docstring format is a required field in the config"
        return self._DOCSTRING_STYLES[self._config.docstring_format]

    @staticmethod
    def _get_docstring_data(docstring: dp.Docstring) -> FunctionData:
        function_args = tuple(
            FunctionArgument(param.arg_name, param.type_name)
            for param in docstring.params
        )
        return_type = docstring.returns.type_name if docstring.returns else None
        return FunctionData(arguments=function_args, return_type=return_type)
