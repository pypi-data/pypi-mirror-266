from pydantic import BaseModel, ConfigDict, SkipValidation
from py_jaxtyping import PyArray
from jaxtyping import Int, UInt8

class Result(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra='forbid')
    contours: PyArray[Int, int, "N 4 1 2"]
    corr_img: SkipValidation[PyArray[UInt8, int, "H W _"]]
    boxes: list[SkipValidation[PyArray[UInt8, int, "H W _"]]]