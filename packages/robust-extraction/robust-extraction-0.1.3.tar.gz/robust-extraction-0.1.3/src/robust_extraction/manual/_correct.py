import cv2 as cv
import numpy as np
from .. import perspective as pve

Pads = pve.Pads
Corners = pve.Corners
def correct(img: cv.Mat, corners: Corners, pads: Pads = (.02, .02, .02, .02)):
    """Correct image perspective
    - `corners`: relative corners (i.e. [1, 1] is the image's bottom right)
    """
    h, w = img.shape[:2]
    rescaled_corners = np.float32(corners)*[w, h]
    return pve.correct(img, rescaled_corners, pads)