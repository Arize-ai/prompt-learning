from importlib.metadata import PackageNotFoundError, version

from arize_toolkit.client import Client

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["Client", "__version__"]
