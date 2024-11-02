import os
import sys
from inspect import cleandoc
from pathlib import Path
from shutil import which

from invoke import task

PKG_NAME = "webassets"
PKG_PATH = Path(f"pelican/plugins/{PKG_NAME}")
TOOLS = ["pre-commit"]

ACTIVE_VENV = os.environ.get("VIRTUAL_ENV", None)
VENV_HOME = Path(os.environ.get("WORKON_HOME", "~/.local/share/virtualenvs"))
VENV_PATH = Path(ACTIVE_VENV) if ACTIVE_VENV else (VENV_HOME.expanduser() / PKG_NAME)
VENV = str(VENV_PATH.expanduser())
BIN_DIR = "bin" if os.name != "nt" else "Scripts"
VENV_BIN = Path(VENV) / Path(BIN_DIR)
PTY = True if os.name != "nt" else False


@task
def tests(c):
    """Run the test suite."""
    c.run("uv run pytest", pty=PTY)


@task
def ruff(c, fix=False, diff=False):
    """Run Ruff to ensure code meets project standards."""
    diff_flag, fix_flag = "", ""
    if fix:
        fix_flag = "--fix"
    if diff:
        diff_flag = "--diff"
    c.run(f"uv run ruff check {diff_flag} {fix_flag} .", pty=PTY)


@task
def lint(c, fix=False, diff=False):
    """Check code style via linting tools."""
    ruff(c, fix=fix, diff=diff)


@task
def uv(c):
    """Install uv in the local virtual environment."""
    if not which("uv"):
        print("** Installing uv in the project virual environment.")
        c.run(f"{VENV_BIN}/python -m pip install uv", pty=PTY)


@task(pre=[uv])
def tools(c):
    """Install development tools in the virtual environment if not already on PATH."""
    for tool in TOOLS:
        if not which(tool):
            print(f"** Installing {tool}.")
            c.run(f"uv pip install {tool}")


@task(pre=[tools])
def precommit(c):
    """Install pre-commit hooks to `.git/hooks/pre-commit`."""
    print("** Installing pre-commit hooks.")
    pre_commit_cmd = (
        which("pre-commit") if which("pre-commit") else f"{VENV_BIN}pre-commit"
    )
    c.run(f"{pre_commit_cmd} install")


@task
def setup(c):
    """Set up the development environment. You must have `uv` installed."""
    if not which("uv"):
        error_message = """
            uv is not installed, and there is no active virtual environment available.
            You can either manually create and activate a virtual environment, or you can
            install uv by running the following command:

            curl -LsSf https://astral.sh/uv/install.sh | sh

            Once you have taken one of the above two steps, run `invoke setup` again.
            """  # noqa: E501
        sys.exit(cleandoc(error_message))

    global ACTIVE_VENV
    if not ACTIVE_VENV:
        print("** Creating a virtual environment.")
        c.run("uv venv")
        ACTIVE_VENV = ".venv"

    tools(c)
    c.run("uv sync")
    precommit(c)
    success_message = """
        Development environment should now be set up and ready.

        To enable running invoke, either run it with `uv run inv` or
        activate the virtual environment with `source .venv/bin/activate`
        """
    print(cleandoc(success_message))
