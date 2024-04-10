import numpy as np
from .. import intersect

_1 = int; _2 = int; _4 = int; N = int; M = int
Vec2 = np.ndarray[_2, float]

def mean_intersect(
    ls1: np.ndarray[N, tuple[_1, _4]],
    ls2: np.ndarray[M, tuple[_1, _4]],
    as_segment: bool = True
) -> np.ndarray[_1, _2] | None:
    """Intersects all pairs in `ls1 x ls2` and returns the mean of all intersections
    - `as_segment`: whether to check if the intersection belongs to the segments
    - Cost `O(n*m)` (yeah, not cool)
    """
    xs = []
    for l1 in ls1:
        for l2 in ls2:
            if (x := intersect(l1, l2, as_segment=as_segment)) is not None:
                xs += [x]
    return np.mean(xs, axis=0) if len(xs) > 0 else None

def intersect_all(
    rows: list[list[np.ndarray[_1, _4]]],
    cols: list[list[np.ndarray[_1, _4]]],
) -> dict[tuple[int, int], Vec2]:
    xs = {}
    for i, row in enumerate(rows):
        for j, col in enumerate(cols):
            if (x := mean_intersect(row, col)) is not None:
                xs[i, j] = x
    return xs