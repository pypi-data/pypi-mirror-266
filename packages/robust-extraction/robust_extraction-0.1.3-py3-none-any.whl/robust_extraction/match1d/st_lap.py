from typing import NamedTuple, Iterable, Callable, Literal
import numpy as np
import scipy.optimize
import ramda as R
import haskellian.iterables as hk
from .. import lines as ls, templates as ts

N = int; M = int; _1 = int; _4 = int

class Alignment(NamedTuple):
    i: int; j: int; k: int; l: int
    
def alignments(a: int, b: int, n: int, m: int) -> Iterable[Alignment]:
    """All possible `X` vs. `Y` alignments s.t. `len(X) >= len(Y)`
    - `(a, b)`: range of required `Y` points to be matched (remaining are optional)
    - `n = len(X)`
    - `m = len(Y)`
    """
    for k in range(a+1): # a = 2 included
        for l in range(b, m+1):
            lmin = l - k
            for i in range(n-lmin+1):
                for j in range(i+lmin, n+1):
                    yield Alignment(i, j, k, l)
                    
class Match(NamedTuple):
    I: list[int]; J: list[int]; cost: float
    alignment: Alignment

def rescaled_matches(
    X: np.ndarray[N, float], Y: np.ndarray[M, float],
    a: int, b: int, penalization: Callable[[int], float] = R.always(1),
    cost_fn: Callable[[np.ndarray[N, M]], np.ndarray[N, M]] = None,
    norm_fn: Callable[[np.ndarray[N, M]], np.ndarray[N, M]] = None,
    verbose = False
) -> Iterable[Match]:
    assert (cost_fn is None) == (norm_fn is None), f"Either both `cost_fn` and `norm_fn` are defined, or none is"
    cost_fn = cost_fn or np.square
    norm_fn = norm_fn or np.sqrt
    for i, j, k, l in alignments(a=a, b=b, n=len(X), m=len(Y)):
        Xn = (X[i:j]-X[i]) / (X[j-1]-X[i])
        Yn = (Y[k:l]-Y[k]) / (Y[l-1]-Y[k])
        absdiff = np.abs(Xn[:, None] - Yn)
        C = cost_fn(absdiff)
        I, J = scipy.optimize.linear_sum_assignment(C)
        n_matched = min(len(I), len(J))
        p = penalization(n_matched)
        cost = norm_fn(C[I, J].sum() * p)
        if verbose: print(f"(i, j) = ({i}, {j}); (k, l) = ({k}, {l}) -> cost = {cost} [#matched = {n_matched}, pen = {p}]")
        yield Match(I=I+i, J=J+k, cost=cost, alignment=Alignment(i, j, k, l))
        
class All(NamedTuple):
    X: list[float]; Y: list[float]
    I: list[int]; J: list[int]; cost: float; alignment: Alignment

def invariant(
    clusters: list[list[np.ndarray[_1, _4]]],
    template: ts.Template1d,
    inclination: Literal['cols', 'rows'], pen_exp: float = 1/2,
    return_all = False, verbose = False
) -> list[list[np.ndarray[_1, _4]]]:
    """#### Scale- and Translation-invariant 1d match
    (as described in [Row/Column Matching v5 (single-template st-LAP)](https://www.notion.so/marcelclaramunt/Row-Column-Matching-Scoresheet-Templates-v5-single-template-LAP-d65b5eac34fe46eab6f4d92e09dc27a3?pvs=4))
    """
    axis = 0 if inclination == "cols" else 1
    a = template.a; b = template.b
    Y = template.points
    lmin = b - a
    # penalization = lambda N: 1/N
    penalization = lambda N: 1/(N-lmin+1)**pen_exp
    X = ls.cluster_midpoints(clusters, axis=axis)
    I, J, cost, alignment = min(rescaled_matches(
        X, np.float32(Y), a, b, penalization, cost_fn=np.abs, norm_fn=R.identity, verbose=verbose
    ), key=R.prop("cost"))
    k = alignment.k
    I_imp = I[a-k:][:b-a]
    matched = hk.pick(I_imp, clusters)
    if not return_all:
        return matched
    else:
        return matched, All(X=X, Y=Y, I=I, J=J, cost=cost, alignment=alignment)
    