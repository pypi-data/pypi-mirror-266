"""
pyrob.cli
"""

import os
import sys
from argparse import ArgumentParser
from pyrob import commands, __version__


def main():
    """
    entrypoint
    """
    parser = ArgumentParser(
        prog=os.path.basename(sys.argv[0]),
        description="A CLI to manage dependencies in a Python project",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(title="command")

    init = subparsers.add_parser("init")
    init.add_argument("-y", action="store_true")
    init.set_defaults(func=commands.init)

    install = subparsers.add_parser("install")
    install.add_argument("pkgs", nargs="*")
    install.set_defaults(func=commands.install)

    uninstall = subparsers.add_parser("uninstall")
    uninstall.add_argument("pkgs", nargs="+")
    uninstall.set_defaults(func=commands.uninstall)

    run = subparsers.add_parser("run")
    run.add_argument("script", nargs="?")
    run.set_defaults(func=commands.run)

    clean = subparsers.add_parser("clean")
    clean.set_defaults(func=commands.clean)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
