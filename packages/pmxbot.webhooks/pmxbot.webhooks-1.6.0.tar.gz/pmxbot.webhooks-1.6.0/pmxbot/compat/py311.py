import sys

__all__ = ['resources']


if sys.version_info < (3, 12):
    import importlib_resources as resources
else:
    from importlib import resources
