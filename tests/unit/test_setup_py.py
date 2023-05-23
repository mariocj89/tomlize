"""Validates the loading of `setup.py`"""
import pathlib

import pytest

from tomlize.exceptions import FailedToParseError
from tomlize.loaders.setup_py import extract

EMPTY_RESULT = {
    "project": {},
    "build-system": {
        "build-backend": "setuptools.build_meta",
        "requires": ["setuptools >= 62.0.0"],
    },
}


@pytest.fixture
def setup_py(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    yield tmp_path / "setup.py"


def test_empty(setup_py):
    setup_py.write_text(
        """
import setuptools
setuptools.setup()
        """
    )
    assert extract(setup_py) == EMPTY_RESULT


def test_simple(setup_py):
    setup_py.write_text(
        """
import setuptools
setuptools.setup(
    name="package",
    version="1.0.0",
    description="My cool package",
)
        """
    )
    assert extract(setup_py)["project"] == {
        "name": "package",
        "version": "1.0.0",
        "description": "My cool package",
    }


def test_version_from_variable(setup_py):
    setup_py.write_text(
        """
import setuptools
version = "1.0.1"
setuptools.setup(
    name="package",
    version=version,
    description="My cool package",
)
        """
    )
    assert extract(setup_py)["project"]["version"] == "1.0.1"


@pytest.mark.parametrize(
    ["input_version", "output_version"],
    [
        ("", ">= 62.0.0"),
        ("> 61", ">= 62.0.0"),
        (">= 63.0.0", ">= 63.0.0"),
    ],
)
def test_setuptools_setup_requires_handling(setup_py, input_version, output_version):
    setup_py.write_text(
        f"""
import setuptools
setuptools.setup(
    setup_requires=["setuptools {input_version}"]
)
        """
    )
    assert (
        extract(setup_py)["build-system"]["requires"][0]
        == f"setuptools {output_version}"
    )


def test_all_attributes(setup_py):
    setup_py.write_text(
        """
import setuptools
version = "1.0.1"
setuptools.setup(
    name="package",
    version=version,
    description="My cool package",
    python_requires=">=3.11",
    author="John Doe",
    author_email="john@doe.com",
    maintainer="Jose Garcia",
    maintainer_email="jose@garcia.com",
    url="chooserandom.com",
    license_file="LICENSE",
    download_url="echaloasuerte.com",
    classifiers = [
        'Programming Language :: Python :: 3.11',
    ],
    install_requires=[
        "six",
        "python-dateutil>=2.7.0",
    ],
    extras_require={"docker": ["binaryornot"]},
    setup_requires=["setuptools >= 70.0.0", "toml > 1.0"],
)
        """
    )
    assert extract(setup_py) == {
        "build-system": {
            "requires": ["setuptools >= 70.0.0", "toml > 1.0"],
            "build-backend": "setuptools.build_meta",
        },
        "project": {
            "name": "package",
            "version": "1.0.1",
            "description": "My cool package",
            "urls": {"Home-page": "chooserandom.com", "Download": "echaloasuerte.com"},
            "classifiers": ["Programming Language :: Python :: 3.11"],
            "requires-python": ">=3.11",
            "license": {"file": "LICENSE"},
            "authors": [{"email": "john@doe.com", "name": "John Doe"}],
            "maintainers": [{"email": "jose@garcia.com", "name": "Jose Garcia"}],
            "dependencies": ["six", "python-dateutil>=2.7.0"],
            "optional-dependencies": {"docker": ["binaryornot"]},
        },
    }


def test_invalid_setup(setup_py):
    setup_py.write_text(
        """
THIS IS NOT PYTHON
        """
    )
    with pytest.raises(FailedToParseError, match="NOT PYTHON"):
        extract(setup_py)


def test_non_existing_seutup_py():
    with pytest.raises(FailedToParseError, match="File not found"):
        extract(pathlib.Path("ashfjsak/setup.py"))


def test_missing_depenndency(setup_py):
    setup_py.write_text(
        """
import pkgconfig
        """
    )
    with pytest.raises(FailedToParseError, match="Unable to import"):
        extract(setup_py)


def test_unexpected_field_warns(setup_py, caplog):
    caplog.set_level("WARN")
    setup_py.write_text(
        """
import setuptools
from distutils.core import Extension
setuptools.setup(
    ext_modules=[Extension('foo', ['foo.c'])],
)
        """
    )

    extract(setup_py)
    assert caplog.messages == ["Unexpected field found: ext_modules"]


def test_readme_file_adds_it_automatically(setup_py):
    setup_py.write_text(
        """
import setuptools
setuptools.setup()
        """
    )
    setup_py.parent.joinpath("README.md").write_text("")

    assert extract(setup_py)["project"]["readme"] == "README.md"


def test_setuptools_specific_fields(setup_py):
    setup_py.write_text(
        """
import setuptools
setuptools.setup(
    package_dir={"":"notsrc"},
    packages=["p"]
)
        """
    )
    setup_py.parent.joinpath("README.md").write_text("")

    assert extract(setup_py)["tool"]["setuptools"] == {
        "package-dir": {"": "notsrc"},
        "packages": ["p"],
    }


def test_entry_points(setup_py):
    setup_py.write_text(
        """
import setuptools
setuptools.setup(
    entry_points={
        "pytest11": [
            "pystack = pytest_pystack.plugin",
        ],
    },
)
        """
    )
    setup_py.parent.joinpath("README.md").write_text("")

    assert extract(setup_py)["project"]["entry-points"] == {
        "pytest11": {"pystack": "pytest_pystack.plugin"}
    }


def test_keywords_as_string(setup_py):
    setup_py.write_text(
        """
import setuptools
setuptools.setup(
    keywords="many, keywords"
)
        """
    )
    setup_py.parent.joinpath("README.md").write_text("")

    assert extract(setup_py)["project"]["keywords"] == ["many", "keywords"]
