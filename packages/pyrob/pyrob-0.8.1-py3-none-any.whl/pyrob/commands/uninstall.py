"""pyrob.commands.uninstall"""

import os
import sys
import json
import argparse
from pyrob.utils import meta, pip
from pyrob.config.vars import VENV, PROJECT_JSON


def uninstall(args: argparse.Namespace) -> None:
    """
    Uninstall packages from virtual environment.

    Args:
        args: Command line arguments from argparse

    Raises:
        SystemExit if virtual environment or project.json not found
    """
    if not os.path.exists(VENV):
        sys.exit(f"{VENV} not found")

    try:
        doc = meta.read(PROJECT_JSON)
    except FileNotFoundError:
        sys.exit(f"{PROJECT_JSON} not found")

    pip.uninstall(*args.pkgs)
    doc["requirements"] = pip.requirements()

    with open(PROJECT_JSON, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
