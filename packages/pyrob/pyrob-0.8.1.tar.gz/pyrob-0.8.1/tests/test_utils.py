import os
import tempfile
from src.pyrob.utils import project

def test_create_venv():
    with tempfile.TemporaryDirectory() as tmpdirname:
        project.make_venv(tmpdirname)
        assert os.path.exists(tmpdirname)
        assert os.path.exists(f"{tmpdirname}/bin/python3")
