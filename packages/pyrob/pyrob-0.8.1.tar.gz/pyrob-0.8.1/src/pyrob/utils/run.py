"""
pyrob.utils.run
"""

import subprocess


def run(cmd: list[str]) -> str:
    """
    Simple wrapper to run the given command in a subprocess

    Args:
        cmd: list containing the given command and arguments
             e.g. ['ls', '-a']

    Returns:
        stdout from subprocess
    """
    return subprocess.check_output(cmd).decode().strip()
