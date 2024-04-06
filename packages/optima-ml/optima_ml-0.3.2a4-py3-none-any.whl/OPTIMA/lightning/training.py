# -*- coding: utf-8 -*-
"""Collection of classes and functions specific to the training of Lightning models."""
import os
import logging

import numpy as np
import torch.utils.data
from lightning.pytorch.callbacks import Callback

import OPTIMA.core.training
import OPTIMA.lightning.inputs


class EarlyStopperForLightningTuning(OPTIMA.core.training.EarlyStopperForTuning, Callback):
    """_summary_.

    Returns
    -------
    _type_
        _description_
    """

    def __init__(self, *args, run_config, model_config, inputs_train, inputs_val, **kwargs):
        """_summary_.

        Parameters
        ----------
        *args : _type_
            _description_
        run_config : _type_
            _description_
        model_config : _type_
            _description_
        inputs_train : _type_
            _description_
        inputs_val : _type_
            _description_
        **kwargs : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        # we need to convert numpy arrays to dataloaders
        inputs_train_tensor = torch.from_numpy(inputs_train.copy()).type(torch.float)
        inputs_val_tensor = torch.from_numpy(inputs_val.copy()).type(torch.float)
        dl_train = OPTIMA.lightning.inputs.get_dataloader(run_config, model_config, inputs_train_tensor)
        dl_val = OPTIMA.lightning.inputs.get_dataloader(run_config, model_config, inputs_val_tensor)

        # provide the dataloaders to the EarlyStopper
        OPTIMA.core.training.EarlyStopperForTuning.__init__(
            self, *args, inputs_train=dl_train, inputs_val=dl_val, **kwargs
        )
        Callback.__init__(self)

    def on_validation_end(self, trainer, pl_module):
        """_summary_.

        Parameters
        ----------
        trainer : _type_
            _description_
        pl_module : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        logs = {}
        for metric, value in trainer.callback_metrics.items():
            logs[metric] = value.detach().cpu().numpy()

        super().at_epoch_end(trainer.current_epoch, logs=logs, pl_module=pl_module, trainer=trainer)

    def on_train_end(self, trainer, pl_module) -> None:
        """_summary_.

        Parameters
        ----------
        trainer : _type_
            _description_
        pl_module : _type_
            _description_

        Returns
        -------
        None
            _description_
        """
        super().finalize()

    def get_train_val_metric_names(self, metric, **kwargs: dict):
        """_summary_.

        Parameters
        ----------
        metric : _type_
            _description_
        **kwargs : dict
            _description_

        Returns
        -------
        _type_
            _description_
        """
        return f"train_{metric}", f"val_{metric}"

    def get_weights(self, pl_module, **kwargs) -> list[np.ndarray]:
        """_summary_.

        Parameters
        ----------
        pl_module : _type_
            _description_
        **kwargs : _type_
            _description_

        Returns
        -------
        list[np.ndarray]
            _description_
        """
        return pl_module.state_dict()  # ist ein pytorch befehl
        # return self.trainer.model.state_dict()

    def set_weights(self, weights: list[np.ndarray], pl_module, **kwargs):
        """_summary_.

        Parameters
        ----------
        weights : list[np.ndarray]
            _description_
        pl_module : _type_
            _description_
        **kwargs : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        pl_module.load_state_dict(weights)

    def save_model(self, output_dir: str, model_name: str, trainer, **kwargs):
        """_summary_.

        Parameters
        ----------
        output_dir : str
            _description_
        model_name : str
            _description_
        trainer : _type_
            _description_
        **kwargs : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        try:
            trainer.save_checkpoint(filepath=os.path.join(output_dir, f"{model_name}.ckpt"))
        except BlockingIOError:
            logging.warning(
                "BlockingIOError: [Errno 11] Unable to create file (unable to lock file, errno = 11, error message "
                "= 'Resource temporarily unavailable'). Skipping the save of this checkpoint!"
            )
        except OSError:
            logging.warning("OSError detected. Skipping the save of this checkpoint!")

    def predict(
        self, inputs: torch.utils.data.DataLoader, trainer, pl_module, verbose: int = 0, **kwargs
    ) -> np.ndarray:
        """_summary_.

        Parameters
        ----------
        inputs : torch.utils.data.DataLoader
            _description_
        trainer : _type_
            _description_
        pl_module : _type_
            _description_
        verbose : int
            _description_ (Default value = 0)
        **kwargs : _type_
            _description_

        Returns
        -------
        np.ndarray
            _description_
        """
        # cannot call the trainer's predict() method here, i.e. cannot do "pred_list = trainer.predict(pl_module, inputs)"
        # as this causes a weird error with the dataloader:
        # "lightning.fabric.utilities.exceptions.MisconfigurationException: `train_dataloader` must be implemented to be
        # used with the Lightning Trainer"???
        # Instead, make predictions manually --> need to move the inputs to the correct device!
        pred_list = []
        for x in inputs:
            pred_list.append(pl_module.predict_step(x.to(pl_module.device)))
        return np.concatenate([t.detach().cpu().numpy() for t in pred_list], axis=0)

    def stop_training(self, trainer, **kwargs) -> None:
        """Mark the training for termination due to Early Stopping.

        Parameters
        ----------
        trainer : _type_
            _description_
        **kwargs : _type_
            _description_
        """
        trainer.should_stop = True
