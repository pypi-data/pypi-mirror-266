# -*- coding: utf-8 -*-
"""Collection of classes and functions specific to the handling of the training input for Lightning models."""
import lightning as pl
import torch

from typing import Optional, Tuple, Union, Any
from types import ModuleType

import numpy as np

import OPTIMA.builtin.inputs

model_config_type = dict[str, Union[int, float, str, Any]]


class LightningDataset(torch.utils.data.Dataset):
    """Tensor dataset with in-memory batching to improve performance."""

    def __init__(
        self, inputs: torch.Tensor, targets: torch.Tensor, weights: Optional[torch.Tensor] = None, batch_size: int = 1
    ) -> None:
        """Constructor of ``LightningDataset``.

        Parameters
        ----------
        inputs : torch.Tensor
            Torch tensor of input features.
        targets : torch.Tensor
            Torch tensor of target labels.
        weights : Optional[torch.Tensor]
            Torch tensor of event weights. (Default value = None)
        batch_size : int
            The batch size of the dataset. (Default value = 1)
        """
        self.inputs = inputs
        self.targets = targets
        self.weights = weights

        self.len = len(inputs) // batch_size
        self.batch_size = batch_size

    def __len__(self):
        """_summary_.

        Returns
        -------
        _type_
            _description_
        """
        return self.len

    def __getitem__(
        self, idx: int
    ) -> Union[Tuple[torch.Tensor, torch.Tensor, torch.Tensor], Tuple[torch.Tensor, torch.Tensor]]:
        """_summary_.

        Parameters
        ----------
        idx : int
            _description_

        Returns
        -------
        Union[Tuple[torch.Tensor, torch.Tensor, torch.Tensor], Tuple[torch.Tensor, torch.Tensor]]
            _description_
        """
        start = self.batch_size * idx
        end = self.batch_size * (idx + 1)

        if self.weights is not None:
            return self.inputs[start:end], self.targets[start:end], self.weights[start:end]
        else:
            return self.inputs[start:end], self.targets[start:end]


def get_dataset(
    run_config: ModuleType, model_config: Optional[model_config_type] = None, *numpy_arrays: np.ndarray
) -> torch.utils.data.Dataset:
    """Helper function to build a Lightning dataset from numpy arrays provided as positional arguments.

    From the provided numpy arrays, Torch tensors are built.

    If a ``LightningDataset`` class is defined in the `run-config`, its constructor is provided with the ``model_config``
    and the ``torch.Tensor`` arguments are passed as positional arguments. Otherwise, a Torch ``TensorDataset`` is built.

    Parameters
    ----------
    run_config : ModuleType
        Reference to the imported run-config file.
    model_config : Optional[model_config_type]
        The model-config of the Lightning model this dataset is to be built for. This is only provided to the
        ``LightningDataset``-class in the `run-config` (if present). (Default value = None)
    *numpy_arrays : np.ndarray
        The numpy arrays to be combined into a dataset.

    Returns
    -------
    torch.utils.data.Dataset
        The built dataset.
    """
    tensors = []
    for array in numpy_arrays:
        # make a copy of the array to ensure it is writable (pytorch currently only supports converting from writable
        # numpy arrays)
        array = array.copy()
        tensors.append(torch.from_numpy(array).type(torch.float))

    if hasattr(run_config, "LightningDataset"):
        dataset = run_config.LightningDataset(model_config, *tensors)
    else:
        dataset = torch.utils.data.TensorDataset(*tensors)
    return dataset


def get_dataloader(
    run_config: ModuleType, model_config: model_config_type, dataset: torch.utils.data.Dataset
) -> torch.utils.data.DataLoader:
    """Helper function to build a dataloader from a torch dataset.

    By default, a ``torch.utils.data.DataLoader`` is instantiated, with the ``batch_size`` set to the ``"batch_size"``
    entry in the provided ``model_config``. To overwrite this behavior, a ``Dataloader``-class can be defined in the
    `run-config`. It is provided with the ``dataset`` and the ``model_config``.

    Parameters
    ----------
    run_config : ModuleType
        Reference to the imported run-config file.
    model_config : model_config_type
        The model-config of the Lightning model this dataset is to be built for. If a ``Dataloader``-class is defined
        in the `run-config`, it is provided directly to the constructor. If this is not the case, it is expected to
        contain a ``"batch_size"``-entry that is provided to the ``torch.utils.data.DataLoader``.
    dataset : torch.utils.data.Dataset
        The dataset to be wrapped in a dataloader.

    Returns
    -------
    torch.utils.data.DataLoader
        The built dataloader.
    """
    if hasattr(run_config, "DataLoader"):
        dataloader = run_config.DataLoader(dataset, model_config)
    else:
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=model_config["batch_size"])
    return dataloader


class DefaultDataModule(pl.LightningDataModule):
    """A LightningDataModule that provides default functionality."""

    def __init__(
        self,
        inputs_train: np.ndarray,
        targets_train: np.ndarray,
        inputs_val: np.ndarray,
        targets_val: np.ndarray,
        run_config: ModuleType,
        model_config: model_config_type,
        weights_train: Optional[np.ndarray] = None,
        weights_val: Optional[np.ndarray] = None,
        inputs_test: Optional[np.ndarray] = None,
        targets_test: Optional[np.ndarray] = None,
        weights_test: Optional[np.ndarray] = None,
        input_handler: Optional[OPTIMA.builtin.inputs.InputHandler] = None,
    ):
        """Constructor of ``DefaultDataModule``.

        It represents the easiest possible implementation of a ``LightningDataModule``. The datasets are built by calling
        the ``get_dataset``-function. The dataloaders are provided by ``get_dataloader``.

        Parameters
        ----------
        inputs_train : np.ndarray
            Numpy array of training input features.
        targets_train : np.ndarray
            Numpy array of training target labels.
        inputs_val : np.ndarray
            Numpy array of validation input features.
        targets_val : np.ndarray
            Numpy array of validation target labels.
        run_config : ModuleType
            Reference to the imported run-config file.
        model_config : model_config_type
            The model-config of the Lightning model this data module is to be built for.
        weights_train : Optional[np.ndarray]
            Numpy array of training event weights. (Default value = None)
        weights_val : Optional[np.ndarray]
            Numpy array of validation event weights. (Default value = None)
        inputs_test : Optional[np.ndarray]
            Numpy array of testing input features. (Default value = None)
        targets_test : Optional[np.ndarray]
            Numpy array of testing target labels. (Default value = None)
        weights_test : Optional[np.ndarray]
            Numpy array of testing event weights. (Default value = None)
        input_handler : Optional[OPTIMA.builtin.inputs.InputHandler]
            Instance of the ``InputHandler``-class. While not needed for the built-in DataModule, a DataModule defined
            in the `run-config` may need to know the inputs they are provided with, and will, thus, be provided with the
            ``input_handler``. (Default value = None)
        """
        super().__init__()

        self.inputs_train = inputs_train
        self.targets_train = targets_train
        self.weights_train = weights_train

        self.inputs_val = inputs_val
        self.targets_val = targets_val
        self.weights_val = weights_val

        self.inputs_test = inputs_test
        self.targets_test = targets_test
        self.weights_test = weights_test

        self.run_config = run_config
        self.model_config = model_config

        self.train_dataset = None
        self.val_dataset = None
        self.test_dataset = None

    def prepare_data(self):
        """_summary_.

        Returns
        -------
        _type_
            _description_
        """
        pass

    def setup(self, stage: str = None):
        """_summary_.

        Parameters
        ----------
        stage : str
            _description_ (Default value = None)

        Returns
        -------
        _type_
            _description_
        """
        # get the datasets
        if stage == "fit" or stage is None:
            self.train_dataset = get_dataset(
                self.run_config, self.model_config, self.inputs_train, self.targets_train, self.weights_train
            )
            self.val_dataset = get_dataset(
                self.run_config, self.model_config, self.inputs_val, self.targets_val, self.weights_val
            )
        if stage == "test" or stage is None and self.inputs_test is not None and self.targets_test is not None:
            self.test_dataset = get_dataset(
                self.run_config, self.model_config, self.inputs_test, self.targets_test, self.weights_test
            )

    def train_dataloader(self):
        """_summary_.

        Returns
        -------
        _type_
            _description_
        """
        dataloader = get_dataloader(self.run_config, self.model_config, self.train_dataset)
        return dataloader

    def val_dataloader(self):
        """_summary_.

        Returns
        -------
        _type_
            _description_
        """
        dataloader = get_dataloader(self.run_config, self.model_config, self.val_dataset)
        return dataloader

    def test_dataloader(self):
        """_summary_.

        Returns
        -------
        _type_
            _description_
        """
        dataloader = get_dataloader(self.run_config, self.model_config, self.test_dataset)
        return dataloader
