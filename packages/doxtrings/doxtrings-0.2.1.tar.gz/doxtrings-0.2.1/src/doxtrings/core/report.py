"""
Implements the classes used to print the reports of the found differences
found in the source code
"""

import sys
from abc import ABC, abstractmethod
from typing import List, NamedTuple, Union

from doxtrings.config import DoXtringsConfig
from doxtrings.core.parser.node_parser import Diff
from doxtrings.documentable import Documentable


class ReportItem(NamedTuple):
    """A NamedTuple containing the relevant report data for a single documentable"""

    documentable: Documentable
    """The documentable this report item is referring to"""
    diffs: List[Diff]
    """The documentable's list of differences"""


class BaseReporter(ABC):
    """Base reporter class"""

    def __init__(self, config: DoXtringsConfig):
        """Initializes the base reporter with an empty list of report items

        Args:
            config (DoXtringsConfig): the DoXtrings configuration
        """
        self._config = config
        self.report_items: List[ReportItem] = []

    def add_documentable_diff(self, documentable: Documentable, diffs: List[Diff]):
        """
        Adds a list of diffs to a documentable. The provided `diffs` argument is filtered
        according to configuration rules before being linked to the documentable in a ReportItem.

        Args:
            documentable (Documentable): the documentable to be added to the report
            diffs (List[Diff]): all the diffs found for the documentable
        """
        if len(diffs):
            self.report_items.append(ReportItem(documentable, diffs))
            if self._config.fail_fast:
                self.report()

    @abstractmethod
    def report(self):
        """Abstract method responsible for printing out the report and handling exit codes"""


class SimpleReporter(BaseReporter):
    """A simple reporter that prints out the relevant information"""

    def report(self):
        """
        Prints out all the collected differences in the console.
        If there are diffs to be reported, exits with code 1.
        """
        if len(self.report_items) == 0:
            print("All docstrings have passed the check")
            sys.exit(0)
        else:
            for item in self.report_items:
                file_line_ref = f"{item.documentable.file}:{item.documentable.line}"
                print(
                    f"Docstring error found at {file_line_ref} on {item.documentable.documentable_type} {item.documentable.name}"
                )
                for diff in item.diffs:
                    location = get_location_string(diff.location)
                    line = f"    At {location}: Reason {diff.reason.value}"
                    if diff.code_value or diff.docstring_value:
                        line += f" expected {diff.code_value} but docstring is {diff.docstring_value}"
                    print(line)
            sys.exit(1)


def get_location_string(location: List[Union[str, int]]) -> str:
    """Transforms a location list into a human readable string.

    Args:
        location (List[Union[str, int]]): the list containing location information.

    Returns:
        str: a string representation of the location list.
    """
    if len(location) == 0:
        return "root"
    str_parts = [f".{l}" if isinstance(l, str) else f"[{str(l)}]" for l in location]
    return "".join(str_parts)
