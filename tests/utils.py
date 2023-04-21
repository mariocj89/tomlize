"""Testing utilities"""
import subprocess
import sys


def validate_pyproject(pyp_path):
    p = subprocess.run(
        [sys.executable, "-m", "validate_pyproject", pyp_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if p.returncode != 0:
        print(p.stdout)
        raise Exception(f"{pyp_path} is invalid")
