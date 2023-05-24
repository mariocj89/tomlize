import pathlib
from typing import Optional

import tomlkit

from tomlize.exceptions import ConversionError

from . import setup_py


def convert(
    *, input_file: pathlib.Path, existing_config: Optional[str] = None
) -> tomlkit.TOMLDocument:
    if input_file.name == "setup.py":
        data = setup_py.transformer.extract(input_file)
    else:
        raise ConversionError(f"Unrecognized input file: {input_file.name}")

    if existing_config is not None:
        doc = tomlkit.parse(existing_config)
    else:
        doc = tomlkit.TOMLDocument()

    for key, value in data.items():
        doc.add(key, value)

    return doc
