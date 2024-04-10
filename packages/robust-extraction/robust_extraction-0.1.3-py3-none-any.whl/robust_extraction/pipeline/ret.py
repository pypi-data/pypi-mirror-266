from typing import Literal
from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict, SkipValidation
from haskellian.either import Either
from py_jaxtyping import PyArray
from jaxtyping import Int, UInt8

class Ok(BaseModel):
  model_config = ConfigDict(arbitrary_types_allowed=True, extra='forbid')
  contours: PyArray[Int, int, "N 4 1 2"]
  corr_img: SkipValidation[PyArray[UInt8, int, "H W _"]]
  boxes: list[SkipValidation[PyArray[UInt8, int, "H W _"]]]

@dataclass
class NotEnoughRows:
  detected: int
  required: int
  reason: Literal['not-enough-rows'] = 'not-enough-rows'

@dataclass
class NotEnoughCols:
  detected: int
  required: int
  reason: Literal['not-enough-cols'] = 'not-enough-cols'

@dataclass
class UnkownError:
  detail: str
  reason: Literal['unknown'] = 'unknown'
  
  
Error = NotEnoughRows | NotEnoughCols | UnkownError
Result = Either[Error, Ok]