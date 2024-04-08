import cv2 as cv
import numpy as np
import haskellian as hk
from .. import templates as ts

def roi(img, x1, x2, y1, y2, pad_left = 0.1, pad_top = 0.2, pad_right = 0.1, pad_bot = 0.25):
    w = x2-x1; h = y2-y1
    l = max(int(x1-pad_left*w), 0)
    r = int(x2+pad_right*w)
    t = max(int(y1-pad_top*h), 0)
    b = int(y2+pad_bot*h)
    return img[t:b, l:r]

def rois(img: cv.Mat, cols: list[tuple[float, float, float]], rows: list[float]) -> list[cv.Mat]:
    res = []
    for x1, x2, x3 in cols:
        for y1, y2 in hk.pairwise(rows):
            res += [roi(img, x1, x2, y1, y2)]
            res += [roi(img, x2, x3, y1, y2)]
    return res
            
Vec2 = tuple[float, float]

def extract(
    img: cv.Mat, top_left: Vec2, size: Vec2, model: ts.SheetModel
) -> list[cv.Mat]:
    """Extract boxes from given relative `top_left` and `size` (`[1, 1]` corresponds to the size of `img`)"""
    h, w = img.shape[:2]
    cols = model.cols.imp_points
    rescaled_cols = (cols - cols[0]) / (cols[-1]-cols[0]) * w*size[0] + w*top_left[0]
    block_cols = [rescaled_cols[b:b+3] for b in model.block_cols]
    rows = model.rows.imp_points
    rescaled_rows = (rows - rows[0]) / (rows[-1]-rows[0]) * h*size[1] + h*top_left[1]
    return rois(img, block_cols, rescaled_rows)
    