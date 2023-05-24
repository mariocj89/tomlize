import pathlib

import tomlkit

from tomlize.exceptions import ConversionError

from . import setup_py

CONVERTERS = {"setup.py": setup_py.extract}


def _add_data(config: tomlkit.TOMLDocument, data):
    for key, value in data.items():
        config.add(key, value)


def convert(
    input_file: pathlib.Path, config: tomlkit.TOMLDocument
) -> tomlkit.TOMLDocument:
    try:
        converter = CONVERTERS[input_file.name]
    except KeyError:
        raise ConversionError(f"Unrecognized input file: {input_file.name}") from None
    data = converter(input_file)
    _add_data(config, data)
    return config
