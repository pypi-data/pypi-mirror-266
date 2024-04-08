from dataclasses import dataclass
from typing import Iterable, Callable
from functools import cached_property
import numpy as np
import ramda as R
from pydantic import BaseModel

@dataclass
class Template1d:
    """Rows/cols template as described in [Row/Column Clustering v5](https://www.notion.so/marcelclaramunt/Row-Column-Clustering-Scoresheet-Templates-v5-single-template-LAP-d65b5eac34fe46eab6f4d92e09dc27a3?pvs=4)
    - `a`: start of important rows/cols
    - `b`: end of important rows/cols
    - `offsets`: normalized on creation (s.t. they add up to 1)
    """
    offsets: list[float]
    a: int
    b: int
    
    def __init__(self, offsets: list[float], a: float, b: float):
        self.offsets = list(np.float32(offsets) / np.sum(offsets))
        self.a = a; self.b = b
    
    @cached_property
    def points(self) -> list[float]:
        return list(np.cumsum([0] + self.offsets))
    
    @cached_property
    def imp_points(self) -> list[float]:
        return self.points[self.a:self.b]
        
    
    @cached_property
    def min(self) -> float:
        return min(self.offsets)
    

class SheetModel(BaseModel):
    """Scoresheet model w/contiguous boxes as described in [Row/Column Clustering v5](https://www.notion.so/marcelclaramunt/Row-Column-Clustering-Scoresheet-Templates-v5-single-template-LAP-d65b5eac34fe46eab6f4d92e09dc27a3?pvs=4)"""
    cols: Template1d
    rows: Template1d
    block_cols: list[int]
    
    @cached_property
    def cmin(self) -> float:
        return self.cols.min
    
    @cached_property
    def rmin(self) -> float:
        return self.rows.min
    
    @property
    def nboxes(self) -> int:
        # Each important row (except the last) corresponds to a row of boxes
        # Each block col corresponds to 2 cols of boxes
        return (len(self.rows.imp_points)-1) * 2*len(self.block_cols)
    
def contiguous_boxes(
    rows: list[int],
    block_cols: list[int]
) -> Iterable[tuple[int, int]]:
    """`(row, col)` indices of box top left corners"""
    for c in block_cols:
        for r in rows:
            yield (r, c)
            yield (r, c+1)
            
_1 = int; _2 = int; _4 = int; Vec2 = np.ndarray[_2, float]

@R.curry
def contour(
	row: int, col: int,
	intersect: Callable[[tuple[int, int]], Vec2]
) -> np.ndarray[_4, tuple[_1, _2]] | None:
	tl = intersect((row, col))
	tr = intersect((row, col+1))
	bl = intersect((row+1, col))
	br = intersect((row+1, col+1))
	xs = [tl, tr, br, bl]
	if any(x is None for x in xs):
		return None
	else:
		return np.int32(xs).reshape(4, 1, 2)

def contours(
    model: SheetModel,
    intersect: Callable[[tuple[int, int]], Vec2]
) -> list[np.ndarray[_4, tuple[_1, _2]] | None]:
    imp_rows = list(range(model.rows.b - model.rows.a))
    return np.array([contour(i, j, intersect) for i, j in contiguous_boxes(imp_rows[:-1], model.block_cols)])
