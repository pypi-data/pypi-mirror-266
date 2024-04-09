"""handles import and conversion of color values."""

import random
from colorsys import hls_to_rgb
from typing import Union

from matplotlib.colors import rgb2hex

from colorbymood.io import load_dicts_from_yaml


def get_colors_from_yaml() -> dict[str, dict[str, float]]:
    def convert_hue(value: float, length: int) -> float:
        return ((value * 320 / (length - 1)) + 40) / 360

    colordict = load_dicts_from_yaml(filename="color.yaml")
    num_hues = len(colordict["hue"].keys())
    colordict["hue"] = {
        key: convert_hue(value=value, length=num_hues)
        for key, value in colordict["hue"].items()
    }
    return colordict


def get_frequency_from_yaml() -> dict[str, Union[str, float, list[tuple[float, ...]]]]:
    freq_dict = load_dicts_from_yaml(filename="frequency.yaml")
    return freq_dict


def hls_to_hex(hue: float, luminance: float, saturation: float) -> str:
    rgb = hls_to_rgb(h=hue, l=luminance, s=saturation)
    return rgb2hex(c=rgb)


def hex_from_dict(hue: str, saturation: str, luminance: str) -> str:
    colordict = get_colors_from_yaml()
    hls = tuple(
        colordict[cat][key]
        for cat, key in zip(
            ("hue", "luminance", "saturation"), (hue, luminance, saturation)
        )
    )
    return hls_to_hex(*hls)


def create_random_interims() -> list[tuple[float, ...]]:
    num_keys = random.randint(1, 20)
    if num_keys % 2 != 1:
        num_keys += 1
    intervals = sorted([random.random() for _ in range(num_keys)])
    intervals = [(val, abs(idx % 2)) for idx, val in enumerate(intervals)]
    interim_vals: list[tuple[float, ...]] = []
    for step, val in intervals:
        interim_vals.append((step - 0.001, abs(val - 1)))
        interim_vals.append((step, val))
    interim_vals.append((0.999, 0))
    return interim_vals
