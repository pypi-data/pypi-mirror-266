# Fixtures

from pathlib import Path

import pytest


@pytest.fixture
def data_path(request) -> Path:
    """Provide the path to the `data_files` folder.

    :param request: Pytest request object.

    :return: Path to the folder
    """
    curr = Path(request.fspath).parents[0]
    return Path(curr).joinpath("data").absolute()
