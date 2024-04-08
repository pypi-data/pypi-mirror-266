"""Correcting perspective from detected lines"""
from .perspective import acceptable, autocorrect
from .perspective2 import correct, Corners, Pads, detect_corners, descaled_autocorrect, Params, default_params