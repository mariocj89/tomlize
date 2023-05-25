import pytest
import tomlkit

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
                "requires": "setuptools>62",
            }
        }
    )
    new = {"project": {"name": "poochie", "version": "0.0.1"}}
    add_data(doc, new)
    assert doc["project"] == {"name": "poochie", "version": "0.0.1"}


@pytest.mark.xfail(reason="This isn't handled currently")
def test_merge_project_key():
    doc = _as_toml_doc({"project": {"name": "poochie"}})
    new = {"project": {"version": "1.0.0"}}
    add_data(doc, new)
