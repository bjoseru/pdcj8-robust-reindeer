#!/usr/bin/env python
# coding: utf-8
from itertools import product
import logging
import time
from typing import Tuple, Union

import numpy as np
from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.screen import ManagedScreen, Screen

from . import rotation
from .artist import Artist, DISTANCE_TO_CAMERA
from .cube import Cube
from .data_structures import KeyboardCommand
from .help import show_help, BRIEF_HELP_TEXT

logging.basicConfig(level=logging.INFO, filename="cube.log")
log = logging.getLogger()

def rotate_face(face: np.array, axis: str, clockwise: bool):
    """Rotate a face of the cube."""
    direction = 1 if clockwise else -1

    rotate = getattr(Cube, "rotate_" + axis)
    for cube in face.flatten():
        rotate(cube, direction * np.pi / 2 )

    if axis == "z":
        direction *= -1

    face[:] = np.rot90(face, -direction)

@ManagedScreen
def main_event_loop(screen: Screen = None) -> None:
    """The main event loop that redraws the screen and takes user input."""
    # create an artist to draw the individual cubes
    artist = Artist(screen)

    # the Rubik cube is made up of 27 individual cubes
    rubik_cube = np.array(
        [ Cube(np.array(coord)) for coord in product((-1, 0, 1), (1, 0, -1), (1, 0, -1)) ],
        dtype=object,
    ).reshape(3, 3, 3)

    # DEBUG: restrict to 2 cubes for easier troubleshooting:
    # rubik_cube = [rubik_cube[0], rubik_cube[-1]]

    last_time = time.time_ns()
    key, mouse_x, mouse_y, mouse_buttons = 0, 0, 0, 0
    distance = 0
    camera_2d = np.array([0, 0])
    start_pos = np.array([0, 0])
    auto_mouse = True

    while True:
        ev = screen.get_event()
        if isinstance(ev, KeyboardEvent):
            key = ev.key_code
            # Stop on ctrl+q or ctrl+x, or simply on q/Q
            if key == KeyboardCommand.quit:
                # raise StopApplication("User terminated app")
                return
            elif key == KeyboardCommand.rotate_front_ccw:  # rotate front disc counter-clockwise
                rotate_face(face=rubik_cube[:, :, 0], axis="z", clockwise=False)
            elif key == KeyboardCommand.rotate_front_cw:  # rotate front disc clockwise
                rotate_face(face=rubik_cube[:, :, 0], axis="z", clockwise=True)
            elif key == KeyboardCommand.rotate_top_cw:  # rotate top disc clockwise
                rotate_face(face=rubik_cube[:, 0], axis="y", clockwise=True)
            elif key == KeyboardCommand.rotate_top_ccw:  # rotate top disc counter-clockwise
                rotate_face(face=rubik_cube[:, 0], axis="y", clockwise=False)
            elif key == KeyboardCommand.rotate_middle_ccw:  # rotate middle disk counter-clockwise
                rotate_face(face=rubik_cube[:, :, 1], axis="z", clockwise=False)
            elif key == KeyboardCommand.rotate_middle_cw:
                rotate_face(face=rubik_cube[:, :, 1], axis="z", clockwise=True)
            elif key == KeyboardCommand.rotate_back_ccw:  # rotate back disk counter-clockwise
                rotate_face(face=rubik_cube[:, :, 2], axis="z", clockwise=False)
            elif key == KeyboardCommand.rotate_back_cw:  # rotate back disk clockwise
                rotate_face(face=rubik_cube[:, :, 2], axis="z", clockwise=True)
            elif key == KeyboardCommand.rotate_bottom_ccw:
                rotate_face(face=rubik_cube[:, 2], axis="y", clockwise=False)
            elif key == KeyboardCommand.rotate_bottom_cw:
                rotate_face(face=rubik_cube[:, 2], axis="y", clockwise=True)
            elif key == KeyboardCommand.rotate_left_ccw:
                rotate_face(face=rubik_cube[0], axis="x", clockwise=False)
            elif key == KeyboardCommand.rotate_left_cw:
                rotate_face(face=rubik_cube[0], axis="x", clockwise=True)
            elif key == KeyboardCommand.rotate_right_ccw:
                rotate_face(face=rubik_cube[2], axis="x", clockwise=False)
            elif key == KeyboardCommand.rotate_right_cw:
                rotate_face(face=rubik_cube[2], axis="x", clockwise=True)
            elif key == KeyboardCommand.reset_view:
                artist.set_initial_camera()
            elif key == KeyboardCommand.help:
                # could show a widget here that explains usage and
                # keys, then waits for key press
                show_help(screen, log)
        elif isinstance(ev, MouseEvent):
            mouse_x, mouse_y, mouse_buttons = ev.x, ev.y, ev.buttons
            if mouse_buttons:
                auto_mouse = not auto_mouse
                log.info("setting mouse to %s, mouse event is %s", auto_mouse, ev)
                start_pos = np.array([mouse_x, mouse_y])

            elif auto_mouse:
                end_pos = np.array([mouse_x, mouse_y])

                camera_2d += end_pos - start_pos
                camera_2d_normalised = (
                    camera_2d / (screen.width, screen.height) * np.pi
                )
                alpha, beta = camera_2d_normalised

                R = rotation.Ry(alpha) @ rotation.Rx(beta)
                camera_x = (R @ np.array([1, 0, 0])).flatten()
                camera_y = (R @ np.array([0, 1, 0])).flatten()
                camera_z = -(R @ np.array([0, 0, 1])).flatten()

                artist.camera_position = -camera_z * DISTANCE_TO_CAMERA
                artist.camera_x = camera_x
                artist.camera_y = camera_y
                artist.camera_z = camera_z

                start_pos = end_pos

            else:
                log.info("not registering mouse movement because auto-mouse has been disabled.")

        current_time = time.time_ns()
        if not current_time == last_time:
            frames_per_second = 1e9 / (current_time - last_time)
        else:
            frames_per_second = 0
        last_time = current_time

        screen.clear_buffer(0, 0, 0)
        screen.print_at(
            f"""{screen.width=}, {screen.height=}, {len(rubik_cube)=}
{frames_per_second=:5.1f} {key=:4d} {mouse_x=:4d}, {mouse_y=:4d} {mouse_buttons=} {distance=:5.1f} {auto_mouse=}""",
            0,
            0,
        )
        screen.print_at(BRIEF_HELP_TEXT, 0, 3)

        def cube_camera_distance(cube: Cube) -> np.float32:
            """Return distance of cube centre point to the camera."""
            return np.linalg.norm(artist.camera_position - cube.position)

        # draw each individual cube, start with those furthest away from the camera:
        for cube in sorted(
            rubik_cube.flatten(), key=cube_camera_distance, reverse=True
        ):
            cube.draw_block_faces(artist)
            cube.draw_cage(artist)

        # these are the cubes in the top layer:
        top_layer = rubik_cube[::-1, 0].T.flatten()[::-1]
        top_colours = [
            cube.get_face_colour(np.array([0, 1, 0])) for cube in top_layer
        ]  # [0,1,0] is the direction pointing up
        # screen.print_at(f"{top_colours=}",0,5)
        for i, c in enumerate(top_colours):
            screen.print_at(
                "T",
                screen.width - 6 + (i % 3),
                screen.height - 12 + (i // 3),
                c,
            )
        # these are the cubes in the front layer:
        front_layer = rubik_cube[:, :, 0].T.flatten()
        front_colours = [
            cube.get_face_colour(np.array([0, 0, 1])) for cube in front_layer
        ]
        # screen.print_at(f"{front_colours=}",0,6)
        for i, c in enumerate(front_colours):
            screen.print_at(
                "F",
                screen.width - 6 + (i % 3),
                screen.height - 9 + (i // 3),
                c,
            )
        # these are the cubes in the bottom layer:
        bottom_layer = rubik_cube[:, 2].T.flatten()
        bottom_colours = [
            cube.get_face_colour(np.array([0, -1, 0])) for cube in bottom_layer
        ]
        # screen.print_at(f"{bottom_colours=}",0,6)
        for i, c in enumerate(bottom_colours):
            screen.print_at(
                "D",
                screen.width - 6 + (i % 3),
                screen.height - 6 + (i // 3),
                c,
            )
        # these are the cubes in the rear layer:
        rear_layer = rubik_cube[::-1, :, 2].T.flatten()[::-1]
        rear_colours = [
            cube.get_face_colour(np.array([0, 0, -1])) for cube in rear_layer
        ]
        # screen.print_at(f"{rear_colours=}",0,6)
        for i, c in enumerate(rear_colours):
            screen.print_at(
                "B",
                screen.width - 6 + (i % 3),
                screen.height - 3 + (i // 3),
                c,
            )

        # these are the cubes in the left layer:
        left_layer = rubik_cube[0, ::-1].flatten()[::-1]
        left_colours = [
            cube.get_face_colour(np.array([-1, 0, 0])) for cube in left_layer
        ]
        # screen.print_at(f"{left_colours=}",0,6)
        for i, c in enumerate(left_colours):
            screen.print_at(
                "L",
                screen.width - 9 + (i % 3),
                screen.height - 9 + (i // 3),
                c,
            )
        # these are the cubes in the right layer:
        right_layer = rubik_cube[2].flatten()
        right_colours = [
            cube.get_face_colour(np.array([1, 0, 0])) for cube in right_layer
        ]
        # screen.print_at(f"{right_colours=}",0,6)
        for i, c in enumerate(right_colours):
            screen.print_at(
                "R",
                screen.width - 3 + (i % 3),
                screen.height - 9 + (i // 3),
                c,
            )

        screen.refresh()

main_event_loop()
