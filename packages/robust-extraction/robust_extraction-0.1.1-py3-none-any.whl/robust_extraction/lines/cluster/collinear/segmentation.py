from typing import Literal
import numpy as np
from ... import midpoint
import ramda as R

_1 = int; _2 = int; _4 = int
Vec2 = np.ndarray[_2, float]

def overlapping_windows(d: int, n: int) -> list[Vec2]:
    """Ranges `[[0, d], [0.5*d, 1.5*d], [d, 2*d], [1.5*d, 2.5*d], ..., [(n-2)*d, (n-1)]]`
    - `n`: num of non-overlapped windows (total is `2*n - 1`)
    """
    windows = [np.array([0, d])]
    for i in range(1, n):
        w = np.int32([i*d, (i+1)*d])
        w2 = w - d/2
        windows += [w2, w]
    return windows

def classify(xs: list[float], windows: list[Vec2]) -> list[list[int]]:
    """Returns `buckets`. For every `i` in `buckets[j]`, `xs[i]` belongs to `windows[j]`"""
    buckets = [np.where((xs >= window[0]) & (xs <= window[1]))[0] for window in windows]
    return R.filter(lambda b: len(b) > 0, buckets)

def segment(lines: list[np.ndarray[_1, _4]], size: float, inclination: Literal["vertical", "horizontal"], window_size: int) -> list[list[int]]:
    """Segment lines by windows of `window_size` height/width. Each segment is a set of line indices"""
    axis = 0 if inclination == "vertical" else 1 # vertical lines are clustered by x; horizontal by y
    n_windows = int(np.ceil(size/window_size))
    xs = np.int32(R.map(R.pipe(midpoint, R.nth(axis)), lines))
    windows = overlapping_windows(window_size, n_windows)
    return classify(xs, windows)