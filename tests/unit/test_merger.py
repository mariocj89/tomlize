import pytest
import tomlkit

from tomlize.exceptions import MergingError
from tomlize.merger import add_data


def _as_toml_doc(data):
    doc = tomlkit.TOMLDocument()
    add_data(doc, data)
    return doc


def test_insert_project_table():
    doc = _as_toml_doc(
        {
            "build-system": {
                "build-backend": "setuptools.build_meta",
                "requires": ["setuptools>62"],
            }
        }
    )
    new = {"project": {"name": "poochie", "version": "0.0.1"}}
    add_data(doc, new)
    assert doc["project"] == {"name": "poochie", "version": "0.0.1"}


@pytest.mark.parametrize(
    ["existing", "new", "output"],
    [
        (  # Add nothing
            {
                "build-backend": "setuptools.build_meta",
                "requires": ["setuptools>62"],
            },
            {},
            {
                "build-backend": "setuptools.build_meta",
                "requires": ["setuptools>62"],
            },
        ),
        (  # Merge 2 different requires
            {
                "requires": ["setuptools"],
            },
            {
                "requires": ["Cython"],
            },
            {
                "requires": ["setuptools", "Cython"],
            },
        ),
        (
            {
                "build-backend": "setuptools.build_meta",
            },
            {
                "build-backend": "setuptools.build_meta",
            },
            {
                "build-backend": "setuptools.build_meta",
            },
        ),
        pytest.param(  # Merge 2 requires same key
            {
                "requires": ["setuptools>1"],
            },
            {
                "requires": ["setuptools>2"],
            },
            {
                "requires": ["setuptools>2"],
            },
            marks=pytest.mark.xfail(reason="Needs dedup logic"),
        ),
    ],
)
def test_merge_build_system_success(existing, new, output):
    doc = _as_toml_doc({"build-system": existing})
    add_data(doc, {"build-system": new})
    assert doc["build-system"] == output


@pytest.mark.parametrize(
    ["existing", "new", "error_regex"],
    [
        (  # Change build backend
            {
                "build-backend": "setuptools.build_meta",
                "requires": ["setuptools>62"],
            },
            {
                "build-backend": "other-backend",
            },
            "build-backend",
        ),
    ],
)
def test_merge_build_system_failure(existing, new, error_regex):
    doc = _as_toml_doc({"build-system": existing})
    with pytest.raises(MergingError, match=error_regex):
        add_data(doc, {"build-system": new})


def test_merge_project_key():
    doc = _as_toml_doc({"project": {"name": "poochie"}})
    new = {"project": {"version": "1.0.0"}}
    add_data(doc, new)
