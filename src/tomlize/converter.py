import pathlib

import tomlkit

from tomlize.exceptions import ConversionError

from . import setup_py


def convert(
    *, input_file: pathlib.Path, config: tomlkit.TOMLDocument
) -> tomlkit.TOMLDocument:
    if input_file.name == "setup.py":
        data = setup_py.transformer.extract(input_file)
    else:
        raise ConversionError(f"Unrecognized input file: {input_file.name}")

    for key, value in data.items():
        config.add(key, value)

    return config
