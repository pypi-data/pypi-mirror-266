from typing import Literal
import numpy as np
from scipy import stats
import networkx as nx
import ramda as R
from .segmentation import segment
from .metrics import all_pairs, max_proj_dist

N = int; _1 = int; _4 = int
    # return list(nx.connected_components(G))
    
def fixed_cluster(
    lines: np.ndarray[N, tuple[_1, _4]],
    M: np.ndarray[N, N], threshold: float,
):
    """Graph-based cluster with fixed `threshold`
    - `M`: matrix of max projection distances - `M[i][j] == max_proj_dist(lines[i], lines[j])`
    - `threshold`: max projection distance for two segments to be considered collinear"""
    E = R.transpose(np.where(M < threshold))
    G = nx.Graph(E)
    ccs = list(nx.connected_components(G))
    return [
        lines[list(cc)]
        for cc in ccs
    ]
    
    
def segmented_metrics(
    lines: np.ndarray[N, tuple[_1, _4]],
    size: float, window_size: float,
    inclination: Literal["vertical", "horizontal"],
) -> np.ndarray[N, N]:
    """Computes full `N x N` distance metric by splitting the lines across `direction` in overlapping windows"""
    segments = segment(lines, size=size, inclination=inclination, window_size=window_size)
    seg_lines = [lines[seg] for seg in segments]
    seg_metrics = R.map(all_pairs(f=max_proj_dist), seg_lines)
    n = len(lines)
    M = np.full((n, n), 1e12)
    for metrics, seg in zip(seg_metrics, segments):
        for i, s1 in enumerate(seg):
            for j, s2 in enumerate(seg):
                M[s1, s2] = metrics[i, j]
    return M

def cluster(
    lines: np.ndarray[N, tuple[_1, _4]], size: float, threshold: float,
    inclination: Literal["horizontal", "vertical"], window_size: float | None = None
):
    """#### Graph-based, fixed threshold line cluster
    - `size`: height or width (if rows or cols)
    - `inclination`: `horizontal/vertical ->` rows/cols
    - `window_size`: size of window whithin which lines are compared for collinearity. Defaults to `2.5*min_d`
    """
    window_size = window_size or 2.5*threshold
    M = segmented_metrics(lines, size=size, inclination=inclination, window_size=window_size)
    return fixed_cluster(lines, M, threshold=threshold)

def adaptive_cluster(
    lines: np.ndarray[N, tuple[_1, _4]],
    size: float, min_d: float, min_clusters: int,
    inclination: Literal["horizontal", "vertical"],
    window_size: float | None = None, n_iters: int = 100,
    min_p: float = 0.1, max_p: float = 1.5, verbose = False
):
    """#### Graph-based, adaptive threshold line cluster
    (as described in [Collinear Segment Clustering v4 (max projection distance + adaptive treshold)](https://www.notion.so/marcelclaramunt/Collinear-Segment-Clustering-v4-mpd-adaptive-thresh-fb301dc9411c4fafb71926c9e205f472?pvs=4))
    - `size`: height or width (if rows or cols)
    - `inclination`: `horizontal/vertical ->` rows/cols
    - `min_d`: minimum estimated spacing between rows/cols
    - `[min_p, max_p]`: range of proportions of `min_d` to use as thresholds
    - `n_iters`: number of tested thresholds (evenly spaced across `[min_p, max_p]`)
    - `window_size`: size of window whithin which lines are compared for collinearity. Defaults to `2.5*min_d`
    """
    window_size = window_size or 2.5*min_d
    M = segmented_metrics(lines, size=size, inclination=inclination, window_size=window_size)
    cluster_nums = []
    cluster_lens = []
    d = (max_p - min_p) / n_iters
    ps = [d*(i+1) + min_p for i in range(n_iters)]
    for p in ps:
        clusters = fixed_cluster(lines, M, threshold=min_d*p)
        n = len(clusters)
        ns = R.map(len, clusters)
        cluster_nums += [n]
        cluster_lens += [ns]

    feasible = R.filter(lambda n: n >= min_clusters, cluster_nums)
    if feasible == []:
        i = np.argmax(cluster_nums)
    else:
        mode = stats.mode(feasible).mode
        if verbose: print(f"Mode = {mode}")
        i = R.find_last_index(lambda n: n >= mode, cluster_nums) - 1 # ramda's implementation is off by one
    return fixed_cluster(lines, M, threshold=min_d*ps[i])