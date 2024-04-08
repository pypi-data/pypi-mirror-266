from typing import Literal
import numpy as np
import ramda as R

_1 = int; _2 = int; _4 = int; N = int

# by chatGPT (I'm not responsible for uglyness)
def union(intervals: np.ndarray[N, _2]) -> float:
    if len(intervals) == 0:
        return 0
    intervals = np.array(intervals)
    intervals = intervals[np.argsort(intervals[:, 0])]
    total_length = 0
    current_end = -np.inf
    for start, end in intervals:
        if start > current_end:
            total_length += end - start
            current_end = end
        else:
            if end > current_end:
                total_length += end - current_end
                current_end = end
    return total_length

def filter(
    clusters: list[list[np.ndarray[_1, _4]]],
    axis: Literal[0, 1], k: float = 2, min_p: float = 0.7
) -> list[list[np.ndarray[_1, _4]]]:
    """Filters clusters by their coverage of `axis`. Clusters failing both tests are filtered out:
    - `coverage >= mean(coverage) - k*stddev(coverage)`, and
    - `coverage >= min_p*mean(coverage)`"""
    xs = [c[:, 0, [axis, axis+2]] for c in clusters]
    coverage = R.map(union, xs)
    m = np.mean(coverage)
    s = np.std(coverage)
    I = np.where((coverage >= m - k*s) | (coverage >= min_p*m))[0]
    return [clusters[i] for i in I]