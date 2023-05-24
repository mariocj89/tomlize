"""Mapping of fields from setuptools to pyproject.toml

Value types can be:
    - None: Drop the key
    - List of str: path in the dict to copy towards
    - callable: Call a function that takes the original value and the output dict
"""


def keywords(original_value, result: dict):
    if isinstance(original_value, str):
        original_value = original_value.split(", ")
    result["project"]["keywords"] = original_value


def entry_points(original_value, result: dict):
    result["project"]["entry-points"] = {}
    for ep_group_name, ep_group in original_value.items():
        new_ep_group = {}
        for ep in ep_group:
            ep_name, ep_value = ep.split("=")
            new_ep_group[ep_name.strip()] = ep_value.strip()
        result["project"]["entry-points"][ep_group_name] = new_ep_group
    # TODO: Handle console scripts (Either here or in enhance)


def _ensure_authors(result: dict):
    if "authors" not in result["project"]:
        result["project"]["authors"] = [{}]


def _ensure_maintainers(result: dict):
    if "maintainers" not in result["project"]:
        result["project"]["maintainers"] = [{}]


def author(original_value, result: dict):
    _ensure_authors(result)
    result["project"]["authors"][0]["name"] = original_value


def author_email(original_value, result: dict):
    _ensure_authors(result)
    result["project"]["authors"][0]["email"] = original_value


def maintainer(original_value, result: dict):
    _ensure_maintainers(result)
    result["project"]["maintainers"][0]["name"] = original_value


def maintainer_email(original_value, result: dict):
    _ensure_maintainers(result)
    result["project"]["maintainers"][0]["email"] = original_value


FIELDS_MAPPING = {
    "name": ["project", "name"],
    "version": ["project", "version"],
    "description": ["project", "description"],
    "classifiers": ["project", "classifiers"],
    "keywords": keywords,
    "entry_points": entry_points,
    "author": author,
    "author_email": author_email,
    "maintainer": maintainer,
    "maintainer_email": maintainer_email,
    "python_requires": ["project", "requires-python"],
    "install_requires": ["project", "dependencies"],
    "extras_require": ["project", "optional-dependencies"],
    "project_urls": ["project", "urls"],
    "url": ["project", "urls", "Home-page"],
    "download_url": ["project", "urls", "Download"],
    "license": ["project", "license", "text"],
    "license_file": ["project", "license", "file"],
    "scripts": ["tool", "setuptools", "script-files"],
    "data_files": ["tool", "setuptools", "data-files"],
    "include_package_data": ["tool", "setuptools", "include-package-data"],
    "py_modules": ["tool", "setuptools", "py-modules"],
    "package_dir": ["tool", "setuptools", "package-dir"],
    "platform": ["tool", "setuptools", "platform"],
    "packages": ["tool", "setuptools", "packages"],
    "zip_safe": None,
}
