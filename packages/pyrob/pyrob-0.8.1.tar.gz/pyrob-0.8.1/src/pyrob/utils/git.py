"""
pyrob.utils.git
"""

import os
from pyrob.config.vars import GITIGNORE_URL
from .run import run


def init() -> None:
    """
    Initialize git repository
    """
    if not os.path.exists(".git"):
        run(["git", "init"])


def get_config() -> tuple[str, str]:
    """
    Get username and email from git config.

    Returns:
        tuple with username and email
    """
    user = run(["git", "config", "user.name"])
    email = run(["git", "config", "user.email"])
    return user, email


def get_gitignore(path: str) -> None:
    """
    Fetches a .gitignore from GitHub's .gitignore template repo

    Args:
        path: The path at which to save the .gitignore file
    """
    os.system(" ".join(["curl", "-s", GITIGNORE_URL, f"> {path}/.gitignore"]))
