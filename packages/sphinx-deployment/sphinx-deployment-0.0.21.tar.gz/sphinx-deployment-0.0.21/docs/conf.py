from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(Path("../src").resolve())

project = "sphinx-deployment"
copyright = "2023-2024, msclock"
author = "msclock"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinx_inline_tabs",
    "sphinx_deployment",
]

source_suffix = [".rst", ".md"]
exclude_patterns = [
    "_build",
    "**.ipynb_checkpoints",
    "Thumbs.db",
    ".DS_Store",
    ".env",
    ".venv",
]

html_theme = "furo"

myst_enable_extensions = [
    "colon_fence",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/", None),
    "jinja2": ("https://jinja.palletsprojects.com/", None),
    "git": ("https://gitpython.readthedocs.io/en/latest/", None),
}

nitpick_ignore = [
    ("py:class", "_io.StringIO"),
    ("py:class", "_io.BytesIO"),
]

always_document_param_types = True

sphinx_deployment_dll = {
    "Links": {
        "Repository": "https://github.com/msclock/sphinx-deployment/",
        "Index": "https://pypi.org/project/sphinx-deployment/",
    }
}
