from __future__ import annotations

import pytest

from sphinx_deployment.cli import Versions


@pytest.fixture()
def versions():
    return Versions()


def test_add(versions: Versions):
    assert len(versions.versions) == 0

    versions.add("v1")
    assert len(versions.versions) == 1
    assert "v1" in versions.versions
    assert versions.versions["v1"].name == "v1"
    assert versions.versions["v1"].title == "v1"

    versions.add("v2", "Version 2")
    assert len(versions.versions) == 2
    assert "v2" in versions.versions
    assert versions.versions["v2"].name == "v2"
    assert versions.versions["v2"].title == "Version 2"


def test_delete(versions: Versions):
    versions.add("v1")
    versions.add("v2")

    assert len(versions.versions) == 2

    assert versions.delete("v1") is True
    assert len(versions.versions) == 1
    assert "v1" not in versions.versions

    assert versions.delete("v3") is False
    assert len(versions.versions) == 1
