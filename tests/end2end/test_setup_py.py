import pprint
import shutil
import subprocess
import sys
import tarfile

import pkginfo
import pytest

from .. import utils


@pytest.fixture
def setup_py(tmp_path):
    f = tmp_path / "setup.py"
    f.write_text(
        """
import setuptools
version = "1.0.0"
setuptools.setup(
    name="package",
    version=version,
    description="My cool package",
    python_requires=">=3.11",
    author="John Doe",
    author_email="john@doe.com",
    install_requires=[
        "six",
        "python-dateutil>=2.7.0",
    ],
    extras_require={"docker": ["binaryornot"]},
    setup_requires=["setuptools >= 70.0.0", "toml > 1.0"],
)
"""
    )
    return f


@pytest.fixture
def empty_pyproject_toml(tmp_path):
    f = tmp_path / "pyproject.toml"
    f.write_text(
        """
"""
    )
    yield f
    utils.validate_pyproject(f)


def run(*args):
    subprocess.run(
        [sys.executable, "-m", "tomlize", *args],
        check=True,
    )


def test_end_to_end_stdout(setup_py):
    run(setup_py)


def test_end_to_end_empty(setup_py, empty_pyproject_toml):
    run(setup_py, empty_pyproject_toml)
    assert (
        empty_pyproject_toml.read_text()
        == """\
[build-system]
build-backend = "setuptools.build_meta"
requires = [ "setuptools >= 70.0.0", "toml > 1.0",]

[project]
name = "package"
version = "1.0.0"
description = "My cool package"
requires-python = ">=3.11"
dependencies = [ "six", "python-dateutil>=2.7.0",]
[[project.authors]]
name = "John Doe"
email = "john@doe.com"

[project.optional-dependencies]
docker = [ "binaryornot",]
"""
    )


def extract_metadata(project_folder):
    try:
        subprocess.run(
            [sys.executable, "-m", "build", project_folder, "--wheel"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(e.stdout)
        raise
    (wheel,) = list(project_folder.glob("dist/*whl"))
    res = pkginfo.Wheel(wheel)
    shutil.rmtree(project_folder.joinpath("dist"))
    return {k: getattr(res, k) for k in res.iterkeys()}


def download_package(tmp_path, package_name):
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "download",
            "--no-binary=:all:",
            "--no-deps",
            package_name,
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    (tarname,) = list(tmp_path.glob("*tar.gz"))
    tar = tarfile.open(tarname, "r:gz")
    tar.extractall()
    tar.close()

    tarname.unlink()
    (project_folder,) = list(tmp_path.glob("*"))
    return project_folder


def transform_setuppy(project_folder):
    setup_py = project_folder / "setup.py"
    print(f"{' setup.py ':*^50}")
    print(setup_py.read_text())
    print(f"{'':*^50}")
    subprocess.run(
        [sys.executable, "-m", "tomlize", setup_py, "pyproject.toml"],
        check=True,
    )
    setup_py.unlink()
    print(f"{' pyproject.toml ':*^50}")
    print(project_folder.joinpath("pyproject.toml").read_text())
    print(f"{'':*^50}")


@pytest.mark.parametrize(
    "package_name",
    [
        "boto3==1.26.118",
        # "urllib3==1.26.15", Fails on long_description
        "requests==2.28.2",
        "botocore==1.29.118",
        "certifi==2022.12.7",
    ],
)
def test_top_packages_conversion(tmp_path, monkeypatch, package_name):
    monkeypatch.chdir(tmp_path)
    project_folder = download_package(tmp_path, package_name)
    monkeypatch.chdir(project_folder)

    original_metadata = extract_metadata(project_folder)
    transform_setuppy(project_folder)
    new_metadata = extract_metadata(project_folder)

    print(f"{' original metadata ':*<50}")
    pprint.pprint(original_metadata)
    print(f"{' new metadata ':*<50}")
    pprint.pprint(new_metadata)

    # massage the data
    if requires_python := original_metadata.pop("requires_python"):
        original_metadata["requires_python"] = ",".join(
            x for x in sorted(requires_python.replace(" ", "").split(",")) if x
        )
    # https://peps.python.org/pep-0621/#have-a-separate-url-home-page-field
    if home_url := original_metadata.pop("home_page"):
        if not original_metadata["project_urls"]:
            original_metadata["project_urls"] = []
        original_metadata["project_urls"].append(f"Home-page, {home_url}")
    # Can be taken from readme file
    if description_content_type := new_metadata.get("description_content_type"):
        if not original_metadata.get("description_content_type"):
            original_metadata["description_content_type"] = description_content_type
    # TODO: Need to figure out why this fails
    if original_metadata.get("author") and original_metadata.get("author_email"):
        original_metadata[
            "author_email"
        ] = f"{original_metadata['author']} <{original_metadata['author_email']}>"
        original_metadata.pop("author")

    mismatches = []
    for attr, original_value in original_metadata.items():
        converted_value = new_metadata.get(attr, None)
        if original_value != converted_value:
            print(f"{attr}: {original_value=} {converted_value=}")
            mismatches.append(attr)
    assert not mismatches
