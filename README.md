# tomlize

[![CI](https://github.com/mariocj89/tomlize/actions/workflows/valdiate.yaml/badge.svg)](https://github.com/mariocj89/tomlizer/actions/workflows/valdiate.yaml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tomlize)
![PyPI](https://img.shields.io/pypi/v/tomlize)
![PyPI - Downloads](https://img.shields.io/pypi/dm/tomlize)
![Code Style](https://img.shields.io/badge/code%20style-black,%20isort-000000.svg)

Move the configuration of all your tools to `pyproject.toml`.

```
$ python -m tomlize --help
usage: __main__.py [-h] input_file [output_file]

positional arguments:
  input_file
  output_file

options:
  -h, --help   show this help message and exit

```

The tool can be used to port the configuration from the following files:

## `setup.py`

```
python -m tomlize setup.py pyproject.toml
```
