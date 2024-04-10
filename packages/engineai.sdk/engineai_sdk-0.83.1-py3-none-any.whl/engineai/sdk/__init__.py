"""Platform SDK package."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version
from warnings import filterwarnings

from beartype.roar import BeartypeDecorHintPep585DeprecationWarning

filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)


try:
    __version__ = version(__package__)
except PackageNotFoundError:
    __version__ = version(__package__.replace(".", "-"))
