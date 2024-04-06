"""
pyrob.commands.run
"""

import os
import sys
import subprocess
from pyrob.utils import meta, project
from pyrob.config.vars import VENV, PROJECT_JSON


def run(args) -> None:
    """
    Runs the given script.
    The script must have a key of the same name in project.json.

    Args:
        args: Command line arguments from argparse

    Raises:
        SystemExit if no script given, virtual environment not found,
        or script not in project.json scripts
    """
    if not args.script:
        sys.exit("No script given")

    if not os.path.exists(VENV):
        project.make_venv(VENV)

    try:
        script = meta.read(PROJECT_JSON)["scripts"][args.script]
        cmd = ["bash", "-c", f"source .venv/bin/activate && {script}"]
        subprocess.run(cmd, check=False)
    except (FileNotFoundError, KeyError, TypeError) as e:
        sys.exit(f"Unable to run command -> {e}")
