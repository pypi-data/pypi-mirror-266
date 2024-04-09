"""handles the addition of command line arguments to the script."""

from typing import Any, Callable

import click

from colorbymood.color import get_colors_from_yaml, get_frequency_from_yaml


def add_command_line_arguments(command: Callable[[], Any]) -> Callable[[], Any]:
    """
    Adds command line arguments to function

    Args:
        command (Callable[[], Any]): function to add arguments to

    Returns:
        Callable[[], Any]: function with added arguments
    """
    possible_colors = get_colors_from_yaml()

    def add_option(*args: str, **kwargs: Any) -> None:
        click.option(*args, **kwargs)(command)

    add_option(
        "-h",
        "--hue",
        "hue_",
        help="Word for hue",
        prompt="Hue word",
        type=click.Choice([str(k) for k in possible_colors["hue"].keys()]),
        required=True,
    )

    add_option(
        "-l",
        "--luminance",
        "luminance_",
        help="Word for luminance",
        prompt="luminance word",
        type=click.Choice([str(k) for k in possible_colors["luminance"].keys()]),
        required=True,
    )

    add_option(
        "-s",
        "--saturation",
        "saturation_",
        help="Word for saturation",
        prompt="saturation word",
        type=click.Choice([str(k) for k in possible_colors["saturation"].keys()]),
        required=True,
    )

    add_option(
        "-f",
        "--frequency",
        "frequency_",
        help="Word for frequency",
        prompt="frequency word",
        type=click.Choice([str(k) for k in get_frequency_from_yaml().keys()]),
        required=True,
    )

    return command
