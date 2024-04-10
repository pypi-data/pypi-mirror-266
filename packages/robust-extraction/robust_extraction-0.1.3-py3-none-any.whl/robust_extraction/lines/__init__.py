""" ### Line segment tools
Segments/lines are represented in `1 x 4` matrices, as follows:
- `line = [[x1, y1, x2, y2]]`, where
- `p = [x1, y1]` and `q = [x2, y2]` are the segment's endpoint
#### Submodules
- `cluster`: clustering by horizontal/vertical, midpoint, and collinearity
- `poly`: fitting and manipulating polylines
- `coverage`: computing and filtering clusterings by coverage
"""
from .points import pq, midpoint, pq_sort, project, cluster_midpoint, cluster_midpoints
from .directions import angle, angle2, direction, flip
from .instersections import intersect, xintersect, yintersect, crop, crop_all
from . import cluster, draw, coverage, poly
# from .joining import contained, remove_contained, join
from .extract import find, find_inside