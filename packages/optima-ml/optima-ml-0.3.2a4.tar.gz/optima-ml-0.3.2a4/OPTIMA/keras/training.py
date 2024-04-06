# -*- coding: utf-8 -*-
"""Collection of classes and functions specific to the training of Keras models."""
from typing import Optional

import os
import logging

import numpy as np

from tensorflow.keras.callbacks import Callback

import OPTIMA.core.training


class EarlyStopperForKerasTuning(OPTIMA.core.training.EarlyStopperForTuning, Callback):
    """_summary_.

    Returns
    -------
    _type_
        _description_
    """

    def __init__(self, *args, **kwargs):
        """_summary_.

        Parameters
        ----------
        *args : _type_
            _description_
        **kwargs : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        OPTIMA.core.training.EarlyStopperForTuning.__init__(self, *args, **kwargs)
        Callback.__init__(self)

    def on_epoch_end(self, epoch, logs=None):
        """_summary_.

        Parameters
        ----------
        epoch : _type_
            _description_
        logs : _type_
            _description_ (Default value = None)

        Returns
        -------
        _type_
            _description_
        """
        super().at_epoch_end(epoch, logs)

    def on_train_end(self, logs: Optional[dict] = None) -> None:
        """_summary_.

        Parameters
        ----------
        logs : Optional[dict]
            _description_ (Default value = None)

        Returns
        -------
        None
            _description_
        """
        super().finalize()

    def get_train_val_metric_names(self, metric: str, **kwargs: dict) -> tuple[str, str]:
        """_summary_.

        Parameters
        ----------
        metric : str
            _description_
        **kwargs : dict
            _description_

        Returns
        -------
        tuple[str, str]
            _description_
        """
        return metric, f"val_{metric}"

    def get_weights(self) -> list[np.ndarray]:
        """_summary_.

        Returns
        -------
        list[np.ndarray]
            _description_
        """
        return self.model.get_weights()

    def set_weights(self, weights: list[np.ndarray]):
        """_summary_.

        Parameters
        ----------
        weights : list[np.ndarray]
            _description_

        Returns
        -------
        _type_
            _description_
        """
        self.model.set_weights(weights)

    def save_model(self, output_dir: str, model_name: str):
        """Save the current model state into the provided directory.

        Parameters
        ----------
        output_dir : str
            _description_
        model_name : str
            _description_
        """
        try:
            self.model.save(os.path.join(output_dir, f"{model_name}.keras"), save_format="keras")
        except BlockingIOError:
            logging.warning(
                "BlockingIOError: [Errno 11] Unable to create file (unable to lock file, errno = 11, error message "
                "= 'Resource temporarily unavailable'). Skipping the save of this checkpoint!"
            )
        except OSError:
            logging.warning("OSError detected. Skipping the save of this checkpoint!")

    def predict(self, inputs: np.ndarray, verbose: int = 0) -> np.ndarray:
        """Calculate the model predictions for the given inputs.

        Parameters
        ----------
        inputs : np.ndarray
            _description_
        verbose : int
            _description_ (Default value = 0)

        Returns
        -------
        np.ndarray
            _description_
        """
        return self.model.predict(inputs, verbose=verbose)

    def stop_training(self) -> None:
        """Mark the training for termination due to Early Stopping."""
        self.model.stop_training = True
        self.finalize()  # need to call finalize manually, this is not done at the end of the training in this case
