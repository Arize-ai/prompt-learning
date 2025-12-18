"""
Version information for the CLI.
"""

import tomllib
from pathlib import Path


def get_version():
    """Get version from pyproject.toml"""
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        return "unknown"


__version__ = get_version()
