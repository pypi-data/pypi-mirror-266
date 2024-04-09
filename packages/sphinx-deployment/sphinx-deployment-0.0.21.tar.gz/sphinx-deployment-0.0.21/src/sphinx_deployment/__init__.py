"""
Copyright (c) 2023-2024 msclock. All rights reserved.

sphinx-deployment: A versioned documentation deployment tool for sphinx.
"""


from __future__ import annotations

from ._version import version as __version__
from .sphinx_ext import setup

__all__ = [
    "__version__",  # Follow PEP 396
    "setup",  # Exposed as sphinx extension
]
