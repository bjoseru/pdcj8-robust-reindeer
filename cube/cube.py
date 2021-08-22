import numpy as np
from asciimatics.screen import Screen

from . import rotation
from .artist import Artist


class Cube:
    """A 1x1x1 cube."""

    __slots__ = ("front", "back", "normal_vectors", "colours", "position")

    def __init__(self, position: np.array = np.array([0, 0, 0])):
        self.position = position

        # define corner points of front face and back face, starting in top left, going clockwise
        front = [
            np.array(
                [-1, 1, 1]
            ),  # (x,y,z) coordinates of each point, z is 1 for all front points
            np.array([1, 1, 1]),
            np.array([1, -1, 1]),
            np.array([-1, -1, 1]),
        ]

        back = [
            np.array([-1, 1, -1]),
            np.array([1, 1, -1]),
            np.array([1, -1, -1]),
            np.array([-1, -1, -1]),
        ]

        self.front = [
            pt / 2 + position for pt in front
        ]  # make the cubes side lengths equal to one
        self.back = [pt / 2 + position for pt in back]

        self.normal_vectors = {
            "front": [0, 0, 1],
            "back": [0, 0, -1],
            "left": [-1, 0, 0],
            "right": [1, 0, 0],
            "top": [0, 1, 0],
            "bottom": [0, -1, 0],
        }

        # taking colours from here:
        # https://en.wikipedia.org/wiki/Rubik%27s_Cube#/media/File:Rubik's_cube_colors.svg
        self.colours = {
            "front": Screen.COLOUR_RED,
            "back": Screen.COLOUR_MAGENTA,  # there's no orange, unfortunately
            "left": Screen.COLOUR_YELLOW,
            "right": Screen.COLOUR_WHITE,
            "top": Screen.COLOUR_GREEN,
            "bottom": Screen.COLOUR_BLUE,
        }

    def draw_cage(self, artist: Artist) -> None:
        """Draw self as wireframe using artist."""
        if artist.camera_position[0] == 0:  # only draw for the initial face
            for pt1, pt2 in zip(self.front, [*self.front[1:], self.front[0]]):
                artist.line(pt1, pt2)
            for pt1, pt2 in zip(self.back, [*self.back[1:], self.back[0]]):
                artist.line(pt1, pt2)
            for pt1, pt2 in zip(self.front, self.back):
                artist.line(pt1, pt2)

    def draw_block_faces(self, artist: Artist) -> None:
        """Draw self with solid colored faces using artist."""
        camera_direction = artist.camera_position

        # front
        if np.inner(camera_direction, self.normal_vectors["front"]) > 0:
            artist.fill_polygon(
                [
                    self.front,
                ],
                self.colours["front"],
            )
        # back
        if np.inner(camera_direction, self.normal_vectors["back"]) > 0:
            artist.fill_polygon(
                [
                    self.back[::-1],
                ],
                self.colours["back"],
            )
        # left
        if np.inner(camera_direction, self.normal_vectors["left"]) > 0:
            artist.fill_polygon(
                [
                    [
                        self.front[0],
                        self.back[0],
                        self.back[3],
                        self.front[3],
                    ]
                ],
                self.colours["left"],
            )
        # right
        if np.inner(camera_direction, self.normal_vectors["right"]) > 0:
            artist.fill_polygon(
                [
                    [
                        self.front[1],
                        self.front[2],
                        self.back[2],
                        self.back[1],
                    ]
                ],
                self.colours["right"],
            )
        # top
        if np.inner(camera_direction, self.normal_vectors["top"]) > 0:
            artist.fill_polygon(
                [
                    [
                        self.front[0],
                        self.front[1],
                        self.back[1],
                        self.back[0],
                    ]
                ],
                self.colours["top"],
            )
        # bottom
        if np.inner(camera_direction, self.normal_vectors["bottom"]) > 0:
            artist.fill_polygon(
                [
                    [
                        self.front[2],
                        self.front[3],
                        self.back[3],
                        self.back[2],
                    ]
                ],
                self.colours["bottom"],
            )

    def get_face_colour(self, face_normal: np.array) -> int:
        """Determine the colour of a particular face."""
        # list of faces and how well they align with the given face_normal:
        face_list = [
            (face, np.inner(face_normal, normal))
            for face, normal in self.normal_vectors.items()
        ]
        # sort the list by alignment, pick the largest, return the corresponding face colour
        return self.colours[sorted(face_list, key=lambda x: x[1], reverse=True)[0][0]]

    def __rotation_update__(self, R: np.matrix) -> None:
        """Multiply each point in this object by rotation matrix R."""
        self.front = [R.dot(pt).flatten() for pt in self.front]
        self.back = [R.dot(pt).flatten() for pt in self.back]
        self.position = R.dot(self.position).flatten()
        self.normal_vectors = {
            face: R.dot(normal).flatten()
            for face, normal in self.normal_vectors.items()
        }

    def rotate_x(self, theta: np.float32) -> None:
        """Rotate entire object around x axis by angle theta [radians]."""
        R = rotation.Rx(theta)
        self.__rotation_update__(R)

    def rotate_y(self, theta: np.float32) -> None:
        """Rotate entire object around z axis by angle theta [radians]."""
        R = rotation.Ry(theta)
        self.__rotation_update__(R)

    def rotate_z(self, theta: np.float32) -> None:
        """Rotate entire object around z axis by angle theta [radians]."""
        R = rotation.Rz(theta)
        self.__rotation_update__(R)
