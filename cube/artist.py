from typing import List

import numpy as np
from asciimatics.screen import Screen

from . import rotation

DISTANCE_TO_CAMERA = 6


class Artist:
    """A dummy class providing a 3D drawing interface."""

    __slots__ = ("screen", "h", "w", "cx", "cy", "camera_position", "camera_x", "camera_y", "camera_z")

    def __init__(self, screen: Screen):
        """Initialise the screen drawing artist."""
        self.screen = screen
        self.h = screen.height
        self.w = screen.width
        self.cx = self.w / 2
        self.cy = self.h / 2

        self.set_initial_camera()

    def set_initial_camera(self) -> None:
        """Set or reset the artist camera to the initial phase, at the diagonal above cube."""
        R = rotation.Ry(30/180*np.pi) @ rotation.Rx(30/180*np.pi)

        self.camera_position = (R @ np.array([0, 0, DISTANCE_TO_CAMERA])).flatten()
        self.camera_x = (R @ np.array([1, 0, 0])).flatten()   # "what is right"
        self.camera_y = (R @ np.array([0, 1, 0])).flatten()  # "what is up"
        self.camera_z = -(R @ np.array([0, 0, 1])).flatten()

    def line(self, pt1: np.array, pt2: np.array) -> None:
        """Draw a line from pt1 to pt2."""
        self.screen.move(*self.project3d(pt1))
        self.screen.draw(*self.project3d(pt2))

    def fill_polygon(self, polygons: List[List[np.array]], colour: int) -> None:
        """Draw a filled polygon of the given colour. Coordinates are 3D."""
        self.screen.fill_polygon(
            [[self.project3d(pt) for pt in poly] for poly in polygons], colour
        )

    # 3d to 2d projection
    def project3d(self, point: np.array) -> np.array:
        """Project a point in 3 space onto 2D coordinates for screen.

        Take a 3D point and project it into 2D to draw it, by using a
        camera given via its position vector and a "camera coordinate
        system": The vector camera_z is (the unit vector) where the camera
        is pointed (say toward the scene, which may be centered about the
        origin), and camera_x and camera_y are unit vectors to define what
        is "to the right" and "up". They should be orthogonal, and
        camera_z their (negative) cross-product.
        """
        camera_position = self.camera_position
        camera_z = self.camera_z

        P = (
            1 / camera_z.dot(point - camera_position) * (point - camera_position)
            + camera_position
        )

        x, y = P.dot(self.camera_x), P.dot(self.camera_y)

        return np.array([self.cx * (1 + x), self.cy * (1 - y)])
