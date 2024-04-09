"""
entry point to the colorbymood program.
"""

import sys

import click
from PyQt6.QtWidgets import QApplication  # pylint: disable=E0611

import colorbymood
from colorbymood import Window, hex_from_dict
from colorbymood.click_utils import add_command_line_arguments


@click.command()
@click.version_option(version=colorbymood.__version__)
@add_command_line_arguments  # type: ignore
def main(
    hue_: str,
    saturation_: str,
    luminance_: str,
    frequency_: str,
) -> None:
    """
    Opens the gui window

    Args:
        hue_ (str): value for hue in the color.yaml file
        saturation_ (str): value for saturation in color.yaml file
        luminance_ (str): value for luminance in color.yaml file
        frequency_ (str): value for frequency in frequency.yaml file
    """
    app = QApplication(sys.argv)
    _ = Window(
        color=hex_from_dict(hue=hue_, saturation=saturation_, luminance=luminance_),
        frequency=frequency_,
    )
    sys.exit(app.exec())
