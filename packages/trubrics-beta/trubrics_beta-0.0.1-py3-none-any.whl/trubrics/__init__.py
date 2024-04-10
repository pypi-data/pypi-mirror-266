from importlib.metadata import version

from trubrics.sdk import Trubrics

__version__ = version("trubrics-beta")
__all__ = ["Trubrics"]
