"""The main CLI module, responsible for running all steps of doXtrings scan"""

from argparse import ArgumentParser
from typing import Optional

from doxtrings.config import get_config
from doxtrings.core.parser.file_parser import DoXtringsAstParser
from doxtrings.core.report import SimpleReporter
from doxtrings.core.search import search_files


def scan():
    """Runs the full doxtrings scan"""
    arg_parser = ArgumentParser(
        prog="DoXtrings", description="Detect missing and wrong docstrings"
    )

    arg_parser.add_argument("-c", "--config-file", default=None, required=False)
    args = arg_parser.parse_args()
    _scan(args.config_file)


def _scan(config_file: Optional[str]):
    cfg = get_config(config_file=config_file)
    parser = DoXtringsAstParser(config_file=config_file)
    reporter = SimpleReporter(cfg)
    for file in search_files(cfg):
        for documentable, diffs in parser.parse_file(file):
            reporter.add_documentable_diff(documentable=documentable, diffs=diffs)
    reporter.report()


if __name__ == "__main__":
    scan()
