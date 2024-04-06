"""
pyrob.utils.meta
"""

import sys
import json


def read(file: str) -> dict:
    """
    Read the given as a json doc.

    Args:
        file: filepath to read

    Raises:
        JSONDecodeError: if file cannot be parsed as JSON
        TypeError: if parsing does not return dict

    Returns:
        dict cast from given json doc
    """
    try:
        with open(file, "r", encoding="utf-8") as f:
            doc = json.load(f)

            if not isinstance(doc, dict):
                raise TypeError(f"{file} must be dict. Received {type(doc)}")

            return doc

    except (json.decoder.JSONDecodeError, TypeError) as e:
        sys.exit(str(e))


def write(file: str, data: dict) -> None:
    """
    Write the given doc to the given path as JSON

    Args:
        file: filepath to write to
        data: dict to write as JSON
    """
    with open(file, "w+", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
