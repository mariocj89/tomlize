"""Transforms setuptools setup_py metadata to toml dict"""
import logging
import pathlib

import packaging.requirements

from .fields_mapping import FIELDS_MAPPING
from .reader import extract_setup_args

MIN_SETUPTOOLS_VERSION = "62.0.0"  # TODO: Find minimal version


def extract(setup_py_path: pathlib.Path) -> dict:
    data = extract_setup_args(setup_py_path)
    data = {key: value["value"] for key, value in data.items()}
    setup_requires = data.pop("setup_requires", [])
    ret = {}
    ret["build-system"] = _generate_build_metadata(setup_requires)
    ret.update(_transform_fields(data, setup_py_path.parent))
    return ret


def _generate_build_metadata(setup_requires):
    build_system = {"build-backend": "setuptools.build_meta", "requires": []}
    for req_str in setup_requires:
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
    return build_system


def _transform_fields(data: dict, project_root: pathlib.Path) -> dict:
    """Transform fields from setup.py to pyproject.toml format"""
    ret = {"project": {}}

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

    ### Enhancements ###
    for name in ["README.rst", "README.md"]:
        if project_root.joinpath(name).exists():
            ret["project"]["readme"] = name
    # TODO: Find and use license-file (glob)

    ### Warn on remaining fields ###
    for field in data:
        logging.warning("Unexpected field found: %s", field)

    return ret
