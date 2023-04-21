import coloredlogs
import toml

from . import loaders
from .cli import parse_args


def main():
    args = parse_args()
    result = {}
    coloredlogs.install(level="INFO", fmt="%(message)s")

    if args.output_file and args.output_file.exists():
        result.update(toml.loads(args.output_file.read_text()))

    if args.input_file.name == "setup.py":
        data = loaders.setup_py.extract(args.input_file)
        # TODO: Merge with existing data
        result.update(data)

    output = toml.dumps(result)
    if args.output_file:
        args.output_file.write_text(output)
    else:
        print(output)
