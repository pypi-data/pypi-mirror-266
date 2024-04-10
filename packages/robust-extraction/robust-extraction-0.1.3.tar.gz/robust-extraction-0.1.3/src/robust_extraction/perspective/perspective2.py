from typing import NamedTuple, TypedDict
import cv2 as cv
import numpy as np
import pure_cv as vc
from .. import templates as ts, contours as cs, lines as ls, vectors as vec

Vec2 = tuple[float, float]

class Corners(NamedTuple):
    tl: Vec2
    tr: Vec2
    br: Vec2
    bl: Vec2
    
class DetectParams(TypedDict):
    min_height_p: float
    min_width_p: float
    filter_col_coverage: bool
    filter_row_coverage: bool
    min_length_height_p: float
    max_gap_height_p: float

default_det = DetectParams(
    min_height_p=0.5, min_width_p=0.5,
    filter_col_coverage=True, filter_row_coverage=True,
    verbose=False, min_length_height_p=0.05, max_gap_height_p=0.002
)

def detect_corners(
    img: cv.Mat, model: ts.SheetModel, params: DetectParams
) -> Corners | None:
    params = default_det | params
    height, width = img.shape[:2]
    MIN_ROW_H = params['min_height_p']*height*model.rmin
    MIN_COL_W = params['min_width_p']*width*model.cmin
    ps = cs.Params(pad_v_prop=model.rmin, pad_h_prop=model.cmin, **params)
    cnt = cs.padded_grid(img, ps)
    min_length = height * params['min_length_height_p']
    max_gap = height * params['max_gap_height_p']
    all_lines = ls.find(img, min_length=min_length, max_gap=max_gap)
    lines = np.int32([
        cropped for line in all_lines
            if (cropped := ls.crop(line, box=cnt)) is not None
    ])
    vlines, hlines = ls.cluster.vh(lines)
    imp_rows = model.rows.b - model.rows.a
    row_lines = ls.cluster.collinear.adaptive_cluster(
        lines=hlines, min_d=MIN_ROW_H, min_clusters=imp_rows,
        size=height, inclination="horizontal", n_iters=100
    )
    rows = ls.coverage.filter(row_lines, axis=0, k=2) if params['filter_row_coverage'] else row_lines
    col_lines = ls.cluster.collinear.cluster(
        lines=vlines, threshold=MIN_COL_W,
        size=width, inclination="vertical"
    )
    cols = ls.coverage.filter(col_lines, axis=1) if params['filter_col_coverage'] else col_lines
    # matched_cols = match1d.invariant(clusters=cols, template=model.cols, inclination='cols')
    if len(cols) < 2 or len(rows) < 2:
        return None
    left=cols[0]; right=cols[-1]
    top=rows[0]; bottom=rows[-1]
    tl = ls.poly.mean_intersect(top, left, as_segment=False)
    tr = ls.poly.mean_intersect(top, right, as_segment=False)
    br = ls.poly.mean_intersect(bottom, right, as_segment=False)
    bl = ls.poly.mean_intersect(bottom, left, as_segment=False)
    return Corners(tl=tl, tr=tr, br=br, bl=bl) 
    
class Pads(NamedTuple):
    left: float
    right: float
    top: float
    bot: float
    
def correct(
    img: cv.Mat,
    corners: Corners,
    pads: Pads = (.02, .02, .02, .02)
):
    tl, tr, br, bl = np.float32(corners)
    pl, pr, pt, pb = pads
    detected_w = int((vec.dist(tl, tr) + vec.dist(bl, br)) / 2)
    detected_h = int((vec.dist(tl, bl) + vec.dist(tr, br)) / 2)
    pad_left = int(detected_w*pl); pad_right = int(detected_w*pr)
    pad_top = int(detected_h*pt); pad_bot = int(detected_h*pb)
    w = int(detected_w + pad_left + pad_right)
    h = int(detected_h + pad_top + pad_bot)
    src = np.int32([tl, tr, br, bl])
    dst = np.int32([[pad_left, pad_top], [w-pad_right, pad_top], [w-pad_right, h-pad_bot], [pad_left, h-pad_bot]])
    M, _ = cv.findHomography(src, dst)
    return cv.warpPerspective(img, M, (w, h))  

class Params(DetectParams):
    rescale_h: int | None
    pads: Pads
    
default_params = default_det | Params(rescale_h=1920, pads=[.02, .02, .02, .02])

def descaled_autocorrect(
    img: cv.Mat, model: ts.SheetModel, params: Params = default_params, logger = None
) -> cv.Mat | None:
    params = default_params | params
    """Autocorrect perspective via detected horizontal and vertical lines.
    - Downcales the image for faster detection (but returns normal scale)
    - Uses adaptive row clustering
    - `min_{height|width}_p`: min estimated proportion of scoresheet size (w.r.t. the full image)
    - May fail (and return `None` is not enough lines are detected)"""
    rescaled = vc.descale_h(img, params['rescale_h']) if params['rescale_h'] is not None else img
    if logger is not None: logger(f'Descaled autocorrect img: {rescaled.shape[:2]}')
    s = img.shape[0] / rescaled.shape[0]
    corners = detect_corners(rescaled, model, params)
    r_corners = np.int32(s*np.array(corners))
    return correct(img, Corners(*r_corners), pads=params['pads'])