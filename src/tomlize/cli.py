import argparse
import pathlib


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=pathlib.Path)
    return parser.parse_args(args=args)
