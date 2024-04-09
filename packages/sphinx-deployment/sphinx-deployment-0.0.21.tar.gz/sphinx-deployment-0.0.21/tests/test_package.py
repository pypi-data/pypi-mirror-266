from __future__ import annotations

import sys

if sys.version_info < (3, 8):
    import importlib_metadata as _metadata
else:
    import importlib.metadata as _metadata

import sphinx_deployment as m


def test_version():
    assert _metadata.version("sphinx_deployment") == m.__version__
