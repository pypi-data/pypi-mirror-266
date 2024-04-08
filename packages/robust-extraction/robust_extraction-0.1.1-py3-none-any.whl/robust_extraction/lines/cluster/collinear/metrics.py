from typing import Callable
import numpy as np
import ramda as R
from ... import project, pq, direction
from .... import vectors as vec

_1 = int; _2 = int; _4 = int; N = int; M = int
Vec2 = np.ndarray[_2, float]


@R.curry
def all_pairs(
    xs: np.ndarray[N, float], f: Callable[[np.ndarray, np.ndarray], float],
) -> np.ndarray[N, N]:
    n = len(xs)
    M = np.empty((n, n))
    for i in range(n):
        for j in range(i, n):
            M[i, j] = M[j, i] = f(xs[i], xs[j])
    return M

@R.curry
def proj_dist(line: np.ndarray[_1, _4], p: Vec2) -> float:
    q = project(p, line)
    return vec.dist(p, q)

def max_proj_dist(l1: np.ndarray[_1, _4], l2: np.ndarray[_1, _4]) -> float:
    """#### Maximum projection distance
    Given `l1 = (p1, q1), l2 = (p2, q2)`, computes max of distances from endpoint to line, i.e:
    >>> max { d(p1, l2), d(q1, l2), d(p2, l1), d(q2, l1) }
    """
    p1, q1 = pq(l1)
    p2, q2 = pq(l2)
    dp2 = proj_dist(l1, p2)
    dq2 = proj_dist(l1, q2)
    dp1 = proj_dist(l2, p1)
    dq1 = proj_dist(l2, q1)
    return max(dp2, dq2, dp1, dq1)
