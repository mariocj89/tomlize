"""Transforms setuptools setup_py metadata to toml dict"""
import logging
import pathlib
import unittest.mock

import packaging.requirements

from .. import exceptions
from .setuptools_mapping import FIELDS_MAPPING

MIN_SETUPTOOLS_VERSION = "62.0.0"  # TODO: Find minimal vesion


def extract(setup_path: pathlib.Path) -> dict:
    data = _extract_setup_args(setup_path)
    ret = {"build-system": {}, "project": {}}

    ### Translate metadata ###
    for field_key, target in FIELDS_MAPPING.items():
        if field_key not in data:
            continue
        orig_value = data.pop(field_key)
        if isinstance(target, list):
            target_object = ret
            *path_parts, terminal = target
            for target_part in path_parts:
                target_object.setdefault(target_part, {})
                target_object = target_object[target_part]
            target_object[terminal] = orig_value
        elif callable(target):
            target(orig_value, ret)
        elif target is None:
            continue
        else:  # pragma: no cover
            raise Exception("Invalid mapping type {target!r} for key {field_key!r}")

    ### build system fields ###
    build_system = ret["build-system"]
    build_system["build-backend"] = "setuptools.build_meta"
    build_system["requires"] = []
    for req_str in data.pop("setup_requires", []):
        req = packaging.requirements.Requirement(req_str)
        if req.name == "setuptools":
            if not req.specifier or list(
                req.specifier.filter([MIN_SETUPTOOLS_VERSION])
            ):
                # Specified setuptools is not enough, skip and use default
                continue
        build_system["requires"].append(req_str)

    if not any(
        packaging.requirements.Requirement(r).name == "setuptools"
        for r in build_system["requires"]
    ):
        build_system["requires"].append(
            f"setuptools >= {MIN_SETUPTOOLS_VERSION}",
        )

    ### Enhancements ###
    project_root = setup_path.parent
    for name in ["README.rst", "README.md"]:
        if project_root.joinpath(name).exists():
            ret["project"]["readme"] = name
    # TODO: Find and use license-file (glob)

    ### Warn on remaining fields ###
    for field in data:
        logging.warning("Unexpected field found: %s", field)

    return ret


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
