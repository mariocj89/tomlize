"""Merges pyproject.toml configuration

Provides a function that allows to add additional
information to an existing pyproject.toml document.
"""
import tomlkit
import tomlkit.exceptions
import tomlkit.items

from .exceptions import MergingError


def _merge_requires(config: tomlkit.items.Array, data: list[str]):
    for require in data:
        if require not in config:
            config.append(require)


def _merge_build_system(config: tomlkit.items.Table, data: dict):
    if requires := data.pop("requires", None):
        config.setdefault("requires", [])
        _merge_requires(config["requires"], requires)
    for key, value in data.items():
        config.add(key, value)


def _merge_project(config: tomlkit.items.Table, data: dict):
    for key, value in data.items():
        config.add(key, value)


def add_data(config: tomlkit.TOMLDocument, data: dict):
    try:
        if build_system := data.pop("build-system", None):
            config.setdefault("build-system", {})
            _merge_build_system(config["build-system"], build_system)
        if project := data.pop("project", None):
            config.setdefault("project", {})
            _merge_project(config["project"], project)
        for key, value in data.items():
            config.add(key, value)
    except tomlkit.exceptions.KeyAlreadyPresent as e:
        raise MergingError(e) from None
