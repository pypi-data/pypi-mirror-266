from __future__ import annotations

from pathlib import Path

from git import Repo


def test_init():
    repo: Repo = Repo.init(".")
    repo_path = Path().resolve()
    assert not repo.bare
    assert repo.git_dir == str(repo_path.joinpath(".git"))
    assert repo.working_tree_dir == str(repo_path)
