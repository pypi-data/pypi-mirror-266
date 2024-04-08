import cv2 as cv
import numpy as np
import ramda as R
from haskellian.core import pipe
import pure_cv as vc
_1 = int; _4 = int

@R.curry
def clusters(clusters: list[list[np.ndarray[_1, _4]]], img: cv.Mat, num_colors: int = 6):
    """Draw clusters with rotating colors"""
    return pipe(img, *[vc.draw.lines(l, color=vc.mod_color(i, num_colors)) for i, l in enumerate(clusters)])