import subprocess
from pytest_mock import mocker
from src.pyrob.utils.run import run


def test_run_subprocess(mocker):
    string = "Hello, World!"
    command = ["echo", string]
    mocker.patch("subprocess.check_output")
    run(command)
    subprocess.check_output.assert_called_once_with(command)


def test_run_output():
    string = "Hello, World!"
    command = ["echo", string]
    assert run(command) == string
