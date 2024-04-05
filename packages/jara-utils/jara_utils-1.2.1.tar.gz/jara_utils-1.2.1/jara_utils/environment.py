import os
from typing import Any

from jara_utils.exceptions import EnvironmentVariableNotFoundError
from jara_utils.normalization.boolean import str_2_bool
from jara_utils.normalization.integer import parse_int


def get_str(name: str, invalid: str | None = None, required: bool = False) -> str | None:
    if name not in os.environ and required:
        raise EnvironmentVariableNotFoundError(name)
    return str(os.environ.get(name, '')) or invalid


def get_int(name: str, invalid: int | None = None, required: bool = False) -> int | None:
    if name not in os.environ and required:
        raise EnvironmentVariableNotFoundError(name)
    return parse_int(os.environ.get(name)) or invalid


def get_bool(name: str, invalid: bool | None = None, required: bool = False) -> bool | None:
    if name not in os.environ and required:
        raise EnvironmentVariableNotFoundError(name)
    value = str_2_bool(os.environ.get(name))
    return value if value is not None else invalid


def get_list(name: str, separator: str = ',', invalid: list[Any] | None = None, required: bool = False) -> list[str]:
    if name not in os.environ and required:
        raise EnvironmentVariableNotFoundError(name)

    if invalid is None:
        invalid = []

    value = os.environ.get(name)
    return value.split(separator) if value else invalid
