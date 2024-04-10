"""
- Contours are represented as N x 1 x 2 tensors
    - i.e. `[[[x1, y1]], [[x2, y2]], [[x3, y3]], ...]`
"""
from .contours import find, filter, aggregate, grid, inside, padded_grid, Params
from .rois import roi, extract