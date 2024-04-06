# -*- coding: utf-8 -*-
"""A module that provides abstract functionality to interact with models from different libraries."""
from types import ModuleType
from typing import Any, Optional, Union

import numpy as np

import importlib.util

if importlib.util.find_spec("tensorflow") is not None:
    import tensorflow as tf

if importlib.util.find_spec("lightning") is not None:
    import torch
    import lightning
    import OPTIMA.lightning.inputs

model_config_type = dict[str, Union[int, float, str, Any]]


class AbstractModel:
    """Simple wrapper to provide generic model functionality for different machine learning libraries.

    Supported are Keras and Lightning models.
    """

    def __init__(
        self, run_config: ModuleType, model: Any, pl_trainer: Optional["lightning.Trainer"] = None  # noqa: F821
    ) -> None:
        """Constructor of AbstractModel.

        Parameters
        ----------
        run_config : ModuleType
            Reference to the imported `run-config`-file.
        model : Any
            The model that should be wrapped.
        pl_trainer : Optional["lightning.Trainer"]
            When using Lightning, a Trainer is necessary to do the inference. (Default value = None)
        """
        self.run_config = run_config
        self.model = model

        if run_config.model_type == "Lightning":
            self.pl_trainer = pl_trainer

    def predict(self, inputs: np.ndarray, verbose: int = 0) -> np.ndarray:
        """Calculates the model prediction for the provided inputs array.

        Parameters
        ----------
        inputs : np.ndarray
            Numpy array containing the input features.
        verbose : int
            Parameter to control the verbosity of the prediction. This is currently only used for Keras. (Default value = 0)

        Returns
        -------
        np.ndarray
            The numpy array of model predictions.
        """
        if self.run_config.model_type == "Keras":
            return self.model.predict(inputs, verbose=verbose)
        elif self.run_config.model_type == "Lightning":
            # make a copy of the array to ensure it is writable (pytorch currently only supports converting from writable
            # numpy arrays) and wrap the input in a dataloader
            inputs = inputs.copy()
            inputs_tensor = torch.from_numpy(inputs).type(torch.float)
            dataloader = OPTIMA.lightning.inputs.get_dataloader(
                self.run_config, self.model.hparams.model_config, inputs_tensor
            )

            # do the prediction. This returns a list of tensors that need to be converted to a numpy array.
            prediction_list = self.pl_trainer.predict(self.model, dataloader)
            prediction_array_list = [t.cpu().detach().numpy() for t in prediction_list]
            prediction_array = np.concatenate(prediction_array_list, axis=0)
            return prediction_array

    def loss(
        self,
        y_true: np.ndarray,
        inputs: Optional[np.ndarray] = None,
        sample_weight: Optional[np.ndarray] = None,
        y_pred: Optional[np.ndarray] = None,
    ) -> float:
        """Calculates the loss for the provided arrays of targets and predictions using the loss function attached to the model.

        Which of the input parameters are necessary depends on the machine learning framework used:

        - Keras: The loss function is directly called using the targets and predictions, thus ``y_true`` and ``y_pred``
          are necessary, ``sample_weight`` is optionally used.
        - Lightning: No direct access to the loss function is possible, instead the ``Trainer`` is used to perform the
          evaluation. For this, the ``inputs`` and ``y_true`` are necessary, ``sample_weight`` is optionally used.

        Parameters
        ----------
        y_true : np.ndarray
            Numpy array of target values.
        inputs : Optional[np.ndarray]
            Numpy array of input features. (Default value = None)
        sample_weight : Optional[np.ndarray]
            Numpy array of sample weights. (Default value = None)
        y_pred : Optional[np.ndarray]
            Numpy array of model predictions. (Default value = None)

        Returns
        -------
        float
            The loss value.
        """
        if self.run_config.model_type == "Keras":
            if y_true is None or y_pred is None:
                raise ValueError(
                    "The target labels `y_true` and corresponding model predictions `y_pred` need to be provided."
                )

            return self.model.loss(
                tf.constant(y_true, dtype=tf.float32),
                tf.constant(y_pred, dtype=tf.float32),
                sample_weight=tf.constant(sample_weight, dtype=tf.float32) if sample_weight is not None else None,
            ).numpy()
        elif self.run_config.model_type == "Lightning":
            if y_true is None or inputs is None:
                raise ValueError("The input features `inputs` and target labels `y_true` need to be provided.")

            # wrap the numpy arrays in a dataloader
            if sample_weight is None:
                dataset = OPTIMA.lightning.inputs.get_dataset(
                    self.run_config, self.model.hparams.model_config, inputs, y_true
                )
            else:
                dataset = OPTIMA.lightning.inputs.get_dataset(
                    self.run_config, self.model.hparams.model_config, inputs, y_true, sample_weight
                )
            dataloader = OPTIMA.lightning.inputs.get_dataloader(
                self.run_config, self.model.hparams.model_config, dataset
            )

            # do the evaluation; this returns a list of dictionaries, one per dataloader used, i.e. one in this case.
            loss = self.pl_trainer.validate(self.model, dataloader, verbose=False)[0].get("val_loss")

            # check if the validation loss was logged
            if loss is None:
                raise RuntimeError(
                    "To calculate the loss, the validation loss needs to log the loss value with key 'val_loss'!"
                )

            return loss


def load_model(run_config: ModuleType, path: str, cpus: int) -> AbstractModel:
    """Helper function that abstracts the model loading for different machine learning libraries.

    In addition to loading the model, the environment will also be configured to use the correct number of cpus and set
    automatic VRAM scaling by calling the ``configure_environment``-function.

    Parameters
    ----------
    run_config : ModuleType
        Reference to the imported `run-config`-file.
    path : str
        Path to the model to load. The following file extensions are assumed:
        - ``'.keras'``: Keras model
        - ``'.ckpt'``: Torch / Lightning-model
        If the provided path does not contain a file extension, the correct extension will be inferred from the
        ``model_type`` setting in the `run_config` and appended to the file path.
    cpus : int
        The number of cpu cores available for this instance.

    Returns
    -------
    AbstractModel
        The reloaded model wrapped in an ``AbstractModel`` instance.
    """
    # configure the environment
    if run_config.model_type == "Keras":
        # for Keras, this means specifying some settings to Tensorflow
        configure_environment(run_config, cpus)
    if run_config.model_type == "Lightning":
        # for Lightning, this means getting a Trainer with the correct settings
        pl_trainer = configure_environment(run_config, cpus)

    if run_config.model_type == "Keras":
        if path[-6:] != ".keras":
            path += ".keras"
        return AbstractModel(run_config=run_config, model=tf.keras.models.load_model(path))
    elif run_config.model_type == "Lightning":
        if path[-5:] != ".ckpt":
            path += ".ckpt"
        return AbstractModel(
            run_config=run_config, model=run_config.LitModel.load_from_checkpoint(path), pl_trainer=pl_trainer
        )
    # elif run_config.model_type == "Torch":
    #     if path[-5:] != ".ckpt":
    #         path += ".ckpt"
    #     return AbstractModel(run_config=run_config, model=torch.load(path))


def configure_environment(run_config: ModuleType, cpus: int) -> None:
    """Helper function that abstracts away the configuration of the machine learning library.

    It sets the number of CPU cores to use to the provided ``cpus`` value, and enables automatic VRAM scaling for `Keras`.

    Parameters
    ----------
    run_config : ModuleType
        Reference to the imported `run-config`-file.
    cpus : int
        The number of cpu cores available for this instance.
    """
    if run_config.model_type == "Keras":
        from tensorflow import config as tf_config

        try:
            # set automatic scaling of the VRAM allocation
            gpus = tf_config.experimental.list_physical_devices("GPU")
            for gpu in gpus:
                tf_config.experimental.set_memory_growth(gpu, True)

            # reduce number of threads
            tf_config.threading.set_inter_op_parallelism_threads(min(cpus, 2))
            tf_config.threading.set_intra_op_parallelism_threads(cpus)
        except RuntimeError:
            pass
    elif run_config.model_type == "Lightning":
        # set correct number of cpu cores; TODO: this for some reason currently only works with pytorch-gpu and is ignored by pytorch??
        from torch import get_num_threads, get_num_interop_threads, set_num_threads, set_num_interop_threads

        if get_num_threads() != cpus:
            set_num_threads(cpus)
        if get_num_interop_threads() != min(cpus, 2):
            set_num_interop_threads(min(cpus, 2))
        pl_trainer = lightning.Trainer(
            devices="auto",
            accelerator="auto",
            enable_progress_bar=False,
            logger=False,  # we don't need logging here
            enable_checkpointing=False,  # also disable checkpointing
        )
        return pl_trainer
