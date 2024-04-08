"""
Utilities for getting metadata about your own package.
"""

import importlib.metadata
import inspect
from pathlib import Path


def _get_root_directory(caller: inspect.FrameInfo) -> Path:
    """
    Return the root directory of the calling module, accounting for submodules.

    For example, if the calling module is `foo.bar.baz`, and `foo` is located
    at `/home/user/foo`, this function will return `/home/user/foo`.
    """
    caller_dir = Path(caller.filename).resolve().parent

    # How deep is this submodule?
    depth = caller.frame.f_globals["__name__"].count(".")

    for _ in range(depth):
        caller_dir = caller_dir.parent

    return caller_dir


def get_package_version(own_package_pypi_name: str) -> str:
    """
    Determine the version of **the calling package**. `own_package_pypi_name` is
    the name of the package, as you would type to install it from pypi.

    You can **not use this function to look up any packages other than your
    own**.
    """

    # Try to just ask python
    try:
        return importlib.metadata.version(own_package_pypi_name)
    except importlib.metadata.PackageNotFoundError:
        pass

    # While the approach above is clean, it fails during development. In that
    # case, read the version from the `pyproject.toml` file.
    import tomllib

    caller_frame = inspect.stack()[1]
    toml_path = _get_root_directory(caller_frame) / "pyproject.toml"

    try:
        with open(toml_path, "rb") as f:
            toml_contents = tomllib.load(f)

    except FileNotFoundError:
        raise RuntimeError(f"Cannot find `pyproject.toml` at `{toml_path}`") from None

    except tomllib.TOMLDecodeError as e:
        raise RuntimeError(f"`{toml_path}` is invalid TOML: {e}") from None

    try:
        return toml_contents["tool"]["poetry"]["version"]
    except KeyError:
        raise RuntimeError(
            f"`{toml_path}` does not contain a `tool.poetry.version` field"
        ) from None
