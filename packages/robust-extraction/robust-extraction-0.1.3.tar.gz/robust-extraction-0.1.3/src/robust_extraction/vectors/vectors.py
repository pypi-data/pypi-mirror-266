import numpy as np
import ramda as R

_2 = int
Vec2 = np.ndarray[_2, float]

def normalize(v: Vec2) -> Vec2:
    return v / np.linalg.norm(v)

@R.curry
def dist(u: Vec2, v: Vec2) -> float:
    return np.linalg.norm(u-v)
