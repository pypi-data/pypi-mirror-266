from typing import TypedDict
import cv2 as cv
import numpy as np
import ramda as R
import pure_cv as vc
from haskellian.core import pipe

_1 = int; _2 = int; _4 = int
Vec2 = np.ndarray[_2, float]

def find(img: cv.Mat) -> list[list[np.ndarray[_1, _2]]]:
    """Find all contours in `img`. Process:
    1. Gray scale
    2. Gaussian blur
    3. Threshold
    4. Find Contours
    """
    gray = vc.grayscale(img)
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    bin_img = vc.threshold(blurred)
    contours, _ = cv.findContours(bin_img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    return contours

@R.curry
def filter(contours: list[list[np.ndarray[_1, _2]]], min_area: float, max_area: float):
    """Filters contours by `min_area` and `max_area`. If none pass, they're filtered only by `min_area`"""
    big_cnts = R.filter(lambda c: cv.contourArea(c) >= min_area, contours)
    medium_cnts = R.filter(lambda c: cv.contourArea(c) <= max_area, big_cnts)
    return medium_cnts if len(medium_cnts) > 0 else big_cnts

RotatedRect = tuple[tuple[float, float], tuple[float, float], float] # (x, y), (w, h)
def vertical_rect(rect: RotatedRect) -> RotatedRect:
    """
    - `rect = (x, y), (w, h), degrees`
    - Rotates `w` and `h` such that `|degrees| <= 45`
    """
    (x, y), (w, h), degrees = rect
    if degrees < -45:
        return (x, y), (h, w), degrees+90
    elif degrees > 45:
        return (x, y), (h, w), degrees-90
    else:
        return rect
    
def aggregate(contours: list[list[np.ndarray[_1, _2]]]) -> RotatedRect:
    """Contour around all `contours` into a rotated rect"""
    return pipe(
        np.concatenate(contours),
        cv.minAreaRect,
        vertical_rect
    )
    
def grid(img: cv.Mat, min_area_p: float = 0.1, max_area_p: float = 0.6) -> RotatedRect | None:
    """Attempts to find the grid zone contour, discarding the whole-sheet contour.
    - May fail if no suitable contours are found"""
    h, w = img.shape[:2]
    all_cnts = find(img)
    match filter(all_cnts, min_area=min_area_p*w*h, max_area=max_area_p*w*h):
        case []:
            return None
        case cnts:
            return aggregate(cnts)
    
class Params(TypedDict):
    pad_h_prop: float
    pad_v_prop: float
    max_area_p: float
    min_area_p: float
    
default = Params(max_area_p=0.5, min_area_p=0.1)
        
def padded_grid(img: cv.Mat, params: Params) -> np.ndarray[_4, _2]:
    """Attempts to find the grid zone contour, discarding the whole-sheet contour.
    - Defaults to a full image contour on failure
    - `pad_h, pad_v`: relative horizontal and vertical padding (added on both sides)
    """
    params = default | params
    height, width = img.shape[:2]
    match grid(img, max_area_p=params['max_area_p'], min_area_p=params['min_area_p']):
        case (x, y), (w, h), angle:
            xpad = params['pad_h_prop']*w
            ypad = params['pad_v_prop']*h
            return cv.boxPoints(((x+xpad,y+ypad), (w+2*xpad, h+2*ypad), angle))
        case _:
            return np.int32([[0, 0], [width-1, 0], [width-1, height-1], [0, height-1]])
    

@R.curry
def inside(p: Vec2, contour: list[np.ndarray[_1, _2]], padding: float = 20) -> bool:
    """Is `p` inside `contour`? (with `padding` tolerance)"""
    return cv.pointPolygonTest(contour, np.float32(p), True) >= -padding
    