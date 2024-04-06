# -*- coding: utf-8 -*-
"""Collection of classes and functions needed to perform the input variable optimization."""

from typing import Union, Optional, Callable
from types import ModuleType

import os
import shutil
import copy
import pickle
import numpy as np
import scipy
import matplotlib.pyplot as plt

import importlib.util

if importlib.util.find_spec("tensorflow") is not None:
    import tensorflow as tf
if importlib.util.find_spec("lightning") is not None:
    import torch.nn.functional

import ray

import OPTIMA.core.training
import OPTIMA.core.model
import OPTIMA.core.evaluation
import OPTIMA.core.tools
import OPTIMA.builtin.inputs
from OPTIMA.core.model import model_config_type


class ShufflerAndPredictor:
    """A class with a single function ``run`` performing the shuffling of variables and calculating the value of the target metric.

    This is also used in `retrain`-mode to calculate the metric values by providing an empty list of input variables
    to shuffle.

    Since both the shuffling and model prediction is to be executed remotely, the class is decorated with a
    ``ray.remote`` decorator, making an instance of this class a `Ray actor`. While this could also be done by only
    defining a function and decorating it, making it a `Ray task`, the worker that is spawned to execute this task
    remains in memory when the task finishes and is reused for the next task. If this task is the training of a
    model (as created in ``perform_crossvalidation``), the ``training_func`` is called, which creates a subprocess
    to perform the training. Since Tensorflow has already been initialized for the worker executing the task
    (because the ``predict``-function of the model was called), this will now hang as Tensorflow is not
    re-initialized in the subprocess but can also not be used from there.

    The solution is to use actors instead of tasks since actors are destroyed when their reference is dropped. Thus,
    between training (in ``perform_crossvalidation``) and prediction (here), the references to all actors are dropped.
    """

    @staticmethod
    def run(
        run_config: ModuleType,
        model_path: str,
        inputs: np.ndarray,
        targets: np.ndarray,
        metric: Callable,
        sample_weights: Optional[np.ndarray] = None,
        indices_vars_to_shuffle: Optional[list[int]] = None,
        num_shuffles: int = 1,
        seed: Optional[int] = None,
        cpus_per_model: int = 1,
        gpus_per_model: int = 0,
    ) -> list[Union[int, float]]:
        """Performs the shuffling of the input features for the given variables and calculates the value of the target metric.

        The indices of the variables to shuffle are taken from ``indices_vars_to_shuffle``. Each corresponding
        input variable is shuffled independently, thus ensuring that each variable is taken from a different event.

        Once the shuffling is done, the model predictions using the shuffled input features, the corresponding
        target labels and the sample weights are provided to ``metric`` to calculate the value of the target metric.

        This procedure is repeated ``num_shuffles`` times.

        In case ``indices_vars_to_shuffle`` is ``None``, i.e. no variables are to be shuffled, only the metric value
        using the provided inputs is calculated.

        Parameters
        ----------
        run_config : ModuleType
            Reference to the imported run-config file.
        model_path : str
            The path to the model to be used for the prediction.
        inputs : np.ndarray
            The array of input features.
        targets : np.ndarray
            The array of target labels.
        metric : Callable
            The callable used to calculate the value of the target metric. It is expected to accept the model
            predictions and target labels as positional arguments and event weights as keyword argument
            ``sample_weights``.
        sample_weights : Optional[np.ndarray]
            Optional event weights to be given to the ``metric``. (Default value = None)
        indices_vars_to_shuffle : Optional[list[int]]
            The list of indices of the input variables that should be shuffled. Each variable is shuffled
            independently. (Default value = None)
        num_shuffles : int
            The number of times the shuffling and calculation of the target metric should be repeated. Only used if
            ``indices_vars_to_shuffle`` is not ``None``. (Default value = 1)
        seed : Optional[int]
            If provided, the seed is used to set the numpy random state before shuffling. (Default value = None)
        cpus_per_model : int
            The number of cpu cores to use for each model. (Default value = 1)
        gpus_per_model : int
            The number of gpus to use for each model. (Default value = 0)

        Returns
        -------
        list[Union[int, float]]
            The list of metric values using the model predictions based on the shuffled input features.
        """
        rng = np.random.RandomState(seed)

        # load the model
        model = OPTIMA.core.model.load_model(run_config, model_path, cpus=cpus_per_model)

        if indices_vars_to_shuffle is not None:
            metrics_after_drop = []
            # repeat n times to average out fluctuations and get a measure for the uncertainty
            for _ in range(num_shuffles):
                # shuffle all entries to be shuffled independently, in a vectorized manner (taken from
                # https://stackoverflow.com/questions/49426584/shuffle-independently-within-column-of-numpy-array)
                inputs_shuffled = copy.copy(inputs)
                idx = rng.rand(*(inputs_shuffled[:, indices_vars_to_shuffle]).shape).argsort(0)
                inputs_shuffled[:, indices_vars_to_shuffle] = inputs_shuffled[:, indices_vars_to_shuffle][
                    idx, np.arange(inputs_shuffled[:, indices_vars_to_shuffle].shape[1])
                ]

                # calculate metric with shuffled inputs
                metrics_after_drop.append(
                    metric(targets, model.predict(inputs_shuffled, verbose=0), sample_weight=sample_weights)
                )
        else:
            # do a normal prediction if nothing is to be shuffled
            metrics_after_drop = [metric(targets, model.predict(inputs, verbose=0), sample_weight=sample_weights)]

        return metrics_after_drop


def get_models_with_inputs(
    models: list[tuple[str, tuple[list, list, list, list]]], input_vars: list[str]
) -> list[tuple[str, list, tuple[ray.ObjectRef, ray.ObjectRef, ray.ObjectRef]]]:
    """Small helper function to grab the validation dataset from the ``models``-list and recombine with the model-path.

    This also saves the list of variables that are used by the model.

    Parameters
    ----------
    models : list[tuple[str, tuple[list, list, list, list]]]
        A list containing a path to the fully trained crossvalidation model and the corresponding lists of split
        input features, target labels, event weights and normalized event weights. Each list entry itself is
        expected to be a list containing the Ray object reference to the numpy array for the training, validation
        and (if used) testing set.
    input_vars : list[str]
        A list containing the name of the input variables used to train the models contained in ``models``.

    Returns
    -------
    list[tuple[str, list, tuple[ray.ObjectRef, ray.ObjectRef, ray.ObjectRef]]]
        For each entry in ``models``, a tuple containing a Ray object reference to the numpy array of input features,
        target labels and normalized event weights of the validation set are returned.
    """
    # grab the inputs we need
    models_with_inputs = []
    for model_path, model_inputs in models:
        inputs_split, targets_split, _, normalized_weights_split = model_inputs
        # we always want to use the validation dataset
        if len(inputs_split) == 2:
            _, inputs = inputs_split
            _, targets = targets_split
            _, normalized_weights = normalized_weights_split
        else:
            _, inputs, _ = inputs_split
            _, targets, _ = targets_split
            _, normalized_weights, _ = normalized_weights_split
        models_with_inputs.append((model_path, input_vars, (inputs, targets, normalized_weights)))
    return models_with_inputs


# helper functions to help with the evaluation of the variable sets and the returned metric values
def evaluate_vars_retrain(
    model_config: model_config_type,
    models_with_inputs: list[tuple[str, list, tuple[ray.ObjectRef, ray.ObjectRef, ray.ObjectRef]]],
    run_config: ModuleType,
    metric: Callable,
    input_handler: OPTIMA.builtin.inputs.InputHandler,
    var_sets_to_try: dict[list],
    training_func: Callable,
    get_actor_pool: Callable,
    delete_actor_pool: Callable,
    num_repeats: int = 1,
    cpus_per_model: int = 1,
    gpus_per_model: int = 0,
    custom_metrics: Optional[list] = None,
    composite_metrics: Optional[list] = None,
    native_metrics: Optional[list] = None,
    weighted_native_metrics: Optional[list] = None,
    rng: Optional[np.random.RandomState] = None,
    temp_output_path: Optional[str] = None,
    save_models_with_inputs: Optional[bool] = False,
) -> dict[str, np.ndarray]:
    """Evaluates the model performance for a given list of input variable sets by retraining the model with the same hyperparameters.

    Since the models are retrained, the results of the evaluation are independent of the baseline models. As such,
    the provided sets of input variables do not need to be subsets of the set of input variables used to train the
    baseline models.

    To perform the training, the ``perform_crossvalidation``-function is called ``num_repeats``-times for each
    provided set of input variables. For each of the trained models, the value of the target metric is calculated.

    For each set of input variables, the `numpy`-array of shape (``num_repeats``, ``num_folds``) is saved in a
    dictionary with the same key as the corresponding input variables set in ``var_sets_to_try``.

    Parameters
    ----------
    model_config : model_config_type
        The model-config of the provided crossvalidation models.
    models_with_inputs : list[tuple[str, list, tuple[ray.ObjectRef, ray.ObjectRef, ray.ObjectRef]]]
        Unused.
    run_config : ModuleType
        A reference to the imported `run-config` file.
    metric : Callable
        The callable used to calculate the value of the target metric. It is expected to accept the model
        predictions and target labels as positional arguments and event weights as keyword argument
        ``sample_weights``.
    input_handler : OPTIMA.builtin.inputs.InputHandler
        An instance of the ``preprocessing.InputHandler``-class.
    var_sets_to_try : dict[list]
        A dictionary containing lists of input variables to evaluate.
    training_func : Callable
        Reference to the function performing the training. This is needed for any evaluation that involves re-training
        the model.
    get_actor_pool : Callable
        Reference to the function to get the pool of ShufflerAndPredictor-actors.
    delete_actor_pool : Callable
        Reference to the function to delete the pool of ShufflerAndPredictor-actors. This is needed to create new
        Ray tasks for the training of the models.
    num_repeats : int
        Number of times each input variable set is evaluated. (Default value = 1)
    cpus_per_model : int
        The number of CPUs to use to train each model. This is given to ``perform_crossvalidation``. (Default value = 1)
    gpus_per_model : int
        The number of GPUs to use to train each model. This is given to ``perform_crossvalidation``. (Default value = 0)
    custom_metrics : Optional[list]
        A list of `custom metrics` as defined in the run-config. (Default value = None)
    composite_metrics : Optional[list]
        A list of `composite metrics` as defined in the run-config. (Default value = None)
    native_metrics : Optional[list]
        A list of native metrics as defined in the run-config. (Default value = None)
    weighted_native_metrics : Optional[list]
        A list of weighted native metrics as defined in the run-config. (Default value = None)
    rng : Optional[np.random.RandomState]
        The numpy random state used to make the execution reproducible. (Default value = None)
    temp_output_path : Optional[str]
        Path to a directory used to save intermediate results. This directory is `not` saved automatically. By default,
        a subdirectory ``'temp'`` of the ``results_folder`` is used. (Default value = None)
    save_models_with_inputs : Optional[bool]
        If ``True``, a ``models_with_inputs``-dictionary is generated for the retrained models of the first
        iteration for each provided set of input variables. It is saved as ``'models_with_inputs_after_drop.pickle``
        to the corresponding subfolder in the temporary directory . (Default value = False)

    Returns
    -------
    dict[str, np.ndarray]
        Dictionary containing the values of the target metric for each trained model for each set of input variables.
        The `numpy`-arrays of shape (``num_repeats``, ``num_folds``) are saved with the same key as the corresponding
        input variables set in ``var_sets_to_try``.
    """
    if weighted_native_metrics is None:
        weighted_native_metrics = []
    if native_metrics is None:
        native_metrics = []
    if composite_metrics is None:
        composite_metrics = []
    if custom_metrics is None:
        custom_metrics = []
    if rng is None:
        rng = np.random.RandomState()
    if temp_output_path is None:
        temp_output_path = "temp"

    # need to delete the actors to free the resources
    delete_actor_pool()

    # iterate over the variables once to start all crossvalidations
    futures_retrain = {}  # this will not only contain futures but also crossvalidation info
    for var_set_key, var_set_to_try in var_sets_to_try.items():
        print(f"\tStarting training for variable set: {var_set_key}")
        futures_retrain[var_set_key] = []
        for it in range(num_repeats):
            # perform crossvalidation with changed input variables: keep config fixed, but select only the set of
            # input variables to try from training dataset and retrain models
            input_handler_after_drop = input_handler.copy()
            input_handler_after_drop.set_vars(var_set_to_try)

            # start the crossvalidation; this will not block until the models are fully trained, instead it will
            # return the futures
            crossval_model_path = os.path.join(temp_output_path, var_set_key, str(it) if num_repeats > 1 else "")
            crossval_model_info, crossval_input_data, futures_varOpt = OPTIMA.core.training.perform_crossvalidation(
                [model_config],
                [crossval_model_path],
                training_func,
                run_config,
                input_handler_after_drop,
                cpus_per_model,
                gpus_per_model,
                custom_metrics,
                composite_metrics,
                native_metrics,
                weighted_native_metrics,
                return_futures=True,
                verbose=0,
                seed=rng.randint(*OPTIMA.core.tools.get_max_seeds()),
            )

            # save the crossvalidation info and the futures
            futures_retrain[var_set_key].append(
                [
                    crossval_model_path,
                    crossval_model_info,
                    crossval_input_data,
                    futures_varOpt,
                ]
            )

    # wait until all trainings are done
    print("\tWaiting for all models to be trained...")
    var_sets_not_finished = list(var_sets_to_try.keys())  # keep track of which var sets are not done yet
    while var_sets_not_finished != []:
        # not simply wait until all var sets are done, instead check each periodically to mark the directory as finished
        # in case the optimization terminates; here we can call ray.get() on all futures since the training is
        # executed using a ray task automatically releases the allocated resources once finished, unlike an actor
        for var_set_key, future_list in futures_retrain.items():
            if var_set_key not in var_sets_not_finished:
                continue
            var_set_done = True
            for crossval_model_path, _, _, f in future_list:
                try:
                    ray.get(f, timeout=0.1)
                except ray.exceptions.GetTimeoutError:
                    var_set_done = False
                    continue

                # when training for this iteration of this var set is done (otherwise we can't get here), mark the
                # folder as done so that it could be resumed should the optimization be killed and remove the var
                # from the list
                open(os.path.join(crossval_model_path, ".crossvalidation_done"), "w").close()

            # this is only True if all iterations of this var set are finished
            if var_set_done:
                var_sets_not_finished.remove(var_set_key)

    print("\tAll models trained, starting evaluation...")

    # once training is done, iterate over all var sets again to perform the evaluation of the trained models
    # need to recreate the actor pool
    actor_pool = get_actor_pool(reuse=False)

    # for the actor pool we need a list of arguments. in order to keep track of which entry in the list of arguments
    # corresponds to which model, we temporarily save the indices in metrics_after_drop
    metrics_after_drop = {}
    args_list = []  # will hold the dictionaries given to the ShufflerAndPredictor's run-function
    for var_set_key in var_sets_to_try.keys():
        metrics_after_drop[var_set_key] = []
        for it in range(num_repeats):
            # get the crossvalidation info
            crossval_model_path, crossval_model_info, crossval_input_data, _ = futures_retrain[var_set_key][it]

            # go through the model_info and input_data and build a list of type [(model_path, inputs), ...], the
            # same type as 'models'
            models_after_drop = []
            for model_info in crossval_model_info[crossval_model_path]:
                models_after_drop.append(
                    (
                        os.path.join(crossval_model_path, model_info["name"]),
                        crossval_input_data[model_info["split"]],
                    )
                )

            # fetch the models and corresponding inputs and perform the inference using one ShufflerAndPredictor each,
            # with indices_vars_to_shuffle = None (default) to disable the shuffling and only do inference.
            models_with_inputs_after_drop = get_models_with_inputs(models_after_drop, var_sets_to_try[var_set_key])
            args_list += [
                {
                    "run_config": run_config,
                    "model_path": model_path,
                    "inputs": inputs,
                    "targets": targets,
                    "metric": metric,
                    "sample_weights": normalized_weights,
                    "cpus_per_model": cpus_per_model,
                    "gpus_per_model": gpus_per_model,
                }
                for model_path, _, (inputs, targets, normalized_weights) in models_with_inputs_after_drop
            ]

            # save the model inputs if requested (only for first iteration since each iteration is equivalent)
            if save_models_with_inputs and it == 0:
                with open(
                    os.path.join(
                        temp_output_path,
                        var_set_key,
                        "0" if num_repeats > 1 else "",
                        "models_with_inputs_after_drop.pickle",
                    ),
                    "wb",
                ) as f:
                    # we want to save the actual data here!
                    pickle.dump(
                        [
                            (
                                model_path,
                                inputs_vars,
                                (ray.get(inputs), ray.get(targets), ray.get(normalized_weights)),
                            )
                            for model_path, inputs_vars, (
                                inputs,
                                targets,
                                normalized_weights,
                            ) in models_with_inputs_after_drop
                        ],
                        f,
                    )

            # save the indices of the arguments for this iteration of this var set in metrics_after_drop
            metrics_after_drop[var_set_key] += [
                len(args_list) - len(models_with_inputs_after_drop) + i
                for i in range(len(models_with_inputs_after_drop))
            ]
    del futures_retrain

    # map the gathered arguments to the actor pool, then save the results in more handy data structure; use the same
    # loops as before to make sure the results are mapped correctly
    results = list(actor_pool.map(lambda a, v: a.run.remote(**v), args_list))
    del args_list
    for var_set_key in var_sets_to_try.keys():
        # need to rearrange the results into lists so that each entry metrics_after_drop[var_set_key] is a list
        # containing the metric values for the num_repeats trys
        results_after_drop = [results[i] for i in metrics_after_drop[var_set_key]]
        num_folds = round(len(results_after_drop) / num_repeats)
        metrics_after_drop[var_set_key] = np.array(results_after_drop).reshape((num_repeats, num_folds)).transpose()

    return metrics_after_drop


def evaluate_vars_shuffle(
    model_config: model_config_type,
    models_with_inputs: list[tuple[str, list, tuple[ray.ObjectRef, ray.ObjectRef, ray.ObjectRef]]],
    run_config: ModuleType,
    metric: Callable,
    input_handler: OPTIMA.builtin.inputs.InputHandler,
    var_sets_to_try: dict[list],
    training_func: Callable,
    get_actor_pool: Callable,
    delete_actor_pool: Callable,
    num_repeats: int = 1,
    cpus_per_model: int = 1,
    gpus_per_model: int = 0,
    custom_metrics: Optional[list] = None,
    composite_metrics: Optional[list] = None,
    native_metrics: Optional[list] = None,
    weighted_native_metrics: Optional[list] = None,
    rng: Optional[np.random.RandomState] = None,
    temp_output_path: Optional[str] = None,
    save_models_with_inputs: Optional[bool] = False,
) -> dict[str, np.ndarray]:
    """Evaluates the model performance for a given list of input variable sets by shuffling the inputs of pretrained models.

    To apply this method, the sets of input variables to try need to be a subset of the set of variables used to
    train the baseline models. The importance of those input variables that are removed is evaluated by shuffling
    the corresponding values in the validation data given in ``models_with_inputs``, performing a prediction using
    the shuffled data and calculating the resulting value of the target metric. This is repeated ``num_repeats``-times
    for each provided set of input variables.

    For each set of input variables, a Ray object reference to the `numpy`-array of shape (``num_repeats``, ``num_folds``)
    is saved in a dictionary with the same key as the corresponding input variables set in ``var_sets_to_try``.

    Parameters
    ----------
    model_config : model_config_type
        Unused.
    models_with_inputs : list[tuple[str, list, tuple[ray.ObjectRef, ray.ObjectRef, ray.ObjectRef]]]
        List containing a tuple containing the path to the saved model and a tuple containing the input features,
        target labels and normalized event weights of the validation set for each fold.
    run_config : ModuleType
        Unused.
    metric : Callable
        The callable used to calculate the value of the target metric. It is expected to accept the model
        predictions and target labels as positional arguments and event weights as keyword argument
        ``sample_weights``.
    input_handler : OPTIMA.builtin.inputs.InputHandler
        Unused.
    var_sets_to_try : dict[list]
        A dictionary containing lists of input variables to evaluate.
    training_func : Callable
        Unused.
    get_actor_pool : Callable
        Reference to the function to get the pool of ShufflerAndPredictor-actors.
    delete_actor_pool : Callable
        Unused.
    num_repeats : int
        Number of times each input variable set is evaluated. (Default value = 1)
    cpus_per_model : int
        Unused. (Default value = 1)
    gpus_per_model : int
        Unused. (Default value = 0)
    custom_metrics : Optional[list]
        Unused. (Default value = None)
    composite_metrics : Optional[list]
        Unused. (Default value = None)
    native_metrics : Optional[list]
        Unused. (Default value = None)
    weighted_native_metrics : Optional[list]
        Unused. (Default value = None)
    rng : Optional[np.random.RandomState]
        The numpy random state used to make the execution reproducible. (Default value = None)
    temp_output_path : Optional[str]
        Unused. (Default value = None)
    save_models_with_inputs : Optional[bool]
        Unused. (Default value = False)

    Returns
    -------
    dict[str, np.ndarray]
        Dictionary containing the values of the target metric for each trained model for each set of input variables.
        The `numpy`-arrays of shape (``num_repeats``, ``num_folds``) are saved with the same key as the corresponding
        input variables set in ``var_sets_to_try``.
    """
    # for the actor pool we need a list of arguments. in order to keep track of which entry in the list of arguments
    # corresponds to which model, we temporarily save the indices in metrics_after_drop
    metrics_after_drop = {}
    args_list = []  # will hold the dictionaries given to the ShufflerAndPredictor's run-function
    for var_set_key, var_set_to_try in var_sets_to_try.items():
        # shuffle the inputs for each pretrained crossvalidation model
        args_list += [
            {
                "run_config": run_config,
                "model_path": model_path,
                "inputs": inputs,
                "targets": targets,
                "metric": metric,
                "sample_weights": normalized_weights,
                "indices_vars_to_shuffle": [i for i in range(len(vars_used)) if vars_used[i] not in var_set_to_try],
                "num_shuffles": num_repeats,
                "seed": rng.randint(*OPTIMA.core.tools.get_max_seeds()),
                "cpus_per_model": cpus_per_model,
                "gpus_per_model": gpus_per_model,
            }
            for model_path, vars_used, (inputs, targets, normalized_weights) in models_with_inputs
        ]

        # save the indices of the arguments for this var to drop in metrics_after_drop
        metrics_after_drop[var_set_key] = [
            len(args_list) - len(models_with_inputs) + i for i in range(len(models_with_inputs))
        ]

    # map the gathered arguments to the actor pool, then save the results in more handy data structure; use the same
    # loops as before to make sure the results are mapped correctly
    actor_pool = get_actor_pool(reuse=True)
    results = list(actor_pool.map(lambda a, v: a.run.remote(**v), args_list))
    del args_list
    for var_set_key in var_sets_to_try.keys():
        # get the results corresponding to the saved indices
        metrics_after_drop[var_set_key] = [results[i] for i in metrics_after_drop[var_set_key]]

    return metrics_after_drop


def _evaluate_metrics_after_drop(
    metrics_after_drop: dict[list],
    metric_op: str,
    baselines: np.ndarray,
    run_config: ModuleType,
) -> tuple[dict]:
    """Calculates averages and normalized averages from the provided metric values for each tried set of input variables.

    Parameters
    ----------
    metrics_after_drop : dict[list]
        Dictionary containing the `numpy`-arrays of shape (``num_repeats``, ``num_folds``) for each set of input
        variables.
    metric_op : str
        Either ``'min'`` or ``'max'``. Denotes if the target metric is to be minimized or maximized.
    baselines : np.ndarray
        The numpy array of baseline metric values used for the normalization.
    run_config : ModuleType
        Reference to the imported run-config file.

    Returns
    -------
    tuple[dict]
        Dictionaries containing the standard deviations and mean values of the metric for each fold, the mean values
        normalized to the corresponding baseline value and their standard deviations for each fold, the average mean
        metric value across all folds and the corresponding uncertainties, the average normalized mean metric values
        across all folds and the corresponding uncertainties and "save" average normalized mean metric values and
        the corresponding uncertainties. The "save" values are calculated from mean values of the metric for each
        fold that are increased (if ``metric_op`` is ``'min'``) or decreased (if ``metric_op`` is ``'max'``) by their
        corresponding standard deviation.
    """
    # TODO: MAD across retries? Everything consistent? Include retries in uncertainty estimate?
    values_after_drop = {}
    uncs_after_drop = {}
    normalized_after_drop = {}
    normalized_safe_after_drop = {}
    avg_metric_after_drop = {}
    unc_metric_after_drop = {}
    avg_normalized_after_drop = {}
    unc_normalized_after_drop = {}
    avg_safe_normalized_after_drop = {}
    unc_safe_normalized_after_drop = {}
    for var_set_key in metrics_after_drop.keys():
        # get the mean metric value and its uncertainty for each variable set across the different number of retries, then
        # calculate a "safe" metric value as mean + unc when minimizing and mean - unc when maximizing. Normalize both
        # mean and safe value to the baseline to get estimates of the relative change for each fold; the safe values are
        # later used for the ranking which metric to drop first
        values = np.mean(metrics_after_drop[var_set_key], axis=1)
        uncs = (
            np.std(metrics_after_drop[var_set_key], axis=1) / np.array(metrics_after_drop[var_set_key]).shape[1]
        )  # uncertainty of the mean!
        safe_values = values + uncs if metric_op == "min" else values - uncs
        normalized_values = values / baselines
        normalized_safe_values = safe_values / baselines
        values_after_drop[var_set_key] = values
        uncs_after_drop[var_set_key] = uncs
        normalized_after_drop[var_set_key] = normalized_values
        normalized_safe_after_drop[var_set_key] = normalized_safe_values

        # now average across the different folds: get the average and average normalized metric value after the drop
        # and the corresponding MADs
        avg_value = np.median(values) if run_config.use_median_for_averages else np.mean(values)
        unc_value = (
            scipy.stats.median_abs_deviation(values) / values.shape[0]  # uncertainty of the mean!
            if run_config.use_median_for_averages
            else np.std(values) / values.shape[0]  # uncertainty of the mean!
        )
        avg_normalized_value = (
            np.median(normalized_values) if run_config.use_median_for_averages else np.mean(normalized_values)
        )
        unc_normalized_value = (
            scipy.stats.median_abs_deviation(normalized_values) / normalized_values.shape[0]  # uncertainty of the mean!
            if run_config.use_median_for_averages
            else np.std(normalized_values) / normalized_values.shape[0]  # uncertainty of the mean!
        )
        avg_safe_normalized_value = (
            np.median(normalized_safe_values) if run_config.use_median_for_averages else np.mean(normalized_safe_values)
        )
        unc_safe_normalized_value = (
            scipy.stats.median_abs_deviation(normalized_safe_values)
            / normalized_safe_values.shape[0]  # uncertainty of the mean!
            if run_config.use_median_for_averages
            else np.std(normalized_safe_values) / normalized_safe_values.shape[0]  # uncertainty of the mean!
        )
        avg_metric_after_drop[var_set_key] = avg_value
        unc_metric_after_drop[var_set_key] = unc_value
        avg_normalized_after_drop[var_set_key] = avg_normalized_value
        unc_normalized_after_drop[var_set_key] = unc_normalized_value
        avg_safe_normalized_after_drop[var_set_key] = avg_safe_normalized_value
        unc_safe_normalized_after_drop[var_set_key] = unc_safe_normalized_value

    return (
        uncs_after_drop,
        values_after_drop,
        normalized_after_drop,
        normalized_safe_after_drop,
        avg_metric_after_drop,
        unc_metric_after_drop,
        avg_normalized_after_drop,
        unc_normalized_after_drop,
        avg_safe_normalized_after_drop,
        unc_safe_normalized_after_drop,
    )


def perform_variable_optimization(
    models: list[tuple[str, tuple[list, list, list, list]]],
    model_config: model_config_type,
    run_config: ModuleType,
    input_handler: OPTIMA.builtin.inputs.InputHandler,
    training_func: Callable,
    target_metric: Optional[str] = None,
    metric_op: str = "min",
    custom_metrics: Optional[list[tuple[str, Callable]]] = None,
    composite_metrics: Optional[list[tuple[str, tuple[str, str], Callable]]] = None,
    native_metrics: Optional[list] = None,
    weighted_native_metrics: Optional[list] = None,
    plots_folder: Optional[str] = None,
    results_folder: Optional[str] = None,
    cpus_per_model: int = 1,
    gpus_per_model: int = 0,
    mode: str = "retrain",
    seed: Optional[int] = None,
) -> list[str]:
    """Performs backwards elimination to optimize the set of input variables.

    By default, each input variable is considered to be independently removable from the dataset. Thus, in each iteration,
    all possible leave-one-out subsets of the full list of input variables of the previous iteration are evaluated. If
    this is not possible, e.g. when all variables of a certain type (all transverse momenta) need to be removed together,
    a ``create_variable_sets_to_try`` needs to be defined in the `run_config`. This function need to take the model-config,
    a list containing the path to the saved crossvalidation models, the list of corresponding input variables and the
    validation datasets (see ``_get_models_with_inputs``). It is expected to return a list containing all lists of
    variables that should be evaluated in this iteration. In the following, the default behaviour is assumed, but all
    explanations are equally valid when not dropping single variables but subsets of the input variables.

    To obtain a baseline for the variable optimization, the `k` pretrained models provided in ``models``, the input
    features, model predictions and sample weights for the validation dataset are given to the target metric. The
    average of the `k` metric values (for the `k` folds) is used as a baseline for the optimization. Depending on
    ``run_config.use_median_for_averages``, the mean or median is used as the average.

    The input variable selection is performed by iteratively removing the least important input variable until a stopping
    condition is reached. The importance of each variable is freshly evaluated each iteration, i.e. the importance of
    each variable does not depend on the result of the previous iteration.

    Which procedure is used to determine the importance of each input variable depends on the value of ``mode``:

    - ``mode`` is set to ``'retrain'``: The importance of an input variable is determined by removing it from the array
      of input features and training `n` times `k` new models with the same hyperparameters. Here, `k` corresponds to
      the `k` folds while `n` corresponds to the number of times the training is repeated for each fold (configurable in
      ``run-config.num_repeats``). Technically, the training is performed by updating the list of input variables to use,
      calling ``perform_crossvalidation`` and providing the ``model_config``. This effectively repeats the crossvalidation
      for a different set of input variables. For each of the `n` times `k` trained models, the input features, model
      prediction and sample weights of the corresponding validation dataset are given to the target metric, resulting in
      `n` metric values for each of the `k` folds and each of the input variables.
    - ``mode`` is set to ``'shuffle'``: The importance of an input variable is determined by shuffling the corresponding
      input feature of the `k` validation datasets and calculating the predictions of the `k` pretrained models given in
      ``models``. Using these predictions, `k` values of the target metric are calculated. This is repeated
      ``run_config.num_repeats``-times, resulting in ``run_config.num_repeats`` metric values for each of the `k`
      pretrained models for each of the input variables. If multiple input variables are dropped (i.e. for iteration two
      or later), all dropped variables are shuffled independently and are therefore `not` taken from the same event.
    - ``mode`` is set to ``'hybrid'``: The ``'shuffle'`` and ``'retrain'`` modes are combined. First, the ``'shuffle'``
      mode is used until the usual termination condition is reached. The optimization is then reverted to either the best
      iteration (if ``run_config.hybrid_revert_to_best_before_switch`` is ``True``) or the last accepted iteration (if
      ``run_config.hybrid_revert_to_best_before_switch`` is ``False``). From this point on, the ``'retrain'`` mode is
      used.
    - ``mode`` is set to ``'custom'`` and an ``evaluate_variable_importance``-function is defined in the `run-config`:
      A user specifiable function is used for the evaluation of variable importance. The signature of this function is
      expected to be the same as ``_evaluate_vars_retrain`` and ``_evaluate_vars_shuffle``.

    In any case, an important variable corresponds to a large degradation of the target metric, thus a relative change
    compared to the baseline values (for each of the `k` folds individually) is used to decide which variable to drop,
    when to stop the optimization and which set of input variables performed best. The mean and the standard deviation
    of the ``run_config.num_repeats`` metric values for the same fold are determined and "safe"-values are calculated
    according to:

    - if ``metric_op`` is ``'min'``: ``save_value`` = mean + std / num_folds
    - if ``metric_op`` is ``'max'``: ``save_value`` = mean - std / num_folds

    The idea is that, since the order in which bad input variables are dropped is not really important, we would rather
    want to drop variables that are more likely bad. Thus, variables with higher uncertainty of the mean metric value
    are kept preferentially since they are more likely to be "less bad".

    For each of the `k` mean metric values / "safe" mean metric values, the relative change with respect to the
    corresponding baseline value is calculated. The average relative change and the corresponding uncertainty are
    calculated using the mean and standard deviation divided by the number of folds, (if
    ``run_config.use_median_for_averages`` is ``False``) or the median and the median absolute deviation divided by the
    number of folds (if ``run_config.use_median_for_averages`` is ``True``). They are plotted for each input variable
    and the plot is saved to ``plots_folder`` as `iteration_i.pdf` for iteration `i`.

    The input variable that resulted in the best average relative change (either the mean or median, depending on
    ``run_config.use_median_for_averages``), i.e. the largest improvement or the smallest degradation, when dropped is
    selected as the candidate input variable to be removed.

    In order to reduce the influence of outliers, a re-evaluation of the candidate input variable is performed if
    ``reevaluate_candidate_to_drop`` is set to ``True`` in the `run-config`. This re-evaluation uses the same evaluation
    method as before unless ``run_config.retrain_for_reevaluation`` is ``True``, in which case the `retrain`-method is
    used. The number of repeats for each variable and fold is specified independent of the main evaluation step via
    ``run_config.num_repeats_for_reevaluation``. This approach therefore also allows to use the computationally cheaper
    `shuffle`-method for the main evaluation and the generally preferable but computationally expensive `retrain`-method
    for the re-evaluation, providing more accurate metric values at the end of each iteration.

    Depending on the combination of evaluation and re-evaluation methods used, the models saved in
    ``models_with_inputs`` potentially need to be updated each iteration to allow the main evaluation of the subsequent
    iteration to be based on the previous iteration instead of the baseline. E.g., if `shuffle` is used for the main
    evaluation and `retrain` is used for the re-evaluation, it is preferable to use the trained models from the
    re-evaluation phase for the next iteration's main evaluation. Otherwise, the importance of each input variable will
    only depend on the initially provided models that were trained with all available inputs. As a result, a significant
    fraction of the inputs of the baseline models may potentially be shuffled together, increasing the chance of
    inaccurate evaluation of variable importance and with that, bad selection of candidate variables to drop. By default,
    ``models_with_inputs`` is only updated if ``retrain_for_reevaluation`` is set to ``True`` in the `run-config`. In
    this case, the iteration 0 of the retraining is used for all folds to update ``models_with_inputs``. This behaviour,
    however, can be overwritten by defining a ``update_model_with_inputs``-function in the `run-config`. This function
    needs to take the `model-config`, the `run-config`, the ``input_handler``, the list of all available input variables,
    a dictionary containing the best set of input variables in this iteration and the temporary output path for the
    re-evaluation as inputs and needs to return the updated ``models_with_inputs``.

    The updated metric values from the re-evaluation are used to decide if the candidate variable should be dropped. If
    no re-evaluation is performed, the original metric values from the main evaluation are used instead. Which condition
    to use for this decision is given by ``run_config.acceptance_criterion``, possible values are:

    - ``run_config.acceptance_criterion`` is set to ``'threshold'``: if the degradation of the target metric with
      respect to the baseline is larger than a threshold, set by ``run_config.max_rel_change``, the iteration is rejected.
    - ``run_config.acceptance_criterion`` is set to ``'improvement'``: if the target metric for the current iteration is
      worse than the best seen value, the iteration is rejected.
    - ``run_config.acceptance_criterion`` is set to ``'degradation'``: if the target metric for the current iteration is
      worse than the best seen value by more than one standard deviation (i.e. the error bars of the current and best
      iteration do not overlap), the iteration is rejected.

    Even if an iteration was rejected, the corresponding input variable is still dropped as long as the number of
    consecutive rejected iterations is less than ``run_config.var_opt_patience``, i.e. in an Early-stopping like manner.
    As soon as ``run_config.var_opt_patience`` consecutive iterations have been rejected, the optimization is terminated.

    Once the optimization has been terminated, two plots are generated showing the evolution of the average metric value
    and the average relative change compared to the baseline as well as the corresponding uncertainties over the course
    of the optimization. They are saved to `optimization_progress.pdf` and `optimization_progress_relativeChange.pdf` in
    the ``plots_folder``, respectively. Again, depending on ``run_config.use_median_for_averages``, either the mean and
    standard deviation or the median and the MAD are used. Additionally, all metric values for all iterations including
    the values from the re-evaluation are saved to `variable_optimization.pickle` in the ``results_folder``.

    Throughout the optimization, the fully trained models for the `retrain`-mode are saved in a folder structure within
    a `temp`-directory in ``results_folder``, allowing the variable optimization to be resumed should it be interrupted.
    This way, only the progress of partially trained models is lost. Similarly, the possible trained models of the
    re-evaluation are saved to a `temp_reevaluation`-directory. At the end of the optimization, both directories and
    their contents are deleted.

    If ``run_config.choose_best_var`` is ``True``, the set of input variables corresponding to the best relative change
    of the target metric compared to the baseline is returned. Otherwise, the final input variable set is returned.

    Parameters
    ----------
    models : list[tuple[str, tuple[list, list, list, list]]]
        A list containing a path to the fully trained crossvalidation model and the corresponding lists of split input
        features, target labels, event weights and normalized event weights. Each list entry itself is expected to be a
        list containing the Ray object reference to the numpy array for the training, validation and (if used) testing set.
    model_config : model_config_type
        The model-config of the provided crossvalidation models.
    run_config : ModuleType
        A reference to the imported `run-config` file.
    input_handler : OPTIMA.builtin.inputs.InputHandler
        An instance of the ``preprocessing.InputHandler``-class
    training_func : Callable
        Reference to the function performing the training. This is needed for any evaluation that involves re-training
        the model.
    target_metric : Optional[str]
        The metric that is to be maximized or minimized. This can either be ``None`` or ``'loss'``, in which case
        binary crossentropy loss is used, or the name of a custom, native or weighted native metric which has to be
        provided in ``custom_metrics``, ``native_metrics`` or ``weighted_native_metrics``. (Default value = None)
    metric_op : str
        Either ``'min'`` or ``'max'``. Specifies if the target metric is to be minimized or maximized. (Default value = 'min')
    custom_metrics : Optional[list[tuple[str, Callable]]]
        A list of `custom metrics` as defined in the run-config. (Default value = None)
    composite_metrics : Optional[list[tuple[str, tuple[str, str], Callable]]]
        A list of `composite metrics` as defined in the run-config. (Default value = None)
    native_metrics : Optional[list]
        A list of native metrics as defined in the run-config. (Default value = None)
    weighted_native_metrics : Optional[list]
        A list of weighted native metrics as defined in the run-config. (Default value = None)
    plots_folder : Optional[str]
        The directory figures are to be saved to. (Default value = None)
    results_folder : Optional[str]
        The directory where the results of the optimization are to be saved to, i.e. the `pickle`-file containing all
        metric values and all temporarily saved models. (Default value = None)
    cpus_per_model : int
        The number of CPUs to use to train each model. This is given to ``perform_crossvalidation``. (Default value = 1)
    gpus_per_model : int
        The number of GPUs to use to train each model. This is given to ``perform_crossvalidation``. (Default value = 0)
    mode : str
        Decides if the `shuffle`, the `retrain` or a `custom` method are used to evaluate the variable importance. (Default value = 'retrain')
    seed : Optional[int]
        If provided, the seed is used to set the numpy random state. This is given to the function that performs the
        evaluation of the variable importance. (Default value = None)

    Returns
    -------
    list[str]
        The optimized list of input variables.
    """
    if weighted_native_metrics is None:
        weighted_native_metrics = []
    if native_metrics is None:
        native_metrics = []
    if composite_metrics is None:
        composite_metrics = []
    if custom_metrics is None:
        custom_metrics = []

    # hybrid mode has two phases, change mode to keep track
    if mode == "hybrid":
        mode = "hybrid_shuffle"

    # create output folder if necessary
    if plots_folder is not None:
        if not os.path.exists(plots_folder):
            os.makedirs(plots_folder)

    # define helper functions to interact with the actor_pool. They are passed to the evaluation function.
    def _get_actor_pool(reuse: Optional[bool] = True) -> ray.util.ActorPool:
        """Small helper function to fetch the ``ShufflerAndPredictor`` actor pool.

        Parameters
        ----------
        reuse : Optional[bool]
            If ``True``, the existing actor pool (if available) is returned. Otherwise, a new pool of actors is
            created. (Default value = True)

        Returns
        -------
        ray.util.ActorPool
            Pool of ``ShufflerAndPredictor``-actors.
        """
        # when not wrapping this in an actor and using a simple task instead, the worker executing the task will stay in
        # memory and is subsequently reused to execute the training; since Tensorflow is already initialized, it cannot be
        # used in the subprocess that is created for the training --> use actors for the prediction instead, they are cleared
        # when their reference is dropped
        ShufflerAndPredictorActor = ray.remote(num_cpus=cpus_per_model, num_gpus=gpus_per_model)(ShufflerAndPredictor)
        try:
            if reuse:
                return actor_pool
            else:
                _delete_actor_pool()
                return ray.util.ActorPool([ShufflerAndPredictorActor.remote() for _ in range(max_num_actors)])
        except NameError:
            # actor_pool does not exist, need to create new one irrelevant of reuse
            return ray.util.ActorPool([ShufflerAndPredictorActor.remote() for _ in range(max_num_actors)])

    def _delete_actor_pool() -> None:
        """Small helper function to delete the `ShufflerAndPredictor`` actor pool if it exists."""
        try:
            nonlocal actor_pool
            del actor_pool
        except NameError:
            return

    def _switch_hybrid_retrain(revert_to_best: bool) -> None:
        """Small helper function to switch from hybrid_shuffle to hybrid_retrain mode and revert the necessary iterations.

        Parameters
        ----------
        revert_to_best : bool
            If ``True``, will revert to the best iteration, otherwise revert to the last accepted iteration.
        """
        nonlocal mode
        nonlocal best_var_sets_per_iteration
        nonlocal best_avg_metric_after_drop_list
        nonlocal best_unc_metric_after_drop_list
        nonlocal best_avg_normalized_after_drop_list
        nonlocal best_unc_normalized_after_drop_list
        nonlocal metrics_after_drop_list
        nonlocal iteration
        nonlocal last_accepted_iteration

        # switch mode
        mode = "hybrid_retrain"

        # set the iteration to revert to
        if revert_to_best:
            revert_iteration = best_iteration
            last_accepted_iteration = best_iteration
        else:
            revert_iteration = last_accepted_iteration

        # revert all iterations since revert_iteration
        best_var_sets_per_iteration = best_var_sets_per_iteration[: revert_iteration + 1]
        best_avg_metric_after_drop_list = best_avg_metric_after_drop_list[: revert_iteration + 1]
        best_unc_metric_after_drop_list = best_unc_metric_after_drop_list[: revert_iteration + 1]
        best_avg_normalized_after_drop_list = best_avg_normalized_after_drop_list[: revert_iteration + 1]
        best_unc_normalized_after_drop_list = best_unc_normalized_after_drop_list[: revert_iteration + 1]
        metrics_after_drop_list = metrics_after_drop_list[:revert_iteration]  # this does not include the baseline
        iteration = revert_iteration

    # get the callable and comparator
    if target_metric is None or target_metric == "loss":
        # TODO: generalize to the actual model loss!
        target_metric = "loss"
        metric_op = "min"
        if run_config.model_type == "Keras":
            bce = tf.keras.losses.BinaryCrossentropy()
            metric = lambda y_true, y_pred, sample_weight=None: bce(y_true, y_pred, sample_weight=sample_weight).numpy()
        elif run_config.model_type == "Lightning":
            metric = lambda y_true, y_pred, sample_weight=None: torch.nn.functional.binary_cross_entropy(
                torch.from_numpy(y_pred).type(torch.float),
                torch.from_numpy(y_true.copy()).type(torch.float),
                weight=torch.from_numpy(sample_weight.reshape((-1, 1)).copy()).type(torch.float),
            ).numpy()
    elif target_metric in [m[0] for m in custom_metrics]:
        for key, custom_metric in custom_metrics:
            if key == target_metric:
                metric = custom_metric
                break
    elif target_metric in [m[0] for m in native_metrics + weighted_native_metrics]:
        for key, native_metric in native_metrics + weighted_native_metrics:
            if key == target_metric:
                # for native metrics, we need to use the wrapper to use stateful metrics
                metric = lambda y_true, y_pred, sample_weight=None, metric=native_metric: OPTIMA.core.evaluation.calc_native_metric(
                    run_config, metric[0](**metric[1]), y_true, y_pred, sample_weight=sample_weight
                )
                break
    else:
        raise ValueError(f"Unknown target metric: {target_metric}")

    # set the numpy random state
    rng = np.random.RandomState(seed)

    # create pool of ShufflerAndPredictor-actors
    cluster_resources = ray.cluster_resources()
    cluster_cpus = cluster_resources.get("CPU")
    cluster_gpus = cluster_resources.get("GPU")
    max_num_actors = int(
        min(
            cluster_cpus // cpus_per_model if cpus_per_model > 0 else np.inf,
            cluster_gpus // gpus_per_model if gpus_per_model > 0 else np.inf,
        )
    )
    actor_pool = _get_actor_pool()

    # calculate baseline
    # throughout the variable optimization, models_with_inputs contains the baseline models with corresponding list of
    # input variables and the validation dataset for all crossvalidation folds. If the baseline model is not updated,
    # i.e. if the evaluation method used in a potential re-evaluation step does not perform a retraining, this variable
    # is not touched. Otherwise, an updated path to the model files, updated list of input variables and the updated
    # validation datasets are saved. While this updating is not needed for all evaluation methods (it is e.g. not
    # necessary for the retrain method), all methods that don't create new models need the updated baseline models,
    # otherwise each evaluation will not use the previous iteration as its baseline.
    models_with_inputs = get_models_with_inputs(models, input_handler.get_vars())
    baseline_args = [
        {
            "run_config": run_config,
            "model_path": model_path,
            "inputs": inputs,
            "targets": targets,
            "metric": metric,
            "sample_weights": normalized_weights,
            "cpus_per_model": cpus_per_model,
            "gpus_per_model": gpus_per_model,
        }
        for model_path, _, (inputs, targets, normalized_weights) in models_with_inputs
    ]
    baselines = np.array(list(actor_pool.map(lambda a, v: a.run.remote(**v), baseline_args)))[:, 0]
    avg_baseline = np.median(baselines) if run_config.use_median_for_averages else np.mean(baselines)
    unc_baseline = (
        scipy.stats.median_abs_deviation(baselines) / baselines.shape[0]
        if run_config.use_median_for_averages
        else np.std(baselines) / baselines.shape[0]
    )

    baseline_rounded, baseline_unc_rounded = OPTIMA.core.evaluation.scientific_rounding(avg_baseline, unc_baseline)
    print(f"Baseline: {baseline_rounded} +- {baseline_unc_rounded} \t ([{baselines}])")

    # get the list of variables
    all_vars = input_handler.get_vars()

    # these will contain the best variable sets for each iteration and the best overall variable set tried so far as
    # lists of tuples of type (var_set_key, var_set)
    best_var_sets_per_iteration = [("baseline", all_vars)]
    best_var_set = ("baseline", all_vars)
    last_accepted_var_set = ("baseline", all_vars)

    # keep track of the current and best iterations
    iteration = 1
    best_iteration = 0
    best_normalized = 1.0
    unc_best_normalized = 0.0
    last_accepted_iteration = 0

    # lists containing the average metric value and uncertainty for the best variable set in each iteration;
    # used for the final progression plot
    best_avg_metric_after_drop_list = [avg_baseline]
    best_unc_metric_after_drop_list = [unc_baseline]
    best_avg_normalized_after_drop_list = [1.0]
    best_unc_normalized_after_drop_list = [0.0]
    metrics_after_drop_list = (
        []
    )  # will contain all the data without processing and is saved to disk for later evaluation

    # do the iterative optimization
    while len(best_var_sets_per_iteration[-1][1]) > 1:
        vars_dropped = [var_set_key for var_set_key, _ in best_var_sets_per_iteration[1:]]
        print(
            "Iteration {}, dropped variables: {}".format(
                iteration, ", ".join(vars_dropped) if len(vars_dropped) > 0 else "None"
            )
        )

        # create the dictionary of variable lists that should be evaluated. if the create_variable_sets_to_try-function is not
        # defined in the run_config, a leave-one-out stategy is used to create all possible subsets with exactly one
        # variable removed. The corresponding key is only used to identify the variable set.
        vars_remaining = best_var_sets_per_iteration[-1][
            1
        ]  # the variable set of the last iteration is the current variable set
        if hasattr(run_config, "create_variable_sets_to_try"):
            var_sets_to_try = run_config.create_variable_sets_to_try(
                model_config, models_with_inputs, metric, all_vars, vars_remaining
            )
        else:
            var_sets_to_try = {
                var_to_drop: [var for var in vars_remaining if var != var_to_drop] for var_to_drop in vars_remaining
            }

        # it may be that create_variable_sets_to_try does not allow some variables to be dropped. Thus, it is possible
        # that best_var_sets_per_iteration[-1][1], i.e. the best variable set of the previous iteration, still contains
        # more than one variable, but create_variable_sets_to_try does not return variable sets to evaluate.
        if len(var_sets_to_try) == 0:
            print("No more variable sets to evaluate. Terminating the variable optimization...")
            break

        # perform the evaluation for the created list of variable lists
        if mode == "custom" and hasattr(run_config, "evaluate_variable_importance"):
            print("Evaluating variable sets using method: custom")
            evaluate_vars = run_config.evaluate_variable_importance
            output_prefix = "custom"
        elif mode == "retrain" or mode == "hybrid_retrain":
            print(
                "Evaluating variable sets using method: retrain" + " (hybrid mode, phase 2)"
                if mode == "hybrid_retrain"
                else ""
            )
            evaluate_vars = evaluate_vars_retrain
            output_prefix = "retrain"
        elif mode == "shuffle" or mode == "hybrid_shuffle":
            print(
                "Evaluating variable sets using method: shuffle" + " (hybrid mode, phase 1)"
                if mode == "hybrid_shuffle"
                else ""
            )
            evaluate_vars = evaluate_vars_shuffle
            output_prefix = "shuffle"

        metrics_after_drop = evaluate_vars(
            model_config,
            models_with_inputs,
            run_config,
            metric,
            input_handler,
            var_sets_to_try,
            training_func,
            _get_actor_pool,
            _delete_actor_pool,
            run_config.num_repeats
            if mode != "hybrid_retrain"
            else run_config.num_repeats_hybrid_retrain,  # need two values in hybrid mode
            cpus_per_model,
            gpus_per_model,
            custom_metrics,
            composite_metrics,
            native_metrics,
            weighted_native_metrics,
            rng,
            temp_output_path=os.path.join(results_folder, "temp", f"{output_prefix}_iteration_{iteration}"),
        )

        # go through the returned metric values after the variable drop and calculate useful average metric values.
        # First get the mean and std of the metric for each variable set across the different number of retries, then
        # calculate a "safe" metric value as mean + std when minimizing and mean - std when maximizing. Normalize both
        # mean and safe value to the baseline to get estimates of the relative change for each fold; the safe values are
        # later used for the ranking which metric to drop first. Finally, average across the different folds to get
        # average and average normalized metric values und corresponding uncertainties.
        (
            _,
            means_after_drop,
            normalized_after_drop,
            normalized_safe_after_drop,
            avg_metric_after_drop,
            unc_metric_after_drop,
            avg_normalized_after_drop,
            unc_normalized_after_drop,
            avg_safe_normalized_after_drop,
            unc_safe_normalized_after_drop,
        ) = _evaluate_metrics_after_drop(metrics_after_drop, metric_op, baselines, run_config)
        for var_set_key in metrics_after_drop.keys():
            # round the values for output
            avg_normalized_values_rounded, unc_normalized_values_rounded = OPTIMA.core.evaluation.scientific_rounding(
                avg_normalized_after_drop[var_set_key], unc_normalized_after_drop[var_set_key]
            )
            avg_mean_rounded, unc_mean_rounded = OPTIMA.core.evaluation.scientific_rounding(
                avg_metric_after_drop[var_set_key], unc_metric_after_drop[var_set_key]
            )
            print(
                f"\tnormalized {target_metric} when dropping {var_set_key}: {avg_normalized_values_rounded} +- "
                f"{unc_normalized_values_rounded}, raw {target_metric}: {avg_mean_rounded} +- {unc_mean_rounded} \t "
                f"([{', '.join([str(s) for s in normalized_after_drop[var_set_key]])}]"
                f" & [{', '.join([str(s) for s in means_after_drop[var_set_key]])}])"
            )

        # go through the normalized safe values and find the input variable with the best change after dropping; we are
        # using the safe values for the ranking because we would keep a variable with a slightly worse mean but much
        # higher uncertainty because it has a higher chance to make an improvement
        get_best = min if metric_op == "min" else max
        best_var_set_iteration_key = get_best(avg_safe_normalized_after_drop, key=avg_safe_normalized_after_drop.get)

        # plot the results for this iteration
        fig, ax = plt.subplots(figsize=[8, 6], layout="constrained")
        ax.errorbar(
            list(var_sets_to_try.keys()),
            [avg_normalized_after_drop[var_set_key] - 1.0 for var_set_key in var_sets_to_try.keys()],
            yerr=[unc_normalized_after_drop[var_set_key] for var_set_key in var_sets_to_try.keys()],
            fmt="o",
            zorder=1,
        )
        ax.axhline(y=0, color="r", linestyle="--", label="baseline", zorder=0)
        if iteration > 1:
            ax.axhline(
                y=best_avg_normalized_after_drop_list[best_iteration] - 1.0,
                color="g",
                linestyle="--",
                label="best",
                zorder=0,
            )
        ax.plot(
            best_var_set_iteration_key,
            avg_normalized_after_drop[best_var_set_iteration_key] - 1.0,
            marker="x",
            markersize=10,
            color="r",
            zorder=2,
        )
        ax.set_xticks(range(len(list(var_sets_to_try.keys()))), list(var_sets_to_try.keys()), rotation="vertical")
        ax.set_title(f"change of {target_metric} value after var. drop relative to baseline")
        ax.legend()
        fig.savefig(os.path.join(plots_folder, f"{output_prefix}_iteration_{iteration}.pdf"))

        if run_config.reevaluate_candidate_to_drop:
            # reevaluate the best set of variables to get an unbiased estimate (because for a high number of redundant
            # variables, the best performing variable set can be expected to be an outlier)
            print(f"Re-evaluating {best_var_set_iteration_key}...")
            if run_config.retrain_for_reevaluation:
                # reevaluate by retraining; this allows to use the shuffle method to select unimportant variables but use
                # retraining to estimate the performance of the corresponding variable set
                reevaluate_vars = evaluate_vars_retrain
            else:
                # reevaluate with original evaluation method
                reevaluate_vars = evaluate_vars

            metrics_best_var_set_iteration = reevaluate_vars(
                model_config,
                models_with_inputs,
                run_config,
                metric,
                input_handler,
                {best_var_set_iteration_key: var_sets_to_try[best_var_set_iteration_key]},
                training_func,
                _get_actor_pool,
                _delete_actor_pool,
                run_config.num_repeats_for_reevaluation,
                cpus_per_model,
                gpus_per_model,
                custom_metrics,
                composite_metrics,
                native_metrics,
                weighted_native_metrics,
                rng,
                temp_output_path=os.path.join(
                    results_folder, "temp_reevaluation", f"{output_prefix}_iteration_{iteration}"
                ),
                save_models_with_inputs=True,
            )

            # we don't need the metric values as a dictionary here since only a single entry will be contained anyway
            (
                _,
                means_best_var_set_iteration,
                normalized_best_var_set_iteration,
                _,
                avg_metric_best_var_set_iteration,
                unc_metric_best_var_set_iteration,
                avg_normalized_best_var_set_iteration,
                unc_normalized_best_var_set_iteration,
                _,
                _,
            ) = [
                d[best_var_set_iteration_key]
                for d in _evaluate_metrics_after_drop(metrics_best_var_set_iteration, metric_op, baselines, run_config)
            ]
            metrics_after_drop[best_var_set_iteration_key + "_reevaluated"] = metrics_best_var_set_iteration[
                best_var_set_iteration_key
            ]

            # print the re-evaluated results
            (
                avg_normalized_best_var_set_iteration_rounded,
                unc_normalized_best_var_set_iteration_rounded,
            ) = OPTIMA.core.evaluation.scientific_rounding(
                avg_normalized_best_var_set_iteration, unc_normalized_best_var_set_iteration
            )
            (
                avg_metric_best_var_set_iteration_rounded,
                unc_avg_metric_best_var_set_iteration_rounded,
            ) = OPTIMA.core.evaluation.scientific_rounding(
                avg_metric_best_var_set_iteration, unc_metric_best_var_set_iteration
            )
            print(
                f"\tRe-evaluation: normalized {target_metric} when dropping {best_var_set_iteration_key}: "
                f"{avg_normalized_best_var_set_iteration_rounded} +- {unc_normalized_best_var_set_iteration_rounded}, "
                f"raw {target_metric}: {avg_metric_best_var_set_iteration_rounded} +- {unc_avg_metric_best_var_set_iteration_rounded} "
                f"\t ([{', '.join([str(s) for s in normalized_best_var_set_iteration])}]"
                f" & [{', '.join([str(s) for s in means_best_var_set_iteration])}])"
            )

            # once the reevaluation of the best variable set is done, we potentially need to update the models_with_inputs
            # for the next iteration. This depends on the method used to evaluate the variable sets and thus needs to be
            # customizable.
            if hasattr(run_config, "update_models_with_inputs"):
                models_with_inputs = run_config.update_models_with_inputs(
                    run_config,
                    model_config,
                    input_handler,
                    all_vars,
                    {best_var_set_iteration_key: var_sets_to_try[best_var_set_iteration_key]},
                    output_path_evaluation=os.path.join(
                        results_folder, "temp_reevaluation", f"{output_prefix}_iteration_{iteration}"
                    ),
                )
            elif run_config.retrain_for_reevaluation:
                # preferably we should choose the most "average" retry iteration, but for simplicity we just take
                # iteration 0. This has already been saved for us by _evaluate_vars_retrain
                # TODO: use most "average" iteration instead?
                with open(
                    os.path.join(
                        results_folder,
                        "temp_reevaluation",
                        f"{output_prefix}_iteration_{iteration}",
                        best_var_set_iteration_key,
                        "0" if run_config.num_repeats_for_reevaluation > 1 else "",
                        "models_with_inputs_after_drop.pickle",
                    ),
                    "rb",
                ) as f:
                    models_with_inputs = pickle.load(f)
        else:
            avg_metric_best_var_set_iteration = avg_metric_after_drop[best_var_set_iteration_key]
            unc_metric_best_var_set_iteration = unc_metric_after_drop[best_var_set_iteration_key]
            avg_normalized_best_var_set_iteration = avg_normalized_after_drop[best_var_set_iteration_key]
            unc_normalized_best_var_set_iteration = unc_normalized_after_drop[best_var_set_iteration_key]

        # add variable that should be dropped next to list of dropped variables
        best_var_sets_per_iteration.append((best_var_set_iteration_key, var_sets_to_try[best_var_set_iteration_key]))

        # update the progress lists with the average metric / normalized metric and uncertainty values
        best_avg_metric_after_drop_list.append(avg_metric_best_var_set_iteration)
        best_unc_metric_after_drop_list.append(unc_metric_best_var_set_iteration)
        best_avg_normalized_after_drop_list.append(avg_normalized_best_var_set_iteration)
        best_unc_normalized_after_drop_list.append(unc_normalized_best_var_set_iteration)

        # add this iteration's metrics after drop dict to the list
        metrics_after_drop_list.append(metrics_after_drop)

        # print the results
        rounded_values = OPTIMA.core.evaluation.scientific_rounding(
            avg_normalized_best_var_set_iteration, unc_normalized_best_var_set_iteration
        )
        print(
            f"  --> Dropped {best_var_set_iteration_key}, normalized {target_metric}: {rounded_values[0]} +- {rounded_values[1]}"
        )

        # check if we should accept this iteration. The criterion used here depends on the chosen termination condition
        # set in the run_config. Possible values are:
        # - threshold: if the normalized metric value shows a degradation compared to the baseline of more than
        #              run_config.max_rel_change, the iteration is rejected.
        # - improvement: if the normalized metric value has not improved compared to the best value, the iteration is
        #                rejected.
        # - degradation: if the normalized metric value shows a degradation compared to the best value of more than
        #                unc_normalized_best_var_set_iteration, the iteration is rejected.
        accept = True
        if run_config.acceptance_criterion == "threshold":
            if (1.0 if metric_op == "min" else -1.0) * (
                avg_normalized_best_var_set_iteration - 1
            ) > run_config.max_rel_change:
                accept = False
                reject_reason = (
                    f"Best normalized {target_metric} {avg_normalized_best_var_set_iteration} "
                    f"{'>' if metric_op == 'min' else '<'} "
                    f"{(1 + run_config.max_rel_change) if metric_op == 'min' else (1 - run_config.max_rel_change)}."
                )
        elif run_config.acceptance_criterion == "improvement":
            if avg_normalized_best_var_set_iteration != get_best(
                [best_normalized, avg_normalized_best_var_set_iteration]
            ):
                accept = False
                reject_reason = (
                    f"{target_metric} did not improve with respect to iteration {best_iteration}, "
                    f"{avg_normalized_best_var_set_iteration} {'>' if metric_op == 'min' else '<'} {best_normalized}."
                )
        elif run_config.acceptance_criterion == "degradation":
            if metric_op == "min":
                adjusted_avg_normalized_best_var_set_iteration = (
                    avg_normalized_best_var_set_iteration - unc_normalized_best_var_set_iteration
                )
                adjusted_best_normalized = best_normalized + unc_best_normalized
            else:
                adjusted_avg_normalized_best_var_set_iteration = (
                    avg_normalized_best_var_set_iteration + unc_normalized_best_var_set_iteration
                )
                adjusted_best_normalized = best_normalized - unc_best_normalized
            if adjusted_avg_normalized_best_var_set_iteration != get_best(
                [adjusted_best_normalized, adjusted_avg_normalized_best_var_set_iteration]
            ):
                accept = False
                reject_reason = (
                    f"{target_metric} degraded by more than 1 standard deviation with respect to iteration "
                    f"{best_iteration}, {avg_normalized_best_var_set_iteration} {'-' if metric_op == 'min' else '+'} "
                    f"{unc_normalized_best_var_set_iteration} {'>' if metric_op == 'min' else '<'} "
                    f"{best_normalized} {'+' if metric_op == 'min' else '-'} {unc_best_normalized}."
                )

        if accept:
            # update the last accepted values
            last_accepted_iteration = iteration
            last_accepted_var_set = (best_var_set_iteration_key, var_sets_to_try[best_var_set_iteration_key])

            # check if best variable set in this iteration should be used as best_var_set
            if avg_normalized_best_var_set_iteration == get_best(
                [best_normalized, avg_normalized_best_var_set_iteration]
            ):
                best_normalized = avg_normalized_best_var_set_iteration
                unc_best_normalized = unc_normalized_best_var_set_iteration
                best_iteration = iteration
                best_var_set = (best_var_set_iteration_key, var_sets_to_try[best_var_set_iteration_key])
        else:
            print(
                f"  --> Iteration did not pass acceptance criterion: {reject_reason} "
                f"({int(iteration - last_accepted_iteration)} / {run_config.var_opt_patience})"
            )

            # check early stopping
            if iteration - last_accepted_iteration >= run_config.var_opt_patience:
                # do not terminate if in hybrid shuffle mode, instead switch to phase 2 (retrain)
                if mode == "hybrid_shuffle":
                    print(
                        f"Reverting to iteration {best_iteration if run_config.hybrid_revert_to_best_before_switch else last_accepted_iteration}"
                        f" and switching to retrain mode."
                    )
                    _switch_hybrid_retrain(revert_to_best=run_config.hybrid_revert_to_best_before_switch)
                else:
                    print("  --> Terminating...")
                    break

        iteration += 1

    # dump the raw metric values and terminate
    with open(os.path.join(results_folder, "variable_optimization.pickle"), "wb") as f:
        pickle.dump((baselines, metrics_after_drop_list), f)

    # need to delete the actors to free the resources
    _delete_actor_pool()

    # delete the temp folders
    if os.path.exists(os.path.join(results_folder, "temp")):
        shutil.rmtree(os.path.join(results_folder, "temp"))
    if os.path.exists(os.path.join(results_folder, "temp_reevaluation")):
        shutil.rmtree(os.path.join(results_folder, "temp_reevaluation"))

    # choose which iteration to return
    target_iteration = best_iteration if run_config.choose_best_var_set else last_accepted_iteration
    target_var_set = best_var_set if run_config.choose_best_var_set else last_accepted_var_set

    # TODO: need to handle hybrid mode in progress plots!
    # generate an overview plot for the metric and normalized metric values for each iteration
    # metric value
    fig, ax = plt.subplots(figsize=[8, 6], layout="constrained")
    vars_dropped = [var_set_key for var_set_key, _ in best_var_sets_per_iteration[1:]]
    ax.errorbar(
        ["baseline"] + vars_dropped,
        best_avg_metric_after_drop_list,
        yerr=best_unc_metric_after_drop_list,
        fmt="o",
        zorder=0,
    )
    ax.set_xticks(range(len(["baseline"] + vars_dropped)), ["baseline"] + vars_dropped, rotation="vertical")
    ax.plot(
        target_var_set[0],
        best_avg_metric_after_drop_list[target_iteration],
        marker="x",
        markersize=10,
        color="r",
        zorder=1,
    )
    ax.set_title(f"{target_metric} value after variable drop")
    fig.savefig(os.path.join(plots_folder, "optimization_progress.pdf"))

    # normalized metric value
    fig, ax = plt.subplots(figsize=[8, 6], layout="constrained")
    ax.errorbar(
        ["baseline"] + vars_dropped,
        [v - 1.0 for v in best_avg_normalized_after_drop_list],
        yerr=best_unc_normalized_after_drop_list,
        fmt="o",
        zorder=0,
    )
    ax.set_xticks(range(len(["baseline"] + vars_dropped)), ["baseline"] + vars_dropped, rotation="vertical")
    ax.plot(
        target_var_set[0],
        best_avg_normalized_after_drop_list[target_iteration] - 1.0,
        marker="x",
        markersize=10,
        color="r",
        zorder=1,
    )
    ax.set_title(f"change of {target_metric} value after var drop relative to baseline")
    fig.savefig(os.path.join(plots_folder, "optimization_progress_relativeChange.pdf"))

    # return the optimized variable set
    return target_var_set[1]
