import argparse
import pathlib


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=pathlib.Path)
    parser.add_argument("output_file", type=pathlib.Path, nargs="?")
    return parser.parse_args()
