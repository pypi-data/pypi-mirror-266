try:
    import importlib.metadata as version_reader
except ImportError:
    import importlib_metadata as version_reader

__version__ = version_reader.version("i38e-utils")
