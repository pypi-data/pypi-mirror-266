import numpy as np
from ..templates import SheetModel, Template1d

BOX_W = 0.23 / 1.05
NUM_W = 0.065 / 1.05

LLOBREGAT23 = SheetModel(
    cols=Template1d(
        offsets=[NUM_W, BOX_W, BOX_W, NUM_W, BOX_W, BOX_W],
        a=1, b=7
    ),
    rows=Template1d(
        offsets=[0.8, 1.25, 0.8] + [1 for _ in range(31)] + [2],
        a=4, b=35
    ),
    block_cols=[0, 3]
)