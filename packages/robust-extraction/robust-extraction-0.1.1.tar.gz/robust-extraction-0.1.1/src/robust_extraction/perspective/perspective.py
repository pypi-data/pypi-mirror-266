from typing import NamedTuple, TypedDict
import numpy as np
import cv2 as cv
import pure_cv as vc
import ramda as R
from .. import lines as ls, templates as ts, match1d, contours as cs

_1 = int; _2 = int; _4 = int
def acceptable(
    left: np.ndarray[_1, _4],
    right: np.ndarray[_1, _4],
    acceptable_degrees: float = 2
) -> bool:
    l_angle = np.mean(R.map(ls.angle, left))
    r_angle = np.mean(R.map(ls.angle, right))
    ldiff = abs(abs(np.rad2deg(l_angle)) - 90) # angle from vertical
    rdiff = abs(abs(np.rad2deg(r_angle)) - 90) # angle from vertical
    return ldiff < acceptable_degrees and rdiff < acceptable_degrees

def correct_old(
    img: cv.Mat,
    left: np.ndarray[_1, _4],
    right: np.ndarray[_1, _4],
    top: np.ndarray[_1, _4],
    bottom: np.ndarray[_1, _4],
    pad_lrtb: tuple[float, float, float, float] = (50, 50, 50, 50),
    return_all: bool = False
) -> cv.Mat:
    pad_left, pad_right, pad_top, pad_bot = pad_lrtb
    tl = ls.poly.mean_intersect(top, left, as_segment=False)
    tr = ls.poly.mean_intersect(top, right, as_segment=False)
    br = ls.poly.mean_intersect(bottom, right, as_segment=False)
    bl = ls.poly.mean_intersect(bottom, left, as_segment=False)
    w = int(max(abs(tl[0]-tr[0]), abs(bl[0]-br[0]))) + pad_left + pad_right
    h = int(max(abs(tl[1]-bl[1]), abs(tr[1]-br[1]))) + pad_top + pad_bot
    src = np.int32([tl, tr, br, bl])
    dst = np.int32([[pad_left, pad_top], [w-pad_right, pad_top], [w-pad_right, h-pad_bot], [pad_left, h-pad_bot]])
    M, _ = cv.findHomography(src, dst)
    corr = cv.warpPerspective(img, M, (w, h))
    if not return_all:
        return corr
    else:
        return corr, dict(M=M, w=w, h=h)
    

def autocorrect(
    img: cv.Mat, model: ts.SheetModel,
    min_height_p = 0.5, min_width_p = 0.5,
    pads_lrtb: tuple[int, int, int, int] = (50, 50, 50, 50),
    filter_col_coverage = True, filter_row_coverage = True,
    return_all = False, verbose = False
) -> cv.Mat | None:
    """Autocorrect perspective via detected horizontal and vertical lines.
    - Uses adaptive row clustering
    - `min_{height|width}_p`: min estimated proportion of scoresheet size (w.r.t. the full image)
    - May fail (and return `None` is not enough lines are detected)"""
    height, width = img.shape[:2]
    MIN_ROW_H = min_height_p*height*model.rmin
    MIN_COL_W = min_width_p*width*model.cmin
    cnt = cs.padded_grid(img, cs.Params(pad_v_prop=model.rmin, pad_h_prop=model.cmin))
    all_lines = ls.find(img)
    lines = np.int32([
        cropped for line in all_lines
            if (cropped := ls.crop(line, box=cnt)) is not None
    ])
    vlines, hlines = ls.cluster.vh(lines)
    imp_rows = model.rows.b - model.rows.a
    row_lines = ls.cluster.collinear.adaptive_cluster(
        lines=hlines, min_d=MIN_ROW_H, min_clusters=imp_rows,
        size=height, inclination="horizontal", n_iters=100, verbose=verbose
    )
    rows = ls.coverage.filter(row_lines, axis=0, k=2) if filter_row_coverage else row_lines
    col_lines = ls.cluster.collinear.cluster(
        lines=vlines, threshold=MIN_COL_W,
        size=width, inclination="vertical"
    )
    cols = ls.coverage.filter(col_lines, axis=1)  if filter_col_coverage else col_lines
    matched_cols = match1d.invariant(clusters=cols, template=model.cols, inclination='cols')
    res = correct_old(
        img, left=cols[0], right=cols[-1],
        top=rows[0], bottom=rows[-1],
        pad_lrtb=np.int32(pads_lrtb),
        return_all=return_all
    )
    if not return_all:
        return res
    else:
        corr, d = res
        return corr, dict(
            rows=rows, cols=matched_cols,
            vlines=vlines, hlines=hlines,
            matched_rows=row_lines, matched_cols=col_lines,
            **d
        )
    