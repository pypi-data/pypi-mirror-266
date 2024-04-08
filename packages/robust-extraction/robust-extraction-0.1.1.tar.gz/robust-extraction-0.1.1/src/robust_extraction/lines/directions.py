import numpy as np
from . import pq
from .. import vectors as vec

_1 = int; _2 = int; _4 = int
Vec2 = np.ndarray[_2, float]

def angle(line: np.ndarray[_1, _4]) -> float:
    """Angle in `[-pi/2, pi/2]`"""
    [[x1, y1, x2, y2]] = line
    dx = x2 - x1
    dy = y2 - y1
    return np.arctan(dy/dx) if dx != 0 else np.pi/2

def angle2(line: np.ndarray[_1, _4]) -> float:
    """Angle in `[-pi, pi]`"""
    [[x1, y1, x2, y2]] = line
    dx = x2 - x1
    dy = y2 - y1
    return np.arctan2(dy, dx)

def direction(line: np.ndarray[_1, _4]) -> Vec2:
    """Unit direction vector"""
    p, q = pq(line)
    return vec.normalize(q - p)

def flip(line: np.ndarray[_1, _4]) -> np.ndarray[_1, _4]:
    """Exchange `x` and `y` endpoint coords"""
    [[x1, y1, x2, y2]] = line
    return np.int32([[y1, x1, y2, x2]])