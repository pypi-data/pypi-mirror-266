"""Implements the functions used to search a directory for the files to be parsed by doXtrings"""

import logging
from os import walk
from pathlib import Path
from typing import Generator, List, Optional

from doxtrings.config import DoXtringsConfig

logger = logging.getLogger(__name__)


def search_files(config: DoXtringsConfig) -> Generator[Path, None, None]:
    """Runs through the directory specified in the config and yields file paths to be parsed.

    Args:
        config (DoXtringsConfig): the DoXtrings configuration

    Yields:
        Generator[Path, None, None]: the file paths to be parsed
    """
    for dirpath, subdirs, filenames in walk(config.path):
        logger.debug(f"Searching files at {dirpath}")
        for filename in filenames:
            if _should_include_file(
                filename, config.exclude_files, config.include_file_extensions
            ):
                file_path = Path(dirpath) / filename
                logger.debug(f"Yielding file {str(file_path)}")
                yield file_path

        # Updates subdir in place to remove unwanted subdirectories
        subdirs[:] = [
            subdir
            for subdir in subdirs
            if _should_include_dir(subdir, config.exclude_files)
        ]
        logger.debug(f"Looking into subdirs {subdirs}")


def _should_include_file(
    filename: str,
    exclude_list: Optional[List[str]],
    allowed_extensions: Optional[List[str]],
):
    if exclude_list is None:
        exclude_list = []
    if allowed_extensions is None:
        allowed_extensions = []
    suffix_match = _match_suffix(filename, allowed_extensions)
    if not suffix_match:
        logger.info(
            f"File {filename} excluded because extension does not match any of: {allowed_extensions}"
        )
    excluded = filename in exclude_list
    if excluded:
        logger.info(
            f"File {filename} excluded because found match in exclude list: {exclude_list}"
        )
    return suffix_match and not excluded


def _should_include_dir(dirname: str, exclude_list: Optional[List[str]]):
    if exclude_list is None:
        exclude_list = []
    excluded = dirname in [excluded.strip("/") for excluded in exclude_list]
    if excluded:
        logger.info(
            f"Directory {dirname} excluded because found match in exclude list: {exclude_list}"
        )
    return not excluded


def _match_suffix(filename: str, allowed_suffixes: List[str]):
    return filename.endswith(tuple(allowed_suffixes))
