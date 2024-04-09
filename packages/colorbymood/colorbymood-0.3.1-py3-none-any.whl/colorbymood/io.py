"""reading yaml files."""

from os.path import dirname
from typing import Any

from yaml import Loader, load  # pylint: disable=E0401


def load_dicts_from_yaml(filename: str) -> dict[str, Any]:
    """
    loads yaml file and converts to dict.

    Args:
        filename (str): path to file

    Returns:
        dict[str, Any]: encoded yaml file
    """
    with open(
        f"{dirname(__file__)}/{filename}", mode="r", encoding="utf-8"
    ) as dictfile:
        content: dict[str, Any] = load(dictfile, Loader)
    return content
