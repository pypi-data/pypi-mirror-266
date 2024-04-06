# -*- coding: utf-8 -*-
"""A module that provides functions to prepare and update the built-in Keras multilayer perceptron."""
# This way of providing the model specific functionality allows supporting different machine learning
# libraries besides Keras
import importlib.util

if importlib.util.find_spec("tensorflow") is not None:
    from OPTIMA.keras.model import build_model, compile_model, update_model  # noqa: F401
