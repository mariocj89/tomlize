"""Merges pyproject.toml configuration

Provides a function that allows to add additional
information to an existing pyproject.toml document.
"""
import tomlkit


def add_data(config: tomlkit.TOMLDocument, data):
    for key, value in data.items():
        config.add(key, value)
