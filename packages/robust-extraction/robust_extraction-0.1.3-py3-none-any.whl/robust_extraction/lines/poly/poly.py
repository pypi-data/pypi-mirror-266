from typing import Literal
import numpy as np
import ramda as R
import haskellian.iterables as hk
from .. import intersect, xintersect, yintersect

_1 = int; _2 = int; _4 = int; N = int; M = int
def join(points: np.ndarray[N, tuple[_1, _2]]) -> np.ndarray[M, tuple[_1, _4]]:
    """Joins `n` points into `m = n-1` lines"""
    poly = []
    for p, q in hk.pairwise(points):
        poly += [[[*p, *q]]]
    return np.int32(poly)

@R.curry
def fit(lines: list[np.ndarray[_1, _4]], axis: Literal[0, 1]) -> list[np.ndarray[_1, _2]]:
    """Fit points to `lines`, assuming `lines` are roughly collinear along `axis`.
    If `axis == 0`:
    1. Take `x` values only, sorted
    2. For every `x`, intersect all lines with vline at `x`
    3. Compute means of intersected `y` values
    """
    xs = np.int32(lines)[:, 0, [axis, axis+2]].flatten() # line = [[x1, y1, x2, y2]]
    ymax = np.max(lines[:, 0, [1-axis, 3-axis]])
    points = []
    for x in sorted(xs):
        ys = []
        for l in lines:
            p = [x, 0] if axis == 0 else [0, x]
            q = [x, ymax] if axis == 0 else [ymax, x]
            if (v := intersect(l, [[*p, *q]])) is not None:
                ys += [v[1-axis]]
        if len(ys) > 0:
            y = np.mean(ys)
            points += [[x, y] if axis == 0 else [y, x]]
    return np.int32(points)

@R.curry
def hfit(hlines: list[np.ndarray[_1, _4]], xmin: int, xmax: int) -> list[np.ndarray[_1, _4]]:
    hpoints = fit(hlines, axis=0)
    # OLD METHOD: continuing extreme lines. This is quite noisy
    # [l1, *_, l2] = hlines
    # p0 = [xmin, xintersect(l1, xmin)]
    # p3 = [xmax, xintersect(l2, xmax)]
    # NEW METHOD: just take the extreme y values (this assumes the image has been perspective/rotation corrected)
    p0 = [xmin, hpoints[0][1]]
    p3 = [xmax, hpoints[0][1]]
    return join([p0, *hpoints, p3])

@R.curry
def vfit(vlines: list[np.ndarray[_1, _4]], ymin: int, ymax: int) -> list[np.ndarray[_1, _4]]:
    vpoints = fit(vlines, axis=1)
    [l1, *_, l2] = vlines
    p0 = [yintersect(l1, ymin), ymin]
    p3 = [yintersect(l2, ymax), ymax]
    return join([p0, *vpoints, p3])