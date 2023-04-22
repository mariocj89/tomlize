"""Transforms setuptools setup_py metadata to toml dict"""
import logging
import pathlib
import unittest.mock

import packaging.requirements

from .. import exceptions

MIN_SETUPTOOLS_VERSION = "62.0.0"  # TODO: Find minimal vesion


def moveif(orig, dst, orig_key, dst_key=None):
    """Copies the key if exists"""
    if dst_key is None:
        dst_key = orig_key
    if orig_key in orig:
        dst[dst_key] = orig.pop(orig_key)


def extract(setup_path: pathlib.Path) -> dict:
    data = _extract_setup_args(setup_path)
    ret = {}

    ## Pending fields
    # ext_modules
    # ext_package
    # package_data
    # entry_points

    ### Ignored fields ###
    for field in [
        "zip_safe",  # Deprecated
    ]:
        data.pop(field, None)

    ### metadata fields ###
    metadata = {}
    for attr in [
        "name",
        "version",
        "description",
        "download_url",
        "classifiers",
        "keywords",
    ]:
        moveif(data, metadata, attr)
    for orig_attr, dst_attr in [
        ("python_requires", "requires-python"),
        ("install_requires", "dependencies"),
        ("extras_require", "optional-dependencies"),
        ("project_urls", "urls"),
    ]:
        moveif(data, metadata, orig_attr, dst_attr)
    if "author" in data or "author_email" in data:
        metadata["authors"] = [{}]
        if name := data.pop("author", None):
            metadata["authors"][0]["name"] = name
        if email := data.pop("author_email", None):
            metadata["authors"][0]["email"] = email
    if "maintainer" in data or "maintainer_email" in data:
        metadata["maintainers"] = [{}]
        if name := data.pop("maintainer", None):
            metadata["maintainers"][0]["name"] = name
        if email := data.pop("maintainer_email", None):
            metadata["maintainers"][0]["email"] = email
    if url := data.pop("url", None):
        if "urls" not in metadata:
            metadata["urls"] = {}
        metadata["urls"]["Home-page"] = url
    if license_text := data.pop("license", None):
        metadata["license"] = {"text": license_text}
    if license_file := data.pop("license_file", None):
        metadata["license"] = {"file": license_file}

    ### build system fields ###
    build_system = {
        "build-backend": "setuptools.build_meta",
        "requires": [],
    }
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
    ret["build-system"] = build_system

    ### setuptools specific fields ###
    setuptools_specific = {}

    if data.get("package_dir", {}).get("") == "src":
        # TODO: Properly figure out if we can default to automatic discovery
        # standard src layout, default to automatic discovery
        data.pop("package_dir")
        data.pop("packages", None)
        data.pop("py_modules", None)
    else:
        moveif(data, setuptools_specific, "packages")
        moveif(data, setuptools_specific, "py_modules")
        moveif(data, setuptools_specific, "package_dir", "package-dir")

    for attr in [
        "platform",
        "packages",
    ]:
        moveif(data, setuptools_specific, attr)
    for orig_attr, dst_attr in [
        ("scripts", "script-files"),
        ("data_files", "data-files"),
        ("include_package_data", "include-package-data"),
        ("py_modules", "py-modules"),
        ("package_dir", "package-dir"),
    ]:
        moveif(data, setuptools_specific, orig_attr, dst_attr)

    ### Enhancements ###
    project_root = setup_path.parent
    for name in ["README.rst", "README.md"]:
        if project_root.joinpath(name).exists():
            metadata["readme"] = name
            data.pop("long_description", None)
            data.pop("long_description_content_type", None)
    if isinstance(metadata.get("keywords"), str):
        metadata["keywords"] = metadata["keywords"].split(", ")
    # TODO: Find and use license-file (glob)

    ### Warn on remaining fields ###
    for field in data:
        logging.warning("Unexpected field found: %s", field)

    if metadata:
        ret["project"] = metadata
    if setuptools_specific:
        ret["tool"] = {"setuptools": setuptools_specific}
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
