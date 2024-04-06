# -*- coding: utf-8 -*-
"""OPTIMA is a framework for automated and distributed optimization of hyperparameters and input variables of arbitrary neural networks."""
from .optima import __version__, __author__, __licence__

name = "OPTIMA"

__all__ = ["__version__", "__author__", "__licence__"]
__pdoc__ = {
    "helpers.extract_data_from_NTuples": False,
    # "resources": False
}
