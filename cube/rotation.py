import numpy as np


def Rx(theta: np.float32) -> np.array:
    """Rotation by theta around x axis."""
    return np.array(
        [
            [1, 0, 0],
            [0, np.cos(theta), np.sin(theta)],
            [0, -np.sin(theta), np.cos(theta)],
        ]
    )


def Ry(theta: np.float32) -> np.array:
    """Rotation by theta around y axis."""
    return np.array(
        [
            [np.cos(theta), 0, -np.sin(theta)],
            [0, 1, 0],
            [np.sin(theta), 0, np.cos(theta)],
        ]
    )


def Rz(theta: np.float32) -> np.array:
    """Rotation by theta around z axis."""
    return np.array(
        [
            [np.cos(theta), np.sin(theta), 0],
            [-np.sin(theta), np.cos(theta), 0],
            [0, 0, 1],
        ]
    )
