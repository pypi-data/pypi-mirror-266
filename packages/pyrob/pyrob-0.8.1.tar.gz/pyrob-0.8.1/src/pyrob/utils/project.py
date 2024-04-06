"""
pyrob.utils.project
"""

from .run import run


def make_venv(venv: str) -> None:
    """
    Create a virtual environment using the venv module

    Args:
        venv: path to virtual environment directory
    """
    run(["python3", "-m", "venv", venv])
