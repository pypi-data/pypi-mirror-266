import numpy as np
import ramda as R
from ..templates import SheetModel, Template1d

NUM_W = 0.035
BOX_W = 0.139
SPACE_W = 0.027

FCDE = SheetModel(
    cols=Template1d(
        offsets=[NUM_W, BOX_W, BOX_W, SPACE_W, NUM_W, BOX_W, BOX_W, SPACE_W, NUM_W, BOX_W, BOX_W],
        a=1, b=12
    ),
    rows=Template1d(
        offsets=[1] + R.repeat(1, 25) + [1.8, 0.8],
        a=1, b=27
    ),
    block_cols=[0, 4, 8]
)
