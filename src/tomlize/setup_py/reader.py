"""Reads the setup.py and extracts information from it"""

import logging
import pathlib
import unittest.mock

from .. import exceptions


def extract_setup_args(setup_path: pathlib.Path):
    return {
        key: {"value": value} for key, value in _extract_setup_args(setup_path).items()
    }


def _run_setup_py(setup_path: pathlib.Path):
    try:
        exec(
            setup_path.read_text(),
            {"__name__": "__main__", "__file__": "setup.py"},
        )
    except FileNotFoundError:
        raise exceptions.FailedToParseError(setup_path, "File not found")
    except ImportError as e:
        raise exceptions.FailedToParseError(
            setup_path, f"Unable to import {e.name!r}, are you missing a dependency?"
        )
    except Exception as e:
        logging.error("Failed to load setup.py")
        raise exceptions.FailedToParseError(setup_path, e) from e


def _extract_setup_args(setup_path: pathlib.Path) -> dict:
    with unittest.mock.patch("setuptools.setup") as fake_setup:
        _run_setup_py(setup_path)
    _, kwargs = fake_setup.call_args
    return kwargs
