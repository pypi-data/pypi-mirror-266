import numpy as np
import cv2 as cv
import ramda as R
from py_jaxtyping import PyArray
from jaxtyping import Int

Contour = PyArray[Int, int, "4 1 2"]
Contours = PyArray[Int, int, "N 4 1 2"]

_1 = int; _2 = int
@R.curry
def roi(
    contour: Contour, img: cv.Mat,
    pad_lrtb: tuple[float, float, float, float] = (0, 0, .15, .25)
) -> cv.Mat:
    """- `pad_lrtb`: proportions of height/width to add as padding"""
    l, r, t, b = pad_lrtb
    x, y, w, h = cv.boundingRect(contour)
    top = max(int(y - t*h), 0)
    bot = int(y + (1+b)*h)
    left = max(int(x - l*w), 0)
    right = int(x + (1+r)*w)
    return img[top:bot, left:right]


def extract(img: cv.Mat, contours: Contours | list[Contour]) -> list[cv.Mat]:
    return R.map(roi(img=img), contours)