from typing import Literal
from .. import SheetModel
from .fcde import FCDE
from .llobregat23 import LLOBREGAT23

ModelID = Literal["fcde", "llobregat23"]

models: dict[ModelID, SheetModel] = dict(
    fcde=FCDE, llobregat23=LLOBREGAT23
)