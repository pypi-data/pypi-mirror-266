from typing import Literal
import numpy as np
import ramda as R
import haskellian as hk
from .. import vectors as vec

_1 = int; _2 = int; _4 = int; N = int
Vec2 = np.ndarray[_2, float]

def pq(line: np.ndarray[_1, _4]) -> tuple[Vec2, Vec2]:
    """Line endpoints (generally refered to as `p` and `q`)"""
    [[x1, y1, x2, y2]] = line
    return np.array([x1, y1]), np.array([x2, y2])

def midpoint(line: np.ndarray[_1, _4]) -> Vec2:
    p, q = pq(line)
    return (p+q)/2

@R.curry
def cluster_midpoint(lines: list[np.ndarray[_1, _4]], axis: Literal[0, 1]) -> float:
    """Mean midpoint `axis` coordinate (of all the midpoints takes the `axis` coord; then takes the mean)"""
    return np.mean(R.map(R.pipe(midpoint, R.nth(axis)), lines))

def cluster_midpoints(clusters: list[list[np.ndarray[_1, _4]]], axis: Literal[0, 1]) -> np.ndarray[N, float]:
    return np.float32(R.map(cluster_midpoint(axis=axis), clusters))

@R.curry
def pq_sort(line: np.ndarray[_1, _4], axis: int) -> np.ndarray[_1, _4]:
    """Sort line endpoints `(p, q)` by a given `axis` (`0 = x, 1 = y`)"""
    p, q = pq(line)
    return line if p[axis] < q[axis] else np.array([[*q, *p]])

def project(x: Vec2, line: np.ndarray[_1, _4]) -> Vec2:
    p, q = pq(line)
    t = vec.normalize(q-p)
    return p + t*np.dot(t, x-p)