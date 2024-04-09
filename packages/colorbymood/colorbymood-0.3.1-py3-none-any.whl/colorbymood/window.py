"""Contains class for gui window with flashing background."""

from PyQt6.QtCore import QEasingCurve  # pylint: disable=E0611
from PyQt6.QtCore import QPropertyAnimation
from PyQt6.QtWidgets import QMainWindow  # pylint: disable=E0611

from colorbymood.color import (  # type: ignore pylint: disable=E0611
    create_random_interims,
    get_frequency_from_yaml,
)

types = QEasingCurve.Type

frequency_dict = get_frequency_from_yaml()


class Window(QMainWindow):
    """
    Class for gui window with flashing background.
    """

    curve_dict = {
        "sine": types.InOutSine,
        "well": types.OutInQuart,
        "linear": types.Linear,
        "irregular": types.OutInBounce,
    }

    def __init__(
        self,
        color: str,
        frequency: str,
    ) -> None:
        super().__init__()
        self.setStyleSheet(f"background-color: {color}")
        self.setWindowTitle("colorbymoood")
        self.add_animation()
        self.set_curve_type(curve_type=frequency_dict[frequency]["type"])  # type: ignore
        self.set_frequency(frequency=frequency_dict[frequency]["freq"])  # type: ignore
        self.set_intermediate_values(
            interim_values=frequency_dict[frequency]["ival"]  # type: ignore
        )
        self.start_animation()
        self.showFullScreen()

    def add_animation(self) -> None:
        """
        creates and adds coloranimation object to the window class.
        """
        self.color_anim = QPropertyAnimation(self, b"windowOpacity")  # type: ignore
        self.color_anim.setStartValue(1)
        self.color_anim.setEndValue(1)
        self.color_anim.setLoopCount(-1)

    def set_curve_type(self, curve_type: str) -> None:
        """ads curve type to window animation"""
        self.color_anim.setEasingCurve(Window.curve_dict[curve_type])

    def set_frequency(self, frequency: float) -> None:
        """adds frequency to window animation"""
        self.color_anim.setDuration(int(1 / frequency * 1000))

    def set_intermediate_values(self, interim_values: list[tuple[float, ...]]) -> None:
        """set intermediate values for window animation"""
        if not interim_values:
            interim_values = create_random_interims()
        for step, value in interim_values:
            self.color_anim.setKeyValueAt(step, value)

    def start_animation(self) -> None:
        """starts window animation"""
        self.color_anim.start()
