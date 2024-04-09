from __future__ import annotations

import json
import os
import shutil
import socketserver
import typing
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from tempfile import TemporaryDirectory

import click
from git import Repo
from jinja2 import Template
from loguru import logger
from sphinx.cmd.build import build_main

from sphinx_deployment import __version__

DIR = Path(__file__).parent.resolve()

# click options
opt_input = click.option(
    "--input-path",
    "-I",
    show_default=True,
    default="docs",
    help="Path to input docs folder containing conf.py.",
)
opt_output = click.option(
    "--output-path",
    "-O",
    show_default=True,
    default=".",
    help="Path to output docs.",
)
opt_remote = click.option(
    "--remote",
    "-R",
    show_default=True,
    default="origin",
    help="Origin to push changes.",
)
opt_branch = click.option(
    "--branch",
    "-b",
    show_default=True,
    default="pages",
    help="Branch to push changes.",
)
opt_message = click.option(
    "--message",
    "-m",
    default="",
    help="Message to push changes.",
)
opt_push = click.option(
    "--push",
    "-P",
    show_default=True,
    is_flag=True,
    default=False,
    help="Push changes to remote.",
)
# click commands registry
commands = click.Group(name="deployment", help="Sphinx Deployment Commands")

# Temporary sections


@dataclass()
class Version:
    name: str
    """name of the deployment"""

    title: str
    """title of the deployment"""


@dataclass
class Versions:
    default: str = field(default="")
    """default version of the deployment"""

    versions: typing.Dict[str, Version] = field(default_factory=dict)
    """versions of the deployment"""

    def __post_init__(self) -> None:
        self.versions = {
            k: Version(**v) if isinstance(v, dict) else v
            for k, v in self.versions.items()
        }

    def add(self, name: str, title: str = "") -> Version:
        """
        Add a new version to the list of versions.

        Parameters:
            name (str): The version name of the new version.
            title (str): The title of the new version.

        Returns:
            Version: The newly added Version object.
        """
        if title == "":
            title = name
        v = Version(name=name, title=title)
        self.versions[name] = v
        return v

    def delete(self, version: str) -> bool:
        """
        Delete a version from the list of versions.

        Parameters:
            version (str): The version number of the version to delete.

        Returns:
            bool: True if the version was deleted successfully.
        """
        if version in self.versions:
            del self.versions[version]
            return True
        return False


def sync_remote(remote: str, branch: str) -> bool:
    """
    Synchronizes a remote repository with the local repository.

    Args:
        remote (str): The name of the remote repository to sync.
        branch (str): The name of the branch to fetch from the remote repository.

    Returns:
        bool: True if the synchronization was successful.
    """
    try:
        rp = Repo(".")
        rp.remote(remote).fetch(f"{branch}:{branch}")
        return True
    except Exception:
        logger.warning(f"Sync failed with {remote}/{branch}")
        return False


def list_versions(branch: str, version_path: str) -> Versions:
    """
    Retrieves a list of versions from a given branch and version path.

    Args:
        branch (str): The name of the branch to retrieve the versions from.
        version_path (str): The path to the version file within the branch.

    Returns:
        Versions: An object containing the retrieved versions.

    Raises:
        Exception: If there is an error retrieving the versions.

    Notes:
        - This function assumes that the current working directory is the root of the repository.
        - The `Versions` object is returned even if there is an error retrieving the versions, but it will be empty in that case.
    """
    try:
        rp = Repo(".")
        versions_json_content = rp.git.execute(
            command=[
                "git",
                "show",
                f"{branch}:{version_path}",
            ],
            with_extended_output=False,
            as_process=False,
            stdout_as_string=True,
        )
        version_dict = json.loads(versions_json_content)
        return Versions(**version_dict)
    except Exception:
        logger.warning(f"No versions found in branch: {branch} and creating new one")
        return Versions()


def dump_versions(version_path: str, versions: Versions) -> None:
    """
    Write the versions to a JSON file.

    Args:
        version_path (str): The path to the JSON file.
        versions (Versions): The versions to be written.

    Returns:
        None
    """
    with Path(version_path).open("w", encoding="utf-8") as f:
        json.dump(asdict(versions), f, indent=4, separators=(",", ": "))
        f.write("\n")


def push_branch(remote: str, branch: str) -> None:
    """
    Pushes a branch to a remote repository.

    Args:
        remote (str): The name of the remote repository to push to.
        branch (str): The name of the branch to push.

    Returns:
        None
    """
    rp = Repo(".")
    rp.remote(remote).push(f"{branch}:refs/heads/{branch}")
    logger.debug(f"pushed branch: {branch} to remote: {remote}")


def redirect_impl(template: Path) -> Template:
    """
    Returns a Template object by reading the contents of the file "redirect.html"
    located at the given template path.

    Args:
        template (pathlib.Path): The Path object representing the template path.

    Returns:
        jinja2.Template: The Template object created from the contents of the file.
    """
    with template.joinpath("redirect.html").open("r", encoding="utf-8") as f:
        return Template(f.read(), autoescape=True, keep_trailing_newline=True)


@contextmanager
def prepare_commit(repo: str = ".") -> typing.Any:
    """
    A context manager that commits changes in a Git repository.

    Args:
        repo (str): The path to the Git repository.

    Yields:
        typing.Any: The Git repository object.
    """
    rp = Repo(repo)

    is_detached = rp.head.is_detached
    detached_commit = rp.head.commit.hexsha
    ref = None if is_detached else rp.head.ref
    try:
        rp.git.execute(
            command=[
                "git",
                "restore",
                "--staged",
                ".",
            ]
        )
        is_dirty = rp.is_dirty()
        if is_dirty:
            rp.git.execute(
                command=[
                    "git",
                    "stash",
                ]
            )
        yield rp
    finally:
        if ref is not None:
            rp.heads[ref.name].checkout()
        if is_dirty:
            rp.git.execute(
                command=[
                    "git",
                    "stash",
                    "pop",
                ]
            )
        if is_detached:
            rp.git.execute(
                command=[
                    "git",
                    "checkout",
                    "--progress",
                    "--force",
                    detached_commit,
                ]
            )


def commit_changes(
    repo: Repo,
    message: str,
    paths: typing.List[str],
    untracked_files: bool = True,
) -> None:
    """
    Commits changes to the repository for the specified paths.

    Args:
        repo (git.repo.base.Repo): The repository object.
        message (str): The commit message.
        paths (typing.List[str]): A list of paths for which changes should be committed.
        untracked_files (bool): Whether to include untracked files in the commit.

    Returns:
        None
    """
    dirties = [
        path
        for path in paths
        if repo.is_dirty(untracked_files=untracked_files, path=path)
    ]
    if dirties:
        repo.index.add([path for path in dirties if Path(path).exists()])
        repo.index.commit(message)


# All commands go here


@commands.command(name="create", help="Create a new deployment.")
@opt_output
@opt_input
@opt_remote
@opt_branch
@opt_message
@opt_push
@click.argument("version", nargs=1, required=True)
def create_command(
    input_path: str,
    output_path: str,
    remote: str,
    branch: str,
    message: str,
    push: bool,
    version: str,
) -> None:
    logger.debug(
        f"create args: {input_path} {output_path} {remote} {branch} {message} {push} {version}"
    )
    _ = sync_remote(remote, branch)

    version_path = Path(output_path).joinpath("versions.json")
    versions = list_versions(branch, str(version_path))
    v = versions.add(version)
    if versions.default == "":
        versions.default = v.name

    os.environ["SPHINX_DEPLOYMENT_CURRENT_VERSION"] = version
    with TemporaryDirectory() as tmp:
        result = build_main(["-b", "html", input_path, tmp])
        if result == 2:
            failed = "sphinx build failed"
            raise RuntimeError(failed)

        if message == "":
            message = (
                f'Deployed {Repo(".").head} to {output_path}/{version} '
                f"with sphinx-deployment {__version__}"
            )

        t = redirect_impl(DIR.joinpath("_static", "templates"))
        redirect_render = t.render(href_to_ver=version + "/index.html")

        with prepare_commit() as repo:
            rp: Repo = repo
            if branch not in rp.heads:
                rp.git.execute(command=["git", "checkout", "--orphan", branch])
                rp.git.execute(command=["git", "rm", "-rf", "."])
            else:
                rp.heads[branch].checkout()

            dest_dir = Path(output_path).joinpath(v.name)
            shutil.rmtree(str(dest_dir), ignore_errors=True)
            shutil.copytree(tmp, str(dest_dir))

            redirect_html = Path(output_path).joinpath("index.html")
            if not redirect_html.exists():
                with redirect_html.open(
                    mode="w",
                    encoding="utf-8",
                ) as f:
                    f.write(redirect_render)

            nojekyll = Path(".nojekyll")
            if not nojekyll.exists():
                nojekyll.touch()

            dump_versions(str(version_path), versions)

            commit_changes(
                rp,
                message,
                [str(dest_dir), str(redirect_html), str(nojekyll), str(version_path)],
            )

    if push:
        push_branch(remote, branch)


@commands.command(name="delete", help="Delete a deployment.")
@opt_output
@opt_input
@opt_remote
@opt_branch
@opt_message
@opt_push
@click.argument(
    "delete",
    required=True,
    nargs=-1,
)
def delete_command(
    input_path: str,
    output_path: str,
    remote: str,
    branch: str,
    message: str,
    push: bool,
    delete: typing.Tuple[str],
) -> None:
    logger.debug(
        f"delete args: {input_path} {output_path} {remote} {branch} {message} {push} {delete}"
    )
    _ = sync_remote(remote, branch)

    version_path = Path(output_path).joinpath("versions.json")
    versions = list_versions(branch, str(version_path))

    if message == "":
        message = (
            f"Deleted {delete} from {branch} " f"with sphinx-deployment {__version__}"
        )
    with prepare_commit() as repo:
        rp: Repo = repo
        rp.heads[branch].checkout()

        all_keys = list(versions.versions.keys())
        for del_ver in delete:
            if del_ver not in all_keys:
                logger.warning(f"Version {del_ver} not found in {all_keys}")
                continue
            versions.versions.pop(del_ver)
            dest_dir = Path(output_path).joinpath(del_ver)
            rp.index.remove(str(dest_dir), working_tree=True, r=True)
            if del_ver == versions.default:
                rp.index.remove(output_path + "/index.html", working_tree=True)
                versions.default = ""

        dump_versions(str(version_path), versions)

        commit_changes(
            rp,
            message,
            [
                *[str(ver_dest) for ver_dest in delete],
                output_path + "/index.html",
                str(version_path),
            ],
        )

    if push:
        push_branch(remote, branch)


@commands.command(name="default", help="Set the default deployment.")
@opt_output
@opt_input
@opt_remote
@opt_branch
@opt_message
@opt_push
@click.argument("version", nargs=1, required=True)
def default_command(
    input_path: str,
    output_path: str,
    remote: str,
    branch: str,
    message: str,
    push: bool,
    version: str,
) -> None:
    logger.debug(
        f"default args: {input_path} {output_path} {remote} {branch} {message} {push} {version}"
    )

    version_path = Path(output_path).joinpath("versions.json")
    versions = list_versions(branch, str(version_path))

    if version not in versions.versions:
        logger.warning(f"Version not found: {version}")
        return

    versions.default = version

    t = redirect_impl(DIR.joinpath("_static", "templates"))
    redirect_render = t.render(href_to_ver=version + "/index.html")

    if message == "":
        message = (
            f'Defaulted {Repo(".").head} to {output_path}/{version} '
            f"with sphinx-deployment {__version__}"
        )

    with prepare_commit() as repo:
        rp: Repo = repo
        rp.heads[branch].checkout()

        root_redirect = Path(output_path).joinpath("index.html")
        with root_redirect.open(
            mode="w",
            encoding="utf-8",
        ) as f:
            f.write(redirect_render)
        dump_versions(str(version_path), versions)

        commit_changes(
            rp,
            message,
            [
                str(root_redirect),
                str(version_path),
            ],
        )

    if push:
        push_branch(remote, branch)


@commands.command(name="rename", help="Rename a deployment.")
@opt_output
@opt_input
@opt_remote
@opt_branch
@opt_message
@opt_push
@click.argument("src", nargs=1)
@click.argument("dst", nargs=1)
def rename_command(
    input_path: str,
    output_path: str,
    remote: str,
    branch: str,
    message: str,
    push: bool,
    src: str,
    dst: str,
) -> None:
    logger.debug(
        f"rename args: {input_path} {output_path} {remote} {branch} {message} {push} {src} {dst}"
    )

    if src == dst:
        logger.warning(f"Source and destination are the same: {src}")
        return

    _ = sync_remote(remote, branch)

    version_path = Path(output_path).joinpath("versions.json")
    versions = list_versions(branch, str(version_path))

    if src not in versions.versions:
        logger.warning(f"Version not found: {src}")
        return

    if dst in versions.versions:
        logger.warning(f"Version already exists: {dst}")
        return

    if message == "":
        message = (
            f"Renamed {src} to {dst} in {branch} "
            f"with sphinx-deployment {__version__}"
        )

    t = redirect_impl(DIR.joinpath("_static", "templates"))
    redirect_render = t.render(href_to_ver=dst + "/index.html")

    with prepare_commit() as repo:
        rp: Repo = repo
        rp.heads[branch].checkout()

        if not versions.delete(src):
            logger.warning(f"Version not found: {src}")
            return

        versions.add(dst)
        rename_src_path = output_path + "/" + src
        if not Path(rename_src_path).exists():
            logger.error(f"Source path not found: {rename_src_path}")
            return

        rename_dest_path = output_path + "/" + dst
        if Path(rename_dest_path).exists():
            logger.error(f"Destination path already exists: {rename_dest_path}")
            return

        rp.index.move([rename_src_path, rename_dest_path], skip_errors=True)

        root_redirect = Path(output_path).joinpath("index.html")
        if versions.default == src:
            versions.default = dst
            with Path(root_redirect).open(
                mode="w",
                encoding="utf-8",
            ) as f:
                f.write(redirect_render)

        dump_versions(str(version_path), versions)
        commit_changes(
            rp,
            message,
            [
                rename_src_path,
                rename_dest_path,
                str(root_redirect),
                str(version_path),
            ],
        )

    if push:
        push_branch(remote, branch)


@commands.command(name="list", help="List deployments.")
@opt_output
@opt_input
@opt_remote
@opt_branch
def list_command(input_path: str, output_path: str, remote: str, branch: str) -> None:
    logger.debug(f"list args: {input_path} {output_path} {remote} {branch}")
    _ = sync_remote(remote, branch)

    version_path = Path(output_path).joinpath("versions.json")
    versions = list_versions(branch, str(version_path))
    logger.debug("\n" + json.dumps(asdict(versions), indent=4, separators=(",", ": ")))


@commands.command(name="serve", help="Serve the versioned deployment.")
@opt_output
@opt_input
@opt_remote
@opt_branch
@click.option("--port", "-p", default=8080, help="Port to serve on")
def serve(
    input_path: str, output_path: str, remote: str, branch: str, port: int
) -> None:
    logger.debug(f"serve args: {input_path} {output_path} {remote} {branch} {port}")
    _ = sync_remote(remote, branch)

    version_path = Path(output_path).joinpath("versions.json")
    versions = list_versions(branch, str(version_path))

    with TemporaryDirectory() as tmp:
        rp = Repo(".")
        rp.git.execute(
            command=[
                "git",
                "checkout",
                branch,
                "--",
                output_path,
            ]
        )
        rp.git.execute(
            command=[
                "git",
                "restore",
                "--staged",
                output_path,
            ]
        )
        try:
            logger.info(f"Moved deployment files to {tmp}")
            shutil.move(str(version_path), tmp)
            for v in versions.versions:
                shutil.move(output_path + "/" + v, tmp)
            shutil.move(output_path + "/index.html", tmp)
            if Path(".nojekyll").exists():
                shutil.move(".nojekyll", tmp)

            os.chdir(tmp)
            with socketserver.TCPServer(("", port), SimpleHTTPRequestHandler) as httpd:
                logger.info(
                    f"Launching docs at http://localhost:{port}/ - use Ctrl-C to quit"
                )
                httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Exiting...")


if __name__ == "__main__":
    # Make the module executable
    commands()
