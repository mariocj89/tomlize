import pathlib
import sys

import coloredlogs
import tomlkit

from . import converter
from .cli import parse_args
from .exceptions import ConversionError


def main(argv):
    args = parse_args(argv)
    coloredlogs.install(level="INFO", fmt="%(message)s")
    output_file = pathlib.Path("pyproject.toml")

    if output_file.exists():
        existing_config = tomlkit.parse(output_file.read_text())
    else:
        existing_config = tomlkit.TOMLDocument()

    try:
        result = converter.convert(
            input_file=args.input_file,
            config=existing_config,
        )
    except ConversionError as error:
        print(f"Failed to convert files: {error}", file=sys.stderr)
        sys.exit(1)

    with output_file.open("w") as fp:
        tomlkit.dump(result, fp)
        print("pyproject.toml file updated!")
