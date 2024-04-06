# -*- coding: utf-8 -*-
"""Collection of classes and functions to handle data loading and preprocessing for classification tasks."""

from types import ModuleType
from typing import Union, Optional, Callable, Any, Literal
from typing_extensions import Self

import copy
import os
import pickle
import sys

import pandas as pd
import sklearn.preprocessing
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split, KFold

import numpy as np


class InputHandler:
    """Helper class to handle the currently used input variables and corresponding non-linear scalings."""

    def __init__(self, run_config: ModuleType) -> None:
        """Constructor of ``InputHandler``.

        Grabs the available input variables and corresponding non-linear transformations from the ``run_config``. If
        the list of input variables is not specified in ``run_config.input_vars``, ``get_vars()`` will return ``None``.
        The same is true for the non-linear input scaling expected in ``run_config.input_scaling``. If variables are set
        via ``set_vars`` and no input scaling is available for a variable, the scaling will be set to the identity.

        Parameters
        ----------
        run_config : ModuleType
            Reference to the imported ``run_config`` file.
        """
        self.run_config = run_config

        # get the list of variables to use; if they are not available, set to None and use all variables later
        if hasattr(run_config, "input_vars"):
            self.vars_in_use = run_config.input_vars
            self.as_indices = False
        else:
            self.vars_in_use = None
            self.as_indices = True

        # do the same for the dictionary of non-linear scalings, but also check if any variable in self.vars_in_use does
        # not have an entry in run_config.input_scaling
        if hasattr(run_config, "input_scaling"):
            self.scaling_dict = run_config.input_scaling
            if self.vars_in_use is not None:
                for var in self.vars_in_use:
                    if var not in self.scaling_dict.keys():
                        self.scaling_dict[var] = ("linear", (1.0, 0.0))
        else:
            if self.vars_in_use is not None:
                self.scaling_dict = {var: ("linear", (1.0, 0.0)) for var in self.vars_in_use}
            else:
                self.scaling_dict = None

    def set_vars(self, input_vars: list[Union[str, tuple[int]]], as_indices: Optional[bool] = False) -> None:
        """Update the currently used input variables and the scaling dictionary.

        Parameters
        ----------
        input_vars : list[Union[str, tuple[int]]]
            List containing the names of the input variables to use.
        as_indices : Optional[bool]
            Indicates if ``input_vars`` contains a list of variable names or a list of tuples of indices. (Default value = False)
        """
        # if the inputs are given as a list of indices, generate labels of type '2_3_1' for index (2, 3, 1)
        self.as_indices = as_indices
        if not as_indices:
            self.vars_in_use = input_vars
        else:
            self.vars_in_use = ["_".join([str(index) for index in indices]) for indices in input_vars]

        # if no non-linear scalings are given, use identity instead
        if hasattr(self.run_config, "input_scaling"):
            self.scaling_dict = {}
            for var in self.vars_in_use:
                if self.run_config.input_scaling.get(var) is None:
                    self.scaling_dict[var] = ("linear", (1.0, 0.0))
                else:
                    self.scaling_dict[var] = self.run_config.input_scaling[var]
        else:
            self.scaling_dict = {var: ("linear", (1.0, 0.0)) for var in self.vars_in_use}

    def get_vars(self, as_indices: Optional[bool] = False) -> Optional[Union[list[str], list[tuple[int]]]]:
        """Get the list of currently used input variables.

        Parameters
        ----------
        as_indices : Optional[bool]
            If True, returns the input variables as indices instead of strings. This only works if the input variables
            have originally been provided as indices. (Default value = False)

        Returns
        -------
        Optional[Union[list[str], list[tuple[int]]]]
            _description_
        """
        # if the variables were provided as indices, we extract them again from the corresponding labels
        if (not as_indices) or self.vars_in_use is None:
            return self.vars_in_use
        else:
            return [tuple(int(index) for index in indices_str.split("_")) for indices_str in self.vars_in_use]

    def get_nonlinear_scaling(self) -> dict[str, tuple[str, tuple[float, float]]]:
        """Get the dictionary containing the non-linear transformation (as a callable) to apply to all input variables in use.

        Returns
        -------
        dict[str : dict[str, tuple[str, tuple[float, float]]]
            Dictionary of non-linear transformations for the input variables in use.
        """
        return self.scaling_dict

    def copy(self) -> "InputHandler":
        """Performs a shallow copy of the ``InputHandler``.

        Returns
        -------
        "InputHandler"
            New ``InputHandler`` instance with the same state.
        """
        new_input_handler = InputHandler(self.run_config)
        new_input_handler.set_vars(copy.deepcopy(self.vars_in_use))
        return new_input_handler


class DummyScaler:
    """Dummy scaler used when the input variables don't need scaling."""

    def __init__(self) -> None:
        """Constructor of DummyScaler."""
        pass

    def fit(self, x: np.ndarray, sample_weight: Optional[np.ndarray] = None) -> Self:
        """`Placeholder`.

        Parameters
        ----------
        x : np.ndarray
            `Unused`.
        sample_weight : Optional[np.ndarray]
            `Unused`. (Default value = None)

        Returns
        -------
        Self
            Returns itself.
        """
        return self

    def transform(self, x: np.ndarray) -> np.ndarray:
        """`Placeholder`.

        Parameters
        ----------
        x : np.ndarray
            `Unused`.

        Returns
        -------
        np.ndarray
            Returns the inputs unchanged.
        """
        return x


class ManualScaler:
    """Scaler that applies the manually chosen, non-linear transformations saved in the InputHander."""

    def __init__(self, input_handler: InputHandler) -> None:
        """Constructor of ``ManualScaler``. Needs a reference to an ``InputHandler`` instance to get the non-linear transformations.

        Parameters
        ----------
        input_handler : InputHandler
            Reference to an instance of ``InputHandler``.
        """
        self.input_handler = input_handler
        scaling_dict = input_handler.get_nonlinear_scaling()

        self.non_linear_ops = []
        for var in input_handler.get_vars():
            scaling = scaling_dict.get(var)
            if scaling is not None and scaling[0] == "sqrt":
                self.non_linear_ops.append((np.sqrt, scaling[1][0], scaling[1][1]))
            elif scaling is not None and scaling[0] == "log10":
                self.non_linear_ops.append((np.log10, scaling[1][0], scaling[1][1]))
            elif scaling is not None and scaling[0] == "linear":
                self.non_linear_ops.append((lambda x: x, scaling[1][0], scaling[1][1]))
            elif scaling is None:
                self.non_linear_ops.append((lambda x: x, 1.0, 0.0))
            else:
                raise ValueError(f"Unknown scaling type {scaling}.")

    def fit(self, input_data: np.ndarray, sample_weight: Optional[np.ndarray] = None) -> Self:
        """Placeholder function.

        This function is provided to be consistent with the other scalers, although fitting to data is not required.

        Parameters
        ----------
        input_data : np.ndarray
            `Unused`.
        sample_weight : Optional[np.ndarray]
            `Unused`. (Default value = None)

        Returns
        -------
        Self
            Returns itself
        """
        return self

    def transform(self, input_data: np.ndarray) -> np.ndarray:
        """Transform a given input according to the non-linear transformations given in the ``InputHandler``.

        Parameters
        ----------
        input_data : np.ndarray
            The data to be transformed.

        Returns
        -------
        np.ndarray
            The transformed data.
        """
        vars_in_use = self.input_handler.get_vars()

        transformed_inputs = np.empty_like(input_data)
        for i in range(len(vars_in_use)):
            transformation, scale, offset = self.non_linear_ops[i]
            transformed_inputs[:, i] = transformation(scale * input_data[:, i] + offset)
        return transformed_inputs


class ManualPlusPowerTransformer(sklearn.preprocessing.PowerTransformer):
    """Extends `sklearn`'s ``PowerTransformer`` by the manual non-linear transformations specified in the ``run_config``.

    Before giving the inputs to the ``PowerTransformer``, the non-linear transformations given in the ``InputHandler`` are
    applied.
    """

    def __init__(self, input_handler: InputHandler, method: str = "yeo-johnson", *, standardize: bool = True) -> None:
        """Constructor of ``ManualPlusPowerTransformer``.

        Parameters
        ----------
        input_handler : InputHandler
            Reference to an ``InputHandler`` instance.
        method : str
            The power transform method. Parameter of `sklearn`'s ``PowerTransformer``. (Default value = "yeo-johnson")
        standardize : bool
            Set to ``True`` to apply zero-mean, unit-variance normalization to the transformed output. Parameter of
            `sklearn`'s PowerTransformer. (Default value = True)
        """
        self.manual_scaler = ManualScaler(input_handler)
        super(ManualPlusPowerTransformer, self).__init__(method, standardize=standardize, copy=False)

    def fit(self, X: np.ndarray, y: Any = None) -> Self:
        """Estimate the optimal parameters of the ``PowerTransformer``.

        The ``PowerTransformer`` is fitted to the transformed inputs, i.e. the non-linear transformations given in the
        ``InputHandler`` are applied to the inputs before giving them to the ``PowerTransformer``'s ``fit``-function.

        Parameters
        ----------
        X : np.ndarray
            The data used to estimate the optimal transformation parameters.
        y : Any
            Parameter of the ``fit``-function of the ``PowerTransformer``. (Default value = None)

        Returns
        -------
        Self
            Returns itself with the ``PowerTransformer``-parameters fitted to the input data.
        """
        X_manually_scaled = self.manual_scaler.transform(X)
        return super(ManualPlusPowerTransformer, self).fit(X_manually_scaled, y=y)

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transforms the given input data.

        Firstly, the manual transformations given in the ``InputHandler`` instance are applied, afterwards the inputs are
        scaled by the ``PowerTransformer``. The transformed inputs are returned. Before transforming, the scaler needs to be
        fitted to data by calling the ``fit``-function.

        Parameters
        ----------
        X : np.ndarray
            The data to be transformed.

        Returns
        -------
        np.ndarray
            The transformed data.
        """
        X_manually_scaled = self.manual_scaler.transform(X)
        X_scaled = super(ManualPlusPowerTransformer, self).transform(X_manually_scaled)
        return X_scaled

    def inverse_transform(self, X: np.ndarray) -> None:
        """`Not implemented`.

        Parameters
        ----------
        X : np.ndarray
            The transformed data.
        """
        raise NotImplementedError


class ManualPlusStandardScaler(sklearn.preprocessing.StandardScaler):
    """Extends `sklearn`'s ``StandardScaler`` by the manual non-linear transformations specified in the ``run_config``.

    Before giving the inputs to the ``StandardScaler``, the non-linear transformations given in the ``InputHandler`` are
    applied.
    """

    def __init__(self, input_handler: InputHandler) -> None:
        """Constructor of the ``ManualPlusStandardScaler``.

        Parameters
        ----------
        input_handler : InputHandler
            Reference to an ``InputHandler`` instance.
        """
        self.input_handler = input_handler
        self.manual_scaler = ManualScaler(input_handler)
        super(ManualPlusStandardScaler, self).__init__(copy=False)

    def fit(self, X: np.ndarray, y: Any = None) -> Self:
        """Applies the manual non-linear transformations, then fits the ``StandardScaler`` on the transformed input.

        Parameters
        ----------
        X : np.ndarray
            The data used to estimate the optimal transformation parameters.
        y : Any
            Parameter of the ``StandardScaler``'s fit function. (Default value = None)

        Returns
        -------
        Self
            Returns itself, with the parameters of the ``StandardScaler`` fitted to the input data.
        """
        X_manually_scaled = self.manual_scaler.transform(X)
        return super(ManualPlusStandardScaler, self).fit(X_manually_scaled, y=y)

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transforms a given input by first applying the manual, non-linear and then the ``StandardScaler``'s linear transformations.

        The non-linear transformation is given by the transformations specified in the provided ``InputHandler`` instance.
        The transformed data is returned. Before transforming, the scaler needs to be fitted to data by calling the
        ``fit``-function.

        Parameters
        ----------
        X : np.ndarray
            The data to be transformed.

        Returns
        -------
        np.ndarray
            The transformed data.
        """
        X_manually_scaled = self.manual_scaler.transform(X)
        X_scaled = super(ManualPlusStandardScaler, self).transform(X_manually_scaled)
        return X_scaled

    def inverse_transform(self, X: np.ndarray) -> None:
        """`Not implemented`.

        Parameters
        ----------
        X : np.ndarray
            The transformed data.
        """
        raise NotImplementedError


class CustomManualPlusStandardScaler:
    """Simpler version of the ``ManualPlusStandardScaler`` without the `sklearn` dependency when saving.

    In case the scaler shall be used in an environment with a different `sklearn` version (e.g. in the CAF environment),
    the scaler cannot be a subclass of an `sklearn` scaler. Thus, provide crude version of a Manual+Linear scaler for
    these cases and only import the ``StandardScaler`` during the fit for the mean and scale calculation.
    """

    def __init__(self, input_handler: InputHandler) -> None:
        """The constructor of ``CustomManualPlusStandardScaler``.

        Parameters
        ----------
        input_handler : InputHandler
            Reference to an ``InputHandler`` instance.
        """
        self.input_handler = input_handler
        self.manual_scaler = ManualScaler(input_handler)
        self.mean_ = None
        self.scale_ = None

    def fit(self, X: np.ndarray, sample_weight: Optional[np.ndarray] = None, y: Any = None) -> Self:
        """Fit the parameters of the linear transformation to the given input data.

        First, the manually specified non-linear transformations given in the ``InputHandler`` are applied. Afterwards,
        `sklearn`'s ``StandardScaler`` is imported and fitted to the transformed data. The scale and offset parameters
        (``mean_`` and ``scale_``) are extracted and saved. An instance of the ``CustomManualPlusStandardScaler``-class is
        returned with the adjusted parameters.

        Parameters
        ----------
        X : np.ndarray
            The data used to estimate the optimal transformation parameters.
        sample_weight : Optional[np.ndarray]
            Weight of each individual sample in ``X``. Parameter of the ``StandardScaler``'s ``fit``-function. (Default value = None)
        y : Any
            Parameter of the ``StandardScaler``'s ``fit``-function. (Default value = None)

        Returns
        -------
        Self
            Returns itself, with the transformation parameters adjusted.
        """
        X_manually_scaled = self.manual_scaler.transform(X)

        from sklearn.preprocessing import StandardScaler

        standard_scaler = StandardScaler()
        standard_scaler.fit(X_manually_scaled, sample_weight=sample_weight, y=y)

        self.mean_ = standard_scaler.mean_
        self.scale_ = standard_scaler.scale_

        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transforms a given input by first applying the manual, non-linear and then a linear transformation.

        The non-linear transformation is given by the transformations specified in the provided ``InputHandler`` instance.
        The linear transformation is calculated according to ``x_scaled = (x - mean_) / scale_``. The transformed inputs
        are returned. Before transforming, the scaler needs to be fitted to data by calling the ``fit``-function.

        Parameters
        ----------
        X : np.ndarray
            The data to transform.

        Returns
        -------
        np.ndarray
            The transformed data.
        """
        assert (
            self.mean_ is not None and self.scale_ is not None
        ), "The scaler needs to be fitted to data first before applying the transformation!"

        X_manually_scaled = self.manual_scaler.transform(X)
        X_scaled = (X_manually_scaled - self.mean_) / self.scale_

        return X_scaled

    def save(self, path: str) -> None:
        """Saves the parameters of the linear transformation to a pickle-file.

        Parameters
        ----------
        path : str
            Path of the pickle-file.
        """
        with open(path, "wb") as f:
            pickle.dump((self.mean_, self.scale_), f)

    def load(self, path: str) -> None:
        """Loads the parameters of the linear transformation from a pickle-file.

        Parameters
        ----------
        path : str
            Path of the pickle-file.
        """
        with open(path, "rb") as f:
            self.mean_, self.scale_ = pickle.load(f)


def get_inputs(
    run_config: ModuleType,
    nevts: Union[int, float, Literal[np.inf], list[int]],
    input_vars_list: Optional[list[Union[str, tuple[int]]]] = None,
    disable_printing: bool = False,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """From a given pickle-file, the input data is loaded and the event weights of all classes are normalized.

    The path of the pickle-file is taken from the ``run_config``. The pickle-file is expected to contain a pandas dataframe
    concatenated from two dataframes with keys ``'features'`` and ``'targets'`` containing the event information and
    corresponding class label, respectively. The features-dataframe must contain the columns ``'Weight'`` and
    ``'EventNumber'`` assigning each event a weight and a number. The remaining columns are interpreted as input variables.
    The targets-dataset is assumed to have the shape ``(Nevents, Nclasses)``, with ``Nevents`` the total number of events.

    The number of events read from the pickle-file is controlled by the ``nevts``-parameter. It can either be specified
    as a list of Nclasses elements (thus explicitly specifying the number of events to load per class), as a single
    number (resulting in an equal split between the classes, when possible), or be set to ``np.inf`` to load the full
    available dataset.

    The event weights are reweighted to give the same total weight (sum over all weights) for all classes. If the
    ``max_event_weight``-parameter is set in the ``run_config``, an event duplication are performed where events with
    weight larger than ``max_event_weight`` times the median weight are duplicated and the corresponding weight is halved.
    This is repeated until all event weights are small enough. Finally, all event weights are normalized to reach an
    average weight (over all classes) of one.

    Parameters
    ----------
    run_config : ModuleType
        Reference to the imported ``run_config``.
    nevts : Union[int, float, Literal[np.inf], list[int]]
        Parameter controlling the number of events loaded from the pickle-file input file whose path is specified in the
        ``run_config``.
    input_vars_list : Optional[list[Union[str, tuple[int]]]]
        List of input variables to load from the input data. If this is a list of strings, they are assumed to be
        present as columns in ``events_df["features"]``. If a list of tuples of indices is given, each tuple is interpreted
        as the index of an input, i.e. (1,) would correspond to the second input variable. Higher-dimensional indices are
        not supported. If a value of ``None`` is given, all columns besides ``'Weight'``, ``'weight'`` and
        ``'EventNumber'`` will be used. (Default value = None)
    disable_printing : bool
        If ``True``, no messages are printed. (Default value = False)

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]
        The arrays of input variables, target labels, event weights, normalized event weights and event numbers are
        returned.
    """
    # load events from input file
    events_df = pd.read_pickle(run_config.inputs_file)
    features_df = events_df["features"]
    targets_df = events_df["targets"]
    del events_df

    # check if the input data is for binary or multiclass classification
    num_classes = targets_df.shape[1]
    if num_classes == 1:
        binary_classification = True
        num_classes = 2
    else:
        binary_classification = False

    # get available number of events for each class in case any of them are underrepresented in the input data
    avail_events = []
    if binary_classification:
        avail_events.append(targets_df[targets_df.iloc[:, 0] == 1].shape[0])
        avail_events.append(targets_df[targets_df.iloc[:, 0] == 0].shape[0])
    else:
        for i in range(num_classes):
            avail_events.append(targets_df[targets_df.iloc[:, i] == 1].shape[0])

    # sanity check
    if nevts == np.inf:
        target_events = [round(features_df.shape[0])] * num_classes
    else:
        if isinstance(nevts, int) or isinstance(nevts, float):
            requested_events = [round(nevts / num_classes)] * num_classes
        elif isinstance(nevts, list) or isinstance(nevts, tuple):
            assert (
                len(nevts) == num_classes
            ), f"nevents has to be int or list/tuple with the same length as the number of classes ({num_classes})!"
            requested_events = nevts
        else:
            raise TypeError

        # check if enough signal and background are available
        target_events = np.minimum(avail_events, requested_events)
        if not (target_events == requested_events).all():
            print(f"Not enough events to satisfy the request of {requested_events}, can only provide {target_events}.")

    # we need to shuffle the events and targets first in case they are ordered by process --> would introduce bias when
    # not using all events!
    features_df = features_df.sample(frac=1, random_state=4242)
    targets_df = targets_df.sample(frac=1, random_state=4242)

    # select the desired number of events for each class
    features_dfs_per_class = []
    targets_dfs_per_class = []
    if binary_classification:
        features_dfs_per_class.append(features_df[targets_df.iloc[:, 0] == 1][: target_events[0]])
        features_dfs_per_class.append(features_df[targets_df.iloc[:, 0] == 0][: target_events[1]])
        targets_dfs_per_class.append(targets_df[targets_df.iloc[:, 0] == 1][: target_events[0]])
        targets_dfs_per_class.append(targets_df[targets_df.iloc[:, 0] == 0][: target_events[1]])
    else:
        for i in range(num_classes):
            features_dfs_per_class.append(features_df[targets_df.iloc[:, i] == 1][: target_events[i]])
            targets_dfs_per_class.append(targets_df[targets_df.iloc[:, i] == 1][: target_events[i]])
    del targets_df

    # get the inputs
    features_df = pd.concat(features_dfs_per_class)
    if input_vars_list is None:
        inputs = features_df.drop(
            [col for col in ["Weight", "weight", "EventNumber"] if col in features_df.columns], axis=1
        ).to_numpy()
    elif isinstance(input_vars_list[0], tuple):
        inputs = features_df.iloc[:, [index[0] for index in input_vars_list]].to_numpy()
    else:
        inputs = features_df[input_vars_list].to_numpy()

    targets = pd.concat(targets_dfs_per_class).to_numpy()
    if "weight" in features_df.columns:
        weights = features_df["weight"].to_numpy()
    elif "Weight" in features_df.columns:
        weights = features_df["Weight"].to_numpy()
    else:
        raise KeyError(
            f'No weight found in the input features {list(features_df.columns)}. Valid keys for the weights are "Weight" and "weight"'
        )
    if "EventNumber" in features_df.columns:
        event_nums = features_df["EventNumber"].to_numpy()
    else:
        raise KeyError(f"No 'EventNumber' found in the input features {list(features_df.columns)}.")
    del features_df

    # examine input data
    if not disable_printing:
        print("input data features (number of events, number of features): {}".format(inputs.shape))
        print("Printing example inputs:")
        print(inputs[1:5])
        print("Input labels (number of events, number of features) ", targets.shape)
        print(targets[1:5])

    # get the total event weight for each class
    total_weights = []
    if binary_classification:
        total_weights.append(np.sum(weights[targets[:, 0] == 1]))
        total_weights.append(np.sum(weights[targets[:, 0] == 0]))
    else:
        for i in range(num_classes):
            total_weights.append(np.sum(weights[targets[:, i] == 1]))
    if not disable_printing:
        print(f"Total weights for each class: {total_weights}")

    # reweight to get the same total weight for all classes
    normalized_weights = weights.copy()
    if binary_classification:
        normalized_weights[targets[:, 0] == 1] /= total_weights[0]
        normalized_weights[targets[:, 0] == 0] /= total_weights[1]
    else:
        for i in range(num_classes):
            normalized_weights[targets[:, i] == 1] /= total_weights[i]

    # check for maximal event weight
    if not np.isinf(run_config.max_event_weight):
        # normalize the weights by the median
        normalized_weights /= np.median(normalized_weights)

        # for large event weights, duplicate corresponding event and reduce the event weight correspondingly
        while np.any(normalized_weights > run_config.max_event_weight):
            if not disable_printing:
                print(
                    f"{normalized_weights[normalized_weights > run_config.max_event_weight].shape[0]} events with normalized "
                    f"weight greater than {run_config.max_event_weight} found, duplicating..."
                )
            inputs = np.concatenate((inputs, inputs[normalized_weights > run_config.max_event_weight, :]))
            targets = np.concatenate((targets, targets[normalized_weights > run_config.max_event_weight, :]))
            weights = np.concatenate((weights, weights[normalized_weights > run_config.max_event_weight]))
            event_nums = np.concatenate((event_nums, event_nums[normalized_weights > run_config.max_event_weight]))
            normalized_weights = np.concatenate(
                (normalized_weights, normalized_weights[normalized_weights > run_config.max_event_weight])
            )
            weights[normalized_weights > run_config.max_event_weight] /= 2
            normalized_weights[normalized_weights > run_config.max_event_weight] /= 2

    # set the average weight to 1
    normalized_weights /= np.mean(normalized_weights)
    if not disable_printing:
        print("average weight after normalization: {}".format(np.mean(normalized_weights)))

    # shuffle all arrays in the same way to mix the classes again
    random_indices = np.arange(targets.shape[0])
    rng = np.random.RandomState(42)
    rng.shuffle(random_indices)
    targets = targets[random_indices]
    inputs = inputs[random_indices]
    weights = weights[random_indices]
    normalized_weights = normalized_weights[random_indices]
    event_nums = event_nums[random_indices]

    return inputs, targets, weights, normalized_weights, event_nums


def plot_input_data(
    run_config: ModuleType,
    inputs: np.ndarray,
    targets: np.ndarray,
    input_vars_list: list,
    outdir: str,
    weights: Optional[np.ndarray] = None,
) -> None:
    """Plots the distribution of each target class for each input variable in inputs and saves them to ``outdir``.

    The ``input_vars_list`` is used for the filename of each plot. The names of input variables in ``input_vars_list`` are
    assumed to be in the same order as in ``inputs``.

    Parameters
    ----------
    run_config : ModuleType
        A reference to the inported run-config file.
    inputs : np.ndarray
        2D Array containing the values of the input variables for each event. The axis 0 is assumed to separate
        the different events.
    targets : np.ndarray
        Array of shape ``(Nevents, Nclasses)`` of target labels denoting the class of each event.
    input_vars_list : list
        List of variable names. It must be in the same order as the input variables in ``inputs`` (axis 1).
    outdir : str
        Path of the output folder the plots will be saved into.
    weights : Optional[np.ndarray]
        1D array of event weights. (Default value = None)
    """
    for i, var in enumerate(input_vars_list):
        vals_per_class = []
        if weights is not None:
            weights_per_class = []
        if targets.shape[1] == 1:
            vals_per_class.append(inputs[targets[:, 0] == 1, i])
            vals_per_class.append(inputs[targets[:, 0] == 0, i])
            if weights is not None:
                weights_per_class.append(weights[targets[:, 0] == 1])
                weights_per_class.append(weights[targets[:, 0] == 0])
        else:
            for j in range(targets.shape[1]):
                vals_per_class.append(inputs[targets[:, j] == 1, i])
                if weights is not None:
                    weights_per_class.append(weights[targets[:, j] == 1])

        fig, ax = plt.subplots(figsize=[8, 6], layout="constrained")
        if weights is not None:
            ax.hist(
                vals_per_class,
                bins=40,
                weights=weights_per_class,
                histtype="step",
                density=True,
                label=run_config.evaluation_class_labels,
            )
        else:
            ax.hist(
                vals_per_class,
                bins=40,
                histtype="step",
                density=True,
                label=run_config.evaluation_class_labels,
            )
        ax.set_xlabel(var)
        ax.legend()
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        fig.savefig(os.path.join(outdir, "inputs_{}.pdf".format(var)))
        plt.close()


train_val_splitting_type = tuple[Union[np.ndarray, list[np.ndarray]], Union[np.ndarray, list[np.ndarray]]]
train_val_test_splitting_type = tuple[
    Union[np.ndarray, list[np.ndarray]], Union[np.ndarray, list[np.ndarray]], Union[np.ndarray, list[np.ndarray]]
]


def get_training_data(
    inputs: np.ndarray,
    targets: np.ndarray,
    weights: np.ndarray,
    normalized_weights: np.ndarray,
    splitting_cond: Union[Union[tuple[Callable], tuple[float]], Union[list[Callable], list[float]], Callable, float],
    preprocessor: Optional[tuple[type, tuple]] = None,
    event_nums: Optional[np.ndarray] = None,
    do_kfold: bool = False,
    fixed_test_dataset: bool = True,
    disable_printing: bool = False,
) -> Union[
    tuple[
        Any,
        train_val_test_splitting_type,
        train_val_test_splitting_type,
        train_val_test_splitting_type,
        train_val_test_splitting_type,
    ],
    tuple[
        train_val_test_splitting_type,
        train_val_test_splitting_type,
        train_val_test_splitting_type,
        train_val_test_splitting_type,
    ],
    tuple[Any, train_val_splitting_type, train_val_splitting_type, train_val_splitting_type, train_val_splitting_type],
    tuple[train_val_splitting_type, train_val_splitting_type, train_val_splitting_type, train_val_splitting_type],
]:
    """Preprocesses and splits the input data into training, validation and testing samples according to a splitting condition.

    The splitting condition can either be a float, a list or tuple of two floats, a callable or a list or tuple of two
    callables. If the splitting condition does not contain callables, the ``do_kfold``-parameter decides if the outputs for
    simple splitting or k-fold crossvalidation are returned. If callables are included in the splitting condition, this
    is decided by the shape of return value of the callables.

    For ``float`` and ``Union[tuple[float, float], list[float, float]]``:

    - if ``do_kfold`` is ``False``:
        - ``float``: random split into training and validation, the splitting condition controls the fraction of validation events.
        - ``Union[tuple[float, float], list[float, float]]``: random splits into training, validation and testing; the first
          entry controls the fraction of testing events, the second entry the fraction of validation events.
    - if ``do_kfold`` is ``True``:
        - ``float``: `sklearn`'s ``KFold`` is used to split the dataset into ``round(1 / splitting_cond)`` folds of training and
          validation data. The inputs are not shuffled prior to the splitting.
        - ``Union[tuple[float, float], list[float, float]]``: the behaviour depends on the value of ``fixed_test_dataset``:
            - if ``fixed_test_dataset`` is ``True``: the testing dataset is split from the full dataset using random
              splitting and kept constant for all folds; splitting_cond[0] controls the fraction of testing events. With
              the remaining dataset, ``round((1 - test_split) / val_split)`` folds of training and validation data are
              created using `sklearn`'s ``KFold``. The inputs are not shuffled prior to the splitting.
            - if ``fixed_test_dataset`` is ``False``: the testing dataset is `not` kept constant and instead varied
              together with the validation dataset in a k-fold-like manner. Depending on the requested size of the
              validation and testing datasets, the dataset is split into ``N`` subsets using `sklearn`'s ``KFold``. ``N``
              is chosen so that the validation and testing sizes can be reached by combining a certain number of subsets.
              E.g., if ``test_split=0.2`` and ``val_split=0.1`` are requested, ``N=10`` and the testing sets are build by
              combining two subsets. For each fold, different subsets are combined to build the training, validation and
              testing sets. The total number of folds is given by the size of the testing dataset, i.e. in the example,
              five folds will be returned. As a result, while the concatenation of the testing datasets of all folds is
              guaranteed to reproduce the full dataset, for the validation datasets this is only true if ``val_split``
              = ``test_split``. Otherwise, the validation datasets may be overlapping (for ``val_split`` > ``test_split``)
              or may leave gaps (``val_split`` < ``test_split``). For ``val_split`` = ``test_split``, each sample is
              exactly once part of the validation and the testing datasets. The inputs are not shuffled prior to the
              splitting.

    For splitting conditions containing a callable, the array of event numbers (``event_nums``) must not be ``None``.
    The dataset is split according to:

    - ``callable``: ``splitting_cond``, when provided with ``event_nums``, is expected to return an array or a list of
      arrays of the same shape as ``event_nums``, with values ``True`` for events that should be included in the
      validation dataset and ``False`` otherwise. A returned list of `k` arrays results in `k` pairs of training and
      validation datasets.
    - ``Union[tuple[Callable, Callable], list[Callable, Callable]]``: the return value of ``splitting_cond[0]``, when
      provided with ``event_nums``, is used to split the full dataset into a testing and a training+validation set. The
      corresponding return value of ``splitting_cond[1]`` is used to split the training+validation set into a
      training and a validation set. As a result, both splitting conditions must either return an array or a list
      of arrays. For each fold (when a list of arrays is returned), the `i`-th list entries from both lists is used
      to determine the splitting of the `i`-th fold.

    For each fold (or the single splitting when not doing k-fold), the provided preprocessing scaler is instantiated and
    fitted to the input variables of the training dataset. The inputs for the training, validation, and (if present)
    testing dataset are subsequently scaled. If no preprocessing scaler is provided, the split inputs remain unchanged.

    The return type of the split inputs, targets, weights and normalized_weights differs if k-fold splitting was
    performed or not. If no k-fold was done, the training, validation and (if present) testing splits of each are combined
    into a tuple. If k-fold splitting was done, the `k` training, validation and (if present) testing splits are each first
    combined into a list before combining them into a tuple. Thus, for k-fold, tuples of 2 or 3 lists containing `k` numpy
    arrays each are returned.

    Parameters
    ----------
    inputs : np.ndarray
        Array of input features. The axis 0 is assumed to separate different events.
    targets : np.ndarray
        Array of target labels.
    weights : np.ndarray
        Array of event weight.
    normalized_weights : np.ndarray
        Array of normalized event weights.
    splitting_cond : Union[Union[tuple[Callable], tuple[float]], Union[list[Callable], list[float]], Callable, float]
        Condition determining the splitting of inputs, targets, weights and normalized_weights into training, validation
        and (potentially) testing sets.
    preprocessor : Optional[tuple[type, tuple]]
        A reference to an input scaler class and the necessary tuple of arguments to instantiate it. (Default value = None)
    event_nums : Optional[np.ndarray]
        Array of event numbers. (Default value = None)
    do_kfold : bool
        If ``splitting_cond`` does not contain a callable, this controls if a simple splitting or k-fold splitting should be
        done. (Default value = False)
    fixed_test_dataset : bool
        If ``True``, a fixed testing dataset will be used for all folds. If ``False``, the testing dataset will be shuffled in
        a k-fold-like manner. Only relevant if ``do_kfold`` is ``True``. (Default value = True)
    disable_printing : bool
        If ``True``, no output will be printed. (Default value = False)

    Returns
    -------
    Union[
        tuple[
        Any,
        train_val_test_splitting_type,
        train_val_test_splitting_type,
        train_val_test_splitting_type,
        train_val_test_splitting_type,
        ],
        tuple[Any, train_val_splitting_type, train_val_splitting_type, train_val_splitting_type, train_val_splitting_type],
    ]
        Returns the fitted input scaler (if it was provided) and tuples for each of inputs, targets, weights and normalized weights containing
        the training, validation and (potentially) testing sets / lists of sets.
    """
    if isinstance(splitting_cond, tuple) or isinstance(splitting_cond, list):
        use_testing_dataset = True
        splitting_cond_test, splitting_cond_val = splitting_cond
        if callable(splitting_cond_test) and callable(splitting_cond_val):
            assert (
                event_nums is not None
            ), "array of event numbers must be provided when using custom splitting condition"
            custom_splitting_condition = True
        elif isinstance(splitting_cond_test, float) and isinstance(splitting_cond_val, float):
            custom_splitting_condition = False
            test_split = splitting_cond_test
            val_split = splitting_cond_val
        else:
            if not disable_printing:
                print(
                    "Splitting condition must either be a float or a callable for both splitting_cond_test and "
                    "splitting_cond_val. Exiting..."
                )
            sys.exit(1)
    else:
        use_testing_dataset = False
        splitting_cond_val = splitting_cond
        if callable(splitting_cond):
            assert (
                event_nums is not None
            ), "array of event numbers must be provided when using custom splitting condition"
            custom_splitting_condition = True
        elif isinstance(splitting_cond, float):
            custom_splitting_condition = False
            val_split = splitting_cond_val
        else:
            if not disable_printing:
                print(
                    "Splitting condition must either be a float or a callable for both splitting_cond_test and "
                    "splitting_cond_val. Exiting..."
                )
            sys.exit(1)

    # total number of events
    ntotal_evts = inputs.shape[0]

    if not custom_splitting_condition:
        if not do_kfold:
            if use_testing_dataset:
                # random splitting into training, validation and testing data
                (
                    inputs_trainVal,
                    inputs_test,
                    targets_trainVal,
                    targets_test,
                    weights_trainVal,
                    weights_test,
                    normalized_weights_trainVal,
                    normalized_weights_test,
                ) = train_test_split(
                    inputs, targets, weights, normalized_weights, test_size=test_split, random_state=1234
                )
                (
                    inputs_train,
                    inputs_val,
                    targets_train,
                    targets_val,
                    weights_train,
                    weights_val,
                    normalized_weights_train,
                    normalized_weights_val,
                ) = train_test_split(
                    inputs_trainVal,
                    targets_trainVal,
                    weights_trainVal,
                    normalized_weights_trainVal,
                    test_size=val_split / (1 - test_split),
                    random_state=4321,
                )
            else:
                (
                    inputs_train,
                    inputs_val,
                    targets_train,
                    targets_val,
                    weights_train,
                    weights_val,
                    normalized_weights_train,
                    normalized_weights_val,
                ) = train_test_split(
                    inputs, targets, weights, normalized_weights, test_size=val_split, random_state=1234
                )

            # fit the scaler to the training data and scale all datasets
            if preprocessor is not None:
                scaler = preprocessor[0](*preprocessor[1])
                scaler.fit(inputs_train, sample_weight=normalized_weights_train)
                inputs_train = scaler.transform(inputs_train)
                inputs_val = scaler.transform(inputs_val)
                if use_testing_dataset:
                    inputs_test = scaler.transform(inputs_test)
        else:
            # when doing KFold splitting, create lists for all arrays and the preprocessing scaler and append each split
            # and the corresponding scaler
            (
                inputs_train,
                inputs_val,
                targets_train,
                targets_val,
                weights_train,
                weights_val,
                normalized_weights_train,
                normalized_weights_val,
            ) = ([], [], [], [], [], [], [], [])
            if preprocessor is not None:
                scaler = []

            # calculate the splitting indices. this is done beforehand because if a non-fixed testing dataset is requested,
            # multiple splits produced by the KFold potentially need to be combined, thus needing manual handling of the
            # splitting indices. If the testing dataset should be fixed or is not required at all, the indices produced
            # directly by KFold can be used.
            if use_testing_dataset:
                # prepare the list to hold the testing dataset for each fold
                inputs_test, targets_test, weights_test, normalized_weights_test = [], [], [], []

                if fixed_test_dataset:
                    # if fixed_test_dataset: extract the test set before k-fold, thus ensuring the same test set for all
                    # folds. Kfold is only used for the training/validation split
                    (
                        inputs,
                        inputs_test_k,
                        targets,
                        targets_test_k,
                        weights,
                        weights_test_k,
                        normalized_weights,
                        normalized_weights_test_k,
                    ) = train_test_split(
                        inputs, targets, weights, normalized_weights, test_size=test_split, random_state=1234
                    )
                    kfold = KFold(n_splits=round((1 - test_split) / val_split), shuffle=False)
                    splitting_indices_list = list(kfold.split(inputs))
                else:
                    # kfold is used for both the trainVal / test and the training/validation splits. Here, the test size
                    # defines the number of folds. To do that, the required number of splits to fulfill the requested
                    # test and validation sizes is calculated. From that, the Lowest Common Multiple defines the number
                    # of splits. As a result, the requested sizes of the validation and testing dataset can be achieved
                    # by combining a certain number of splits. E.g. if test_split=0.2, val_split=0.1, we need 5 splits
                    # for the test size, 10 splits for the validation size, thus 10 splits in total. We can then take
                    # 2 splits to get the testing size and just a single one to get the validation size.
                    num_splits = int(np.lcm(round(1 / test_split), round(1 / val_split)))
                    num_test_splits = int(num_splits / round(1 / test_split))
                    num_val_splits = int(num_splits / round(1 / val_split))
                    kfold = KFold(n_splits=num_splits, shuffle=False)

                    # we only need the indices for the k validation sets.
                    _, splitting_indices_list = zip(*list(kfold.split(inputs)))

                    # splitting_indices_list contains the array of indices for the validation dataset for each of the num_splits folds.
                    # Since we (in general) don't need num_splits folds, we need to combine a certain number of folds to form
                    # the validation and testing dataset for each fold. The remaining folds are used for the training dataset.
                    # The number of folds we need is determined by the size of the testing dataset.
                    train_indices_list, val_indices_list, test_indices_list = [], [], []
                    for i in range(0, num_splits, num_test_splits):
                        test_start = i
                        test_end = (
                            test_start + num_test_splits
                        ) % num_splits  # exclusive: test_end is not part of the test set anymore
                        if test_end > test_start:
                            test_indices = list(range(test_start, test_end))
                        else:
                            test_indices = list(range(test_start, num_splits)) + list(range(test_end))
                        test_indices_list.append(np.concatenate([splitting_indices_list[i] for i in test_indices]))

                        val_start = test_end  # test_end is exclusive!
                        val_end = (val_start + num_val_splits) % num_splits  # exclusive
                        if val_end > val_start:
                            val_indices = list(range(val_start, val_end))
                        else:
                            val_indices = list(range(val_start, num_splits)) + list(range(val_end))
                        val_indices_list.append(np.concatenate([splitting_indices_list[i] for i in val_indices]))

                        train_indices = [i for i in range(num_splits) if i not in test_indices + val_indices]
                        train_indices_list.append(np.concatenate([splitting_indices_list[i] for i in train_indices]))
                    splitting_indices_list = list(zip(train_indices_list, val_indices_list, test_indices_list))
            else:
                # no testing dataset necessary
                kfold = KFold(n_splits=round(1 / val_split), shuffle=False)
                splitting_indices_list = list(kfold.split(inputs))

            # iterate over all splitting indices, create subsets of the inputs for each, and add them to the lists;
            # for each iteration, split the train+val dataset into training and validation using random splitting.
            # also instantiate a preprocessing scaler and fit it to the training data
            for splitting_indices in splitting_indices_list:
                if use_testing_dataset and not fixed_test_dataset:
                    train_index, val_index, test_index = splitting_indices
                else:
                    train_index, val_index = splitting_indices

                # split into two dataset according to kfold indices
                inputs_train_k = inputs[train_index]
                inputs_val_k = inputs[val_index]
                if use_testing_dataset and not fixed_test_dataset:
                    inputs_test_k = inputs[test_index]
                targets_train_k = targets[train_index]
                targets_val_k = targets[val_index]
                if use_testing_dataset and not fixed_test_dataset:
                    targets_test_k = targets[test_index]
                weights_train_k = weights[train_index]
                weights_val_k = weights[val_index]
                if use_testing_dataset and not fixed_test_dataset:
                    weights_test_k = weights[test_index]
                normalized_weights_train_k = normalized_weights[train_index]
                normalized_weights_val_k = normalized_weights[val_index]
                if use_testing_dataset and not fixed_test_dataset:
                    normalized_weights_test_k = normalized_weights[test_index]

                # add the splitted inputs to the corresponding lists
                if preprocessor is not None:
                    # instantiate the scaler, add it to the list and fit it to the training data
                    scaler.append(preprocessor[0](*preprocessor[1]))
                    scaler[-1].fit(inputs_train_k, sample_weight=normalized_weights_train_k)

                    # apply the scaler to the inputs and add all the splits to the corresponding lists
                    inputs_train.append(scaler[-1].transform(inputs_train_k))
                    inputs_val.append(scaler[-1].transform(inputs_val_k))
                    if use_testing_dataset:
                        inputs_test.append(scaler[-1].transform(inputs_test_k))
                    targets_train.append(targets_train_k)
                    targets_val.append(targets_val_k)
                    if use_testing_dataset:
                        targets_test.append(targets_test_k)
                    weights_train.append(weights_train_k)
                    weights_val.append(weights_val_k)
                    if use_testing_dataset:
                        weights_test.append(weights_test_k)
                    normalized_weights_train.append(normalized_weights_train_k)
                    normalized_weights_val.append(normalized_weights_val_k)
                    if use_testing_dataset:
                        normalized_weights_test.append(normalized_weights_test_k)
                else:
                    inputs_train.append(inputs_train_k)
                    inputs_val.append(inputs_val_k)
                    if use_testing_dataset:
                        inputs_test.append(inputs_test_k)
                    targets_train.append(targets_train_k)
                    targets_val.append(targets_val_k)
                    if use_testing_dataset:
                        targets_test.append(targets_test_k)
                    weights_train.append(weights_train_k)
                    weights_val.append(weights_val_k)
                    if use_testing_dataset:
                        weights_test.append(weights_test_k)
                    normalized_weights_train.append(normalized_weights_train_k)
                    normalized_weights_val.append(normalized_weights_val_k)
                    if use_testing_dataset:
                        normalized_weights_test.append(normalized_weights_test_k)
    else:
        # apply splitting according to custom splitting condition: condition returns either True or False, depending on
        # the EventNumber that is given. when the returned splitting condition is 2D (whereas the EventNumbers are only
        # 1D), assume that kfold should be done and repeat the input data the required number of times (depending on
        # condition.shape[0] in that case)
        if use_testing_dataset:
            condition_array_test = splitting_cond_test(event_nums)
            condition_array_val = splitting_cond_val(event_nums)
        else:
            condition_array_val = splitting_cond_val(event_nums)

        # infer if kfold should be done
        if use_testing_dataset:
            do_kfold = isinstance(condition_array_test, list) and isinstance(condition_array_val, list)
            if not do_kfold:
                assert isinstance(condition_array_test, np.ndarray) and isinstance(
                    condition_array_val, np.ndarray
                ), "custom splitting conditions must return numpy array or list of numpy arrays!"
        else:
            do_kfold = isinstance(condition_array_val, list)
            if not do_kfold:
                assert isinstance(condition_array_val, np.ndarray), (
                    "custom splitting conditions must return numpy" " array or list of numpy arrays!"
                )

        if not do_kfold:
            # get the training condition as those entries that are not validation (or test) entries
            if use_testing_dataset:
                condition_array_train = np.logical_and(
                    np.logical_not(condition_array_test), np.logical_not(condition_array_val)
                )
            else:
                condition_array_train = np.logical_not(condition_array_val)

            # do the custom splitting
            inputs_train = inputs[condition_array_train]
            inputs_val = inputs[condition_array_val]
            if use_testing_dataset:
                inputs_test = inputs[condition_array_test]
            targets_train = targets[condition_array_train]
            targets_val = targets[condition_array_val]
            if use_testing_dataset:
                targets_test = targets[condition_array_test]
            weights_train = weights[condition_array_train]
            weights_val = weights[condition_array_val]
            if use_testing_dataset:
                weights_test = weights[condition_array_test]
            normalized_weights_train = normalized_weights[condition_array_train]
            normalized_weights_val = normalized_weights[condition_array_val]
            if use_testing_dataset:
                normalized_weights_test = normalized_weights[condition_array_test]

            # get the scaler, fit on the training inputs and transform all inputs
            if preprocessor is not None:
                scaler = preprocessor[0](*preprocessor[1])
                scaler.fit(inputs_train, sample_weight=normalized_weights_train)
                inputs_train = scaler.transform(inputs_train)
                inputs_val = scaler.transform(inputs_val)
                if use_testing_dataset:
                    inputs_test = scaler.transform(inputs_test)

        else:
            # prepare empty lists for all arrays and the preprocessing scaler
            (
                inputs_train,
                inputs_val,
                targets_train,
                targets_val,
                weights_train,
                weights_val,
                normalized_weights_train,
                normalized_weights_val,
            ) = ([], [], [], [], [], [], [], [])
            if use_testing_dataset:
                inputs_test, targets_test, weights_test, normalized_weights_test = [], [], [], []
            if preprocessor is not None:
                scaler = []
            for conditions_k in (
                zip(condition_array_test, condition_array_val) if use_testing_dataset else condition_array_val
            ):
                if use_testing_dataset:
                    condition_test_k, condition_val_k = conditions_k
                else:
                    condition_val_k = conditions_k

                # get the training condition as those entries that are not validation (or test) entries
                if use_testing_dataset:
                    condition_train_k = np.logical_and(
                        np.logical_not(condition_test_k), np.logical_not(condition_val_k)
                    )
                else:
                    condition_train_k = np.logical_not(condition_val_k)

                # do the custom splitting
                inputs_train_k = inputs[condition_train_k]
                inputs_val_k = inputs[condition_val_k]
                if use_testing_dataset:
                    inputs_test_k = inputs[condition_test_k]
                targets_train_k = targets[condition_train_k]
                targets_val_k = targets[condition_val_k]
                if use_testing_dataset:
                    targets_test_k = targets[condition_test_k]
                weights_train_k = weights[condition_train_k]
                weights_val_k = weights[condition_val_k]
                if use_testing_dataset:
                    weights_test_k = weights[condition_test_k]
                normalized_weights_train_k = normalized_weights[condition_train_k]
                normalized_weights_val_k = normalized_weights[condition_val_k]
                if use_testing_dataset:
                    normalized_weights_test_k = normalized_weights[condition_test_k]

                # add the split inputs to the corresponding lists
                if preprocessor is not None:
                    # instantiate the scaler, add it to the list, fit it on this iterations training data and transform all inputs
                    scaler.append(preprocessor[0](*preprocessor[1]))
                    scaler[-1].fit(inputs_train_k, sample_weight=normalized_weights_train_k)

                    # apply the scaler to the inputs and add all the splits to the corresponding lists
                    inputs_train.append(scaler[-1].transform(inputs_train_k))
                    inputs_val.append(scaler[-1].transform(inputs_val_k))
                    if use_testing_dataset:
                        inputs_test.append(scaler[-1].transform(inputs_test_k))
                    targets_train.append(targets_train_k)
                    targets_val.append(targets_val_k)
                    if use_testing_dataset:
                        targets_test.append(targets_test_k)
                    weights_train.append(weights_train_k)
                    weights_val.append(weights_val_k)
                    if use_testing_dataset:
                        weights_test.append(weights_test_k)
                    normalized_weights_train.append(normalized_weights_train_k)
                    normalized_weights_val.append(normalized_weights_val_k)
                    if use_testing_dataset:
                        normalized_weights_test.append(normalized_weights_test_k)
                else:
                    inputs_train.append(inputs_train_k)
                    inputs_val.append(inputs_val_k)
                    if use_testing_dataset:
                        inputs_test.append(inputs_test_k)
                    targets_train.append(targets_train_k)
                    targets_val.append(targets_val_k)
                    if use_testing_dataset:
                        targets_test.append(targets_test_k)
                    weights_train.append(weights_train_k)
                    weights_val.append(weights_val_k)
                    if use_testing_dataset:
                        weights_test.append(weights_test_k)
                    normalized_weights_train.append(normalized_weights_train_k)
                    normalized_weights_val.append(normalized_weights_val_k)
                    if use_testing_dataset:
                        normalized_weights_test.append(normalized_weights_test_k)

    if not do_kfold:
        if use_testing_dataset and not disable_printing:
            print(
                f"splitting the total number of {ntotal_evts} events in {inputs_train.shape[0]} train, "
                f"{inputs_val.shape[0]} validation and {inputs_test.shape[0]} test events."
            )
        elif not disable_printing:
            print(
                f"splitting the total number of {ntotal_evts} events in {inputs_train.shape[0]} train and "
                f"{inputs_val.shape[0]} validation events."
            )
    else:
        if use_testing_dataset:
            num_splits = (
                round((1 - test_split) / val_split) if not custom_splitting_condition else len(condition_array_test)
            )
        else:
            num_splits = round(1 / val_split) if not custom_splitting_condition else len(condition_array_val)
        if not disable_printing:
            print(f"splitting the total number of {ntotal_evts} events using {num_splits}-Fold splitting:")
            for i in range(num_splits):
                if use_testing_dataset:
                    print(
                        f"\tsplit {i+1}: {inputs_train[i].shape[0]} train, {inputs_val[i].shape[0]} validation "
                        f"and {inputs_test[i].shape[0]} test events"
                    )
                else:
                    print(
                        f"\tsplit {i + 1}: {inputs_train[i].shape[0]} train and {inputs_val[i].shape[0]} validation "
                        f"events"
                    )

                if targets_train[i].shape[1] == 1:
                    print(
                        f"\t        train: {inputs_train[i][targets_train[i][:, 0] == 1].shape[0]} signal, "
                        f"{inputs_train[i][targets_train[i][:, 0] == 0].shape[0]} background"
                    )
                    print(
                        f"\t        val: {inputs_val[i][targets_val[i][:, 0] == 1].shape[0]} signal, "
                        f"{inputs_val[i][targets_val[i][:, 0] == 0].shape[0]} background"
                    )
                    if use_testing_dataset:
                        print(
                            f"\t        test: {inputs_test[i][targets_test[i][:, 0] == 1].shape[0]} signal, "
                            f"{inputs_test[i][targets_test[i][:, 0] == 0].shape[0]} background"
                        )
                else:
                    print(
                        f"\t        train: {[inputs_train[i][targets_train[i][:, j] == 1].shape[0] for j in range(targets_train[i].shape[1])]}."
                    )
                    print(
                        f"\t        val: {[inputs_val[i][targets_val[i][:, j] == 1].shape[0] for j in range(targets_val[i].shape[1])]}."
                    )
                    if use_testing_dataset:
                        print(
                            f"\t        test: {[inputs_test[i][targets_test[i][:, j] == 1].shape[0] for j in range(targets_test[i].shape[1])]}."
                        )

    if use_testing_dataset:
        if preprocessor is not None:
            return (
                scaler,
                (inputs_train, inputs_val, inputs_test),
                (targets_train, targets_val, targets_test),
                (weights_train, weights_val, weights_test),
                (normalized_weights_train, normalized_weights_val, normalized_weights_test),
            )
        else:
            return (
                (inputs_train, inputs_val, inputs_test),
                (targets_train, targets_val, targets_test),
                (weights_train, weights_val, weights_test),
                (normalized_weights_train, normalized_weights_val, normalized_weights_test),
            )
    else:
        if preprocessor is not None:
            return (
                scaler,
                (inputs_train, inputs_val),
                (targets_train, targets_val),
                (weights_train, weights_val),
                (normalized_weights_train, normalized_weights_val),
            )
        else:
            return (
                (inputs_train, inputs_val),
                (targets_train, targets_val),
                (weights_train, weights_val),
                (normalized_weights_train, normalized_weights_val),
            )
