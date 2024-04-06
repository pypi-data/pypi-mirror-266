import os
import tempfile
import json
import pytest
from src.pyrob.utils import meta


def test_read_json():
    fd, test_path = tempfile.mkstemp()
    test_dict = {"hello": "world!"}

    with os.fdopen(fd, "w") as tmp:
        json.dump(test_dict, tmp)

    assert test_dict == meta.read(test_path)
    os.remove(test_path)


def test_read_json_raise():
    fd, test_path = tempfile.mkstemp()
    test = [{"foo": "bar"}]

    with os.fdopen(fd, "w") as tmp:
        json.dump(test, tmp)

    with pytest.raises(SystemExit) as excinfo:
        meta.read(test_path)

    assert excinfo.type is SystemExit
    os.remove(test_path)
