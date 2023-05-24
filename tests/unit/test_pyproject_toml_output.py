from pathlib import Path
from unittest import mock

import pytest
import tomlkit

from tomlize.converter import convert
from tomlize.exceptions import ConversionError


@mock.patch("tomlize.converter.setup_py.transformer.extract")
class TestConvert:
    def test_smoke(self, extract):
        extract.return_value = {"foo": "bar"}
        result = convert(input_file=Path("setup.py"))
        assert result == {"foo": "bar"}
        extract.assert_called_once()

    def test_failed_conversion(self, extract):
        with pytest.raises(ConversionError, match="Unrecognized"):
            convert(input_file=Path("bazgina.cfg"))
        extract.assert_not_called()

    def test_insert_project_table(self, extract):
        extract.return_value = {"project": {"name": "poochie", "version": "0.0.1"}}
        pyproject_toml = """
        [build-system]
        build-backend = "setuptools.build_meta"
        requires = ["setuptools>62"]
        """
        result = convert(input_file=Path("setup.py"), existing_config=pyproject_toml)
        assert result["project"] == {"name": "poochie", "version": "0.0.1"}
        extract.assert_called_once()

    def test_preserve_comments(self, extract):
        pyproject_toml = """
        [build-system]
        build-backend = "setuptools.build_meta"
        requires = ["setuptools>62"]

        [tool.mypy]
        warn_return_any = true  # leave my comment alone
        """
        extract.return_value = {"foo": "bar"}
        result = convert(
            input_file=Path("setup.py"),
            existing_config=pyproject_toml,
        )
        assert "foo" in result
        assert result.get("tool").get("mypy"), tomlkit.dumps(result)
        result_text = tomlkit.dumps(result)
        assert "warn_return_any = true  # leave my comment alone" in result_text
        extract.assert_called_once()

    def test_existing_project_table(self, extract):
        pyproject_toml = """
        [build-system]
        build-backend = "setuptools.build_meta"
        requires = ["setuptools>62"]

        [project]
        name = "foo"
        """
        extract.return_value = {"project": {"name": "poochie", "version": "0.0.1"}}
        with pytest.raises(ConversionError, match=r"\[project\] already exists"):
            convert(input_file=Path("setup.py"), existing_config=pyproject_toml)

        extract.assert_called_once()
