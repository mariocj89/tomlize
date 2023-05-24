from tomlize.setup_py.remover import CodeTarget, _remove_lines, remove


def test_remove_nothing_keeps_format():
    from_ = """

TOKEN = 1

"""
    assert _remove_lines(from_, []) == from_


def test_remove_one_hit():
    from_ = """

TOKEN = 1

"""
    to = """

= 1

"""
    assert _remove_lines(from_, [CodeTarget(2, 0, 2, 6)]) == to


def test_remove_two_hits():
    from_ = """

TOKEN = 1

"""
    to = """



"""
    assert (
        _remove_lines(
            from_,
            [
                CodeTarget(2, 0, 2, 6),
                CodeTarget(2, 6, 2, 9),
            ],
        )
        == to
    )


def test_remove_multiline_hits():
    from_ = """
{
    "key": 1
}
"""
    to = """
"""
    assert (
        _remove_lines(
            from_,
            [
                CodeTarget(1, 0, 3, 2),
            ],
        )
        == to
    )


def test_remove_in_a_file(tmp_path):
    file_ = tmp_path / "file.txt"
    file_.write_text(
        """
        some text>REMOVE< in a file
"""
    )
    to = """
        some text in a file
"""
    assert remove(file_, [CodeTarget(1, 17, 1, 25)]) == to
