import numpy as np
import ramda as R
from haskellian.core import safe
from .. import contours as cs
from . import pq

_1 = int; _2 = int; _4 = int; N = int
Vec2 = np.ndarray[_2, float]

@R.curry
def yintersect(line: np.ndarray[_1, _4], y: float) -> float:
    """Returns `x` s.t. `(x, y)` belongs to `line`"""
    [[x1, y1, x2, y2]] = line
    p = np.array([x1, y1])
    q = np.array([x2, y2])
    t = q-p
    return p[0] + (y-p[1])*t[0]/t[1]

@R.curry
def xintersect(line: np.ndarray[_1, _4], x: float) -> float:
    """Returns `y` s.t. `(x, y)` belongs to `line`"""
    [[x1, y1, x2, y2]] = line
    p = np.array([x1, y1])
    q = np.array([x2, y2])
    t = q-p
    return p[1] + (x-p[0])*t[1]/t[0]

@R.curry
def intersect(
    seg1: np.ndarray[_1, _4],
    seg2: np.ndarray[_1, _4],
    as_segment: bool = True
) -> Vec2 | None:
    """Intersects segments or lines. 
    - `as_segment`: whether to check if the intersection belongs to the segments
    - Returns `None` if they don't intersect (because they're parallel or `as_segment`
        is true and the intersection point doesn't belong to the segments
    """
    [[x1, y1, a1, b1]] = seg1
    p1 = np.array([x1, y1])
    q1 = np.array([a1, b1])
    [[x2, y2, a2, b2]] = seg2
    p2 = np.array([x2, y2])
    q2 = np.array([a2, b2])
    t1 = q1 - p1
    t2 = q2 - p2
    # L1: p1 + alpha*t1 for alpha in [0, 1]
    # L2: p2 + beta*t2  for beta in [0, 1]
    # we solve for alpha and beta s.t. L1 = L2
    # [t1x -t2x] [alpha] = [p2x - p1x]
    # [t1y -t2y] [beta]  = [p2y - p1y]
    A = np.array([t1, -t2]).T
    b = p2 - p1
    result = safe(lambda: np.linalg.solve(A, b))
    match result:
        case None: return None
        case _: ...
    alpha, beta = result
    if not as_segment or 0 <= alpha <= 1 and 0 <= beta <= 1:
        return p1 + alpha*t1

@R.curry
def crop(line: np.ndarray[_1, _4], box: np.ndarray[_4, _2], pad: int = 20) -> np.ndarray[_1, _4] | None:
    """Crop the `line` to be fully inside `box`. Returns `None` if the line is outside"""
    assert len(box) == 4, f"`box` must have exactly 4 points, but has {len(box)}"
    p, q = pq(line)
    p1, p2, p3, p4 = box
    lines = [
        [[*p1, *p2]], [[*p2, *p3]],
        [[*p3, *p4]], [[*p4, *p1]]
    ]
    intersects = R.map(intersect(seg2=line), lines)
    intersects = R.filter(lambda x: x is not None, intersects)
    match cs.inside(p, box, padding=pad), cs.inside(q, box, padding=pad):
        case True, True: # fully inside
            return np.int32(line)
        case False, False:
            match intersects:
                case []: # fully ouside
                    return None
                case [x1]: # tangent
                    return None
                case [x1, *xs]: # 2-4 intersections. could have double intersections on corners
                    x2 = max(xs, key=lambda x: np.linalg.norm(x1-x)) # any intersection that is far away works
                    return np.int32([[*x1, *x2]])
        case True, False: # p inside
            match intersects:
                case []:
                    return None # p on the border
                case [x, *_]:
                    return np.int32([[*p, *x]])
        case False, True:
            match intersects:
                case []:
                    return None # q on the border
                case [x, *_]:
                    return np.int32([[*q, *x]])
                
@R.curry
def crop_all(lines: list[np.ndarray[_1, _4]], box: np.ndarray[_4, _2], pad: int = 20) -> np.ndarray[N, tuple[_1, _4]]:
    """Crop the `line` to be fully inside `box`. Returns `None` if the line is outside"""
    return np.int32([cropped for line in lines if (cropped := crop(line, box, pad=pad)) is not None])