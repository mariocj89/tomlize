import pathlib
import sys
from typing import Optional

import coloredlogs
import tomlkit

from . import setup_py
from .cli import parse_args
from .exceptions import ConversionError


def _convert(
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


def main(argv):
    args = parse_args(argv)
    coloredlogs.install(level="INFO", fmt="%(message)s")
    output_file = pathlib.Path("pyproject.toml")

    existing_config = None
    if output_file.exists():
        existing_config = output_file.read_text()

    try:
        result = _convert(
            input_file=args.input_file,
            existing_config=existing_config,
        )
    except ConversionError as error:
        print(f"Failed to convert files: {error}", file=sys.stderr)
        sys.exit(1)

    with output_file.open("w") as fp:
        tomlkit.dump(result, fp)
