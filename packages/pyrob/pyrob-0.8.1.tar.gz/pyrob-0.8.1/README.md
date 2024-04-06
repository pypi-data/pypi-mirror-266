# pyrob

A simple CLI to help manage project package requirements

## Table of contents

- [Installation](#installation)
- [Usage](#usage)
- [Development](#development)

## Installation

```bash
pip install pyrob
```

## Usage

| Command                      | Description                                           |
| ---------------------------- | ----------------------------------------------------- |
| `pyrob init [-y]`            | Initialize a new project                              |
| `pyrob run [script]`         | Run the given command defined in project.json         |
| `pyrob install [pkgs ...]`   | Install the given packages to virtual environment     |
| `pyrob uninstall [pkgs ...]` | Uninstall the given packages from virtual environment |
| `pyrob clean`                | Remove cache artifacts (e.g. `__pycache__`)           |

## Development

A Makefile is included with targets to handle dev actions

| Command                 | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| `make venv`             | Create a virtual environment with `venv` module              |
| `make test`             | Run unit tests with `pytest`                                 |
| `make lint`             | Lint using `pylint`                                          |
| `make format`           | Format using `black`                                         |
| `make typecheck`        | Typecheck using `mypy`                                       |
| `make build`            | Build a binary wheel and a source tarball                    |
| `make release`          | Push a new tag, create a GitHub release, and publish to PyPI |
| `make install`          | Install the package globally                                 |
| `make uninstall`        | Uninstall package globally                                   |
| `make clean`            | Delete virtual environment and build/cache artifacts         |
| `make testpypi`         | Publishes current build to TestPyPI                          |
| `make install_testpypi` | Install from TestPyPI                                        |
