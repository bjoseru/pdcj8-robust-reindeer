from enum import IntEnum
from typing import NamedTuple


class HelpEntry(NamedTuple):
    """
    Helper class to hold help information and extract help from markdown files.
    """
    name: str
    description: str


class KeyboardCommand(IntEnum):
    """Enum detailing Keyboard Commands to do operations on the Cube view."""

    rotate_front_ccw = ord("f")
    rotate_front_cw = ord("F")

    rotate_top_ccw = ord("t")
    rotate_top_cw = ord("T")

    rotate_middle_ccw = ord("m")
    rotate_middle_cw = ord("M")

    rotate_back_ccw = ord("b")
    rotate_back_cw = ord("B")

    rotate_bottom_ccw = ord("d")
    rotate_bottom_cw = ord("D")

    rotate_left_ccw = ord("l")
    rotate_left_cw = ord("L")

    rotate_right_ccw = ord("r")
    rotate_right_cw = ord("R")

    reset_view = ord("z")

    help = ord("h")
    quit = ord("q")
