import numpy as np
import cv2 as cv
import pure_cv as vc
from . import crop_all

_1 = int; _2 = int; _4 = int

def find(
    img: cv.Mat, thresholded: bool = False,
    rho: float = 1,
    theta: float = np.pi / 180,
    threshold: int = 100,
    min_length: float = 200,
    max_gap: float = 5
) -> list[np.ndarray[_1, _4]]:
    bin_img = img if thresholded else vc.threshold(img)
    return cv.HoughLinesP(
        bin_img, rho=rho, theta=theta, threshold=threshold,
        minLineLength=min_length, maxLineGap=max_gap
    )
    
def find_inside(
    img: cv.Mat, box: np.ndarray[_4, _2],
    pad: int = 20,
    thresholded: bool = False,
    rho: float = 1,
    theta: float = np.pi / 180,
    threshold: int = 100,
    min_length: float = 200,
    max_gap: float = 10
) -> list[np.ndarray[_1, _4]]:
    lines = find(img, thresholded, rho, theta, threshold, min_length, max_gap)
    return crop_all(lines, box, pad)