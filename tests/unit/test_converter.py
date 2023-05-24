from pathlib import Path
from unittest import mock

import pytest
import tomlkit

import tomlize.converter
from tomlize.converter import convert
from tomlize.exceptions import ConversionError

TEST_CONVERTER_FILENAME = "test-file"
TEST_CONVERTER_FILE = Path("test-file")


def empty_toml():
    return tomlkit.TOMLDocument()


def decode_toml(text):
    return tomlkit.parse(text)


@pytest.fixture()
def setup_py_extract():
    fake = mock.Mock()
    with mock.patch.dict(tomlize.converter.CONVERTERS, {TEST_CONVERTER_FILENAME: fake}):
        yield fake


def test_smoke(setup_py_extract):
    setup_py_extract.return_value = {"foo": "bar"}
    result = convert(TEST_CONVERTER_FILE, empty_toml())
    assert result == {"foo": "bar"}
    setup_py_extract.assert_called_once()


def test_failed_conversion(setup_py_extract):
    with pytest.raises(ConversionError, match="Unrecognized"):
        convert(Path("not-supported"), empty_toml())
    setup_py_extract.assert_not_called()


def test_insert_project_table(setup_py_extract):
    setup_py_extract.return_value = {"project": {"name": "poochie", "version": "0.0.1"}}
    pyproject_toml = """
    [build-system]
    build-backend = "setuptools.build_meta"
    requires = ["setuptools>62"]
    """
    result = convert(
        TEST_CONVERTER_FILE,
        decode_toml(pyproject_toml),
    )
    assert result["project"] == {"name": "poochie", "version": "0.0.1"}
    setup_py_extract.assert_called_once()


def test_preserve_comments(setup_py_extract):
    pyproject_toml = """
    [build-system]
    build-backend = "setuptools.build_meta"
    requires = ["setuptools>62"]

    [tool.mypy]
    warn_return_any = true  # leave my comment alone
    """
    setup_py_extract.return_value = {"foo": "bar"}
    result = convert(
        TEST_CONVERTER_FILE,
        decode_toml(pyproject_toml),
    )
    assert "foo" in result
    assert result.get("tool").get("mypy"), tomlkit.dumps(result)
    result_text = tomlkit.dumps(result)
    assert "warn_return_any = true  # leave my comment alone" in result_text
    setup_py_extract.assert_called_once()


@pytest.mark.xfail(reason="This isn't handled currently")
def test_existing_project_table(setup_py_extract):
    pyproject_toml = """
    [build-system]
    build-backend = "setuptools.build_meta"
    requires = ["setuptools>62"]

    [project]
    name = "foo"
    """
    setup_py_extract.return_value = {"project": {"name": "poochie", "version": "0.0.1"}}
    with pytest.raises(ConversionError, match=r"\[project\] already exists"):
        convert(
            TEST_CONVERTER_FILE,
            decode_toml(pyproject_toml),
        )

    setup_py_extract.assert_called_once()
