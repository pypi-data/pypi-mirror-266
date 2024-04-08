import numpy as np
import ramda as R
from sklearn.cluster import KMeans
import haskellian.iterables as hk
from haskellian.core import pipe
from .. import angle, pq_sort

N = int; _1 = int; _4 = int

def vh(
    lines: np.ndarray[N, tuple[_1, _4]]
) -> tuple[np.ndarray[N, tuple[_1, _4]], np.ndarray[N, tuple[_1, _4]]]:
    """Returns `(vlines, hlines)`
    - Clustered by `abs(angle)`, with `angle in [-pi, pi]`
    - `vlines` sorted by `x` s.t.:
        - Each line `[[x1, y1, x2, y2]]` satisfies `x1 < x2`
        - `i <= j` iff `vlines[i][0] <= vlines[j][0]`
    - Similarly, `hlines` sorted by `y`, s.t.:
        - Each line `[[x1, y1, x2, y2]]` satisfies `y1 < y2`
        - `i <= j` iff `hlines[i][1] <= hlines[j][1]`
    """
    angles = np.array(R.map(angle, lines))
    kmeans = KMeans(n_clusters=2, max_iter=5000, n_init=100)
    labs = kmeans.fit_predict(np.abs(angles[:, None]))
    centers = [[alpha], [beta]] = kmeans.cluster_centers_
    h_lab = np.argmin([np.abs(alpha), np.abs(beta)])
    h_angle = centers[h_lab]
    v_angle = centers[1-h_lab]
    # h_angle = np.abs(np.median(angles[labs == h_lab]))
    # v_angle = np.abs(np.median(angles[labs == 1-h_lab]))
    hlines = pipe(
        lines[(labs == h_lab) & np.isclose(np.abs(angles), h_angle, atol=4*np.pi/180)],
        R.map(pq_sort(axis=0)),
        hk.sorted(key=lambda l: l[0][1]),
        np.int32
    )
    vlines = pipe(
        lines[(labs == 1-h_lab) & np.isclose(np.abs(angles), v_angle, atol=8*np.pi/180)],
        R.map(pq_sort(axis=1)),
        hk.sorted(key=lambda l: l[0][0]),
        np.int32
    )
    return vlines, hlines