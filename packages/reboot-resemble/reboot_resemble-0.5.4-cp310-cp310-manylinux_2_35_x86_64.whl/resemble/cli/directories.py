import git
# mypy fails with 'error: Trying to read deleted variable "exc"' if we use
# 'git.exc'
import git.exc as gitexc
import os
from contextlib import contextmanager
from resemble.cli.terminal import info


def is_on_path(file):
    """Helper to check if a file is on the PATH."""
    for directory in os.environ['PATH'].split(os.pathsep):
        if os.path.exists(os.path.join(directory, file)):
            return True
    return False


def dot_rsm_directory() -> str:
    """Helper for determining the '.rsm' directory."""
    try:
        repo = git.Repo(search_parent_directories=True)
    except gitexc.InvalidGitRepositoryError:
        return os.path.join(os.getcwd(), '.rsm')
    else:
        return os.path.join(repo.working_dir, '.rsm')


def dot_rsm_dev_directory() -> str:
    """Helper for determining the '.rsm/dev' directory."""
    return os.path.join(dot_rsm_directory(), 'dev')


@contextmanager
def chdir(directory):
    """Context manager that changes into a directory and then changes back
    into the original directory before control is returned."""
    cwd = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(cwd)


@contextmanager
def use_working_directory(working_directory: str):
    """Context manager that changes into the given working directory."""
    # Always get the absolute directory because it might not have come
    # from an rc file.
    working_directory = os.path.abspath(working_directory)

    info(f"Using working directory {working_directory}\n")

    with chdir(working_directory):
        yield
