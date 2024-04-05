import os
from collections import OrderedDict
from pathlib import Path

from dotenv import dotenv_values


def load_multiple_dotenvs(paths: list[Path], overwrite_existing: bool = False) -> None:
    """
    Loads multiple dotenv files, combine them and then set them as environment variables.
    :param paths: A list of paths for the .envfiles
    :param overwrite_existing: If it's true will overwrite the existing venvs.
    :return:
    """
    configs = OrderedDict()

    for path in paths:
        configs.update(dotenv_values(path))

    for k, v in configs.items():
        if k in os.environ and not overwrite_existing:
            continue
        if v is not None:
            os.environ[k] = v
