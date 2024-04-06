"""
pyrob.commands.install
"""

import os
import sys
import tempfile
from argparse import Namespace
from pyrob.utils import project, meta, pip
from pyrob.config.vars import VENV, PROJECT_JSON


def install(args: Namespace) -> None:
    """
    Install dependencies to virtual environment

    Args:
        args: Command line arguments from argparse
    """
    if not os.path.exists(VENV):
        project.make_venv(VENV)

    print("Installing packages...")

    if len(args.pkgs) > 0:
        install_from_args(args.pkgs)
    else:
        install_from_meta()


def install_from_args(pkgs: list[str]) -> None:
    """
    Install packages from given sequence and updates project.json.
    Creates project.json file if not exists.

    Args:
        pkgs: List of packages to install to virtual environment
    """
    doc = {}

    try:
        doc = meta.read(PROJECT_JSON)
    except FileNotFoundError:
        pass

    pip.install_from_args(*pkgs)
    doc["requirements"] = pip.requirements()
    meta.write(PROJECT_JSON, doc)
    print("Installed:", *pkgs)


def install_from_meta() -> None:
    """
    Install packages from requirements in project.json.

    Raises:
        TypeError: if project.json parsing does not return dict
        SystemExit: if project.json not found, is a list, or requirements key not in project.json
    """
    fd, tmp_req_path = tempfile.mkstemp()

    try:
        doc = meta.read(PROJECT_JSON)
        reqs = doc["requirements"]

        if not isinstance(reqs, dict):
            raise TypeError(f"{PROJECT_JSON} requirements must be dict[str, str]")

        # cast dict to str of package==version pairs separated by newlines
        # same format as returned by 'pip freeze'
        reqs_txt = "\n".join([f"{pkg}=={ver}" for pkg, ver in reqs.items()])

        with os.fdopen(fd, "w") as tmp:
            tmp.write(reqs_txt)

        pip.install_from_reqs(tmp_req_path)

    except (FileNotFoundError, KeyError, TypeError) as e:
        sys.exit(f"Unable to install -> {e}")

    finally:
        os.remove(tmp_req_path)
