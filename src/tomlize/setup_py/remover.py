"""Removes code from setup.py"""
import dataclasses
import pathlib


@dataclasses.dataclass(order=True, frozen=True)
class CodeTarget:
    """Identifies code within a file"""

    line_from: int
    col_from: int
    line_to: int
    col_to: int


def remove(filename: pathlib.Path, code_targets: list[CodeTarget]):
    return _remove_lines(filename.read_text(), code_targets)


def _remove_lines(content: str, code_targets: list[CodeTarget]):
    for target in sorted(code_targets, reverse=True):
        content = _remove_content(content, target)
    return content


def _remove_content(content: str, target: CodeTarget):
    start_idx, end_idx = _find_str_positions(content, target)
    content_list = list(content)
    content_list[start_idx:end_idx] = []
    return "".join(content_list)


def _find_str_positions(content: str, code_target: CodeTarget) -> tuple[int, int]:
    """
    Computes the start and end string position that are referenced by a code target
    """
    content_iter = iter(content)
    line_no = 0
    start_idx = 0

    # Place us in the right line
    while line_no < code_target.line_from:
        char = next(content_iter)
        start_idx += 1
        if char == "\n":
            line_no += 1

    # Place us in the right col
    for _ in range(code_target.col_from):
        char = next(content_iter)
        assert char != "\n", repr(content[start_idx - 3 : start_idx + 3])
        start_idx += 1

    end_idx = start_idx
    # Place us in the right line end
    while line_no < code_target.line_to:
        char = next(content_iter)
        end_idx += 1
        if char == "\n":
            line_no += 1

    # Place us in the right col end
    col_steps = code_target.col_to
    if code_target.line_from == code_target.line_to:
        col_steps = code_target.col_to - code_target.col_from
    for _ in range(col_steps):
        char = next(content_iter)
        end_idx += 1

    return start_idx, end_idx
