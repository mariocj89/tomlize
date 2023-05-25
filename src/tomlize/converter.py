import pathlib

import tomlkit

from tomlize.exceptions import ConversionError

from . import merger, setup_py

CONVERTERS = {"setup.py": setup_py.extract}


def convert(
    input_file: pathlib.Path, config: tomlkit.TOMLDocument
) -> tomlkit.TOMLDocument:
    try:
        converter = CONVERTERS[input_file.name]
    except KeyError:
        raise ConversionError(f"Unrecognized input file: {input_file.name}") from None
    data = converter(input_file)
    merger.add_data(config, data)
    return config
