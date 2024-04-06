# -*- coding: utf-8 -*-
"""A module that provides functions to handle the search space for the hyperparameter optimization for the build-in multilayer perceptrons."""
from types import ModuleType
from typing import Any

from ray import tune

from OPTIMA.core.search_space import tune_search_space_type, run_config_to_tune_converter
from OPTIMA.core.model import model_config_type


def get_hp_defaults() -> model_config_type:
    """Provides a dictionary of default values for all hyperparameters supported (and thus needed) by the built-in ``build``-function.

    This function is specific to the built-in ``build``-function for classification using multilayer perceptrons. It can
    be overwritten by defining a ``get_hp_defaults``-function in the run-config.

    This function's output is only used if the built-in ``build``-function is used or if a ``build_search_space``-function
    is defined in the `run-config`. If this is not the case, the hyperparameter defaults are ignored.

    Returns
    -------
    model_config_type
        Dictionary with the names of all hyperparameters as keys and the corresponding default values as values.
    """
    # WARNING: when adding new hyperparameters, make sure to also clip the maximum allowed ranges in
    # OptimizationTools.limit_and_round_hps() because the mutations in PBT are not guaranteed to stay inside the
    # specified ranges!
    hyperparameter_defaults = {
        "num_layers": 3,
        "units": 32,
        "activation": "swish",
        "kernel_initializer": "auto",
        "bias_initializer": "auto",
        "l1_lambda": 0.0,
        "l2_lambda": 0.0,
        "dropout": 0.1,
        "batch_size": 64,
        "learning_rate": 0.001,
        "Adam_beta_1": 0.9,
        "one_minus_Adam_beta_2": 0.001,
        "Adam_epsilon": 1e-7,
        "loss_function": "BinaryCrossentropy",
    }
    return hyperparameter_defaults


def build_search_space(hyperparameter_defaults: dict[str, Any], run_config: ModuleType) -> tune_search_space_type:
    """Builds the search space required for `Tune` from the defaults-dictionary and the ``search_space`` defined in the run-config.

    This function is a wrapper around the ``run_config_to_tune_converter``-function to handle special cases specific to the
    built-in ``build``-function for classification using multilayer perceptrons. It is optional and can be overwritten by
    defining a ``build_search_space``-function in the run-config. If a custom ``build``-function is used and this function
    is not overwritten, the ``run_config_to_tune_converter``-function will be called directly, thus disabling any MLP
    specific behaviour.

    The search space is built by iterating over the hyperparameter defaults provided in hyperparameter_defaults. If the
    hyperparameter is one of the keys in ``run_config.search_space``, the corresponding value is given to the
    ``run_config_to_tune_converter``-function to build the search space entry. If it is not present in
    ``run_config.search_space``, the default value given in ``hyperparameter_defaults`` is used. An exception to this are
    the hyperparameters ``'loss_function'`` and ``'units'``.

    For the hyperparameter ``'loss_function'``, the value ``'all'`` is valid in addition to the names of the supported loss
    functions and will be replaced with a list of all built-in loss functions.

    In order to handle varying numbers of neurons per layer, an ``'optimize_units_per_layer'``-option is expected in the
    run-config. It decides if all layers should be of the same size (i.e. only a single hyperparameter, named ``'units'``)
    or if the number of neurons should be a separate hyperparameter for each individual layer (named ``'units_i'`` for
    layer `i`). The following cases are distinguished:

    - ``optimize_units_per_layer`` is ``False``: a single hyperparameter ``'units'`` is sufficient and is treated like a
      normal hyperparameter.
    - ``optimize_units_per_layer`` is ``True`` and ``'units'`` is present in ``run_config.search_space.keys()``: a
      seperate hyperparameter ``'units_i'`` will be created for each layer, the same search space is used for each of
      them. The maximum number of layers that are possible (and thus how many hyperparameters need to be created) is
      inferred from the ``'num_layers'`` hyperparameter.
    - ``optimize_units_per_layer`` is ``True`` and ``'units'`` is not present in ``run_config.search_space.keys()``: two
      cases are distinguished:
        - at least one key in ``run_config.search_space`` contains ``'units'``: the expressions provided in
          ``run_config.search_space`` for any hyperparameter containing ``'units'`` is given to the
          ``run_config_to_tune_converter``-function and added to the search space. No sanity checks regarding the name
          of the hyperparameter or the correct number of hyperparameters is made.
        - none of the keys in ``run_config.search_space`` contain ``'units'``: a single hyperparameter ``'units'`` with
          the corresponding default value provided in ``hyperparameter_defaults`` is added to the search space.

    Parameters
    ----------
    hyperparameter_defaults : dict[str, Any]
        Dictionary containing the default values for all supported hyperparameters.
    run_config : ModuleType
        Reference to the imported run-config file.

    Returns
    -------
    tune_search_space_type
        Dictionary containing a `Tune`-compatible search space entry (or a fixed value) for each supported hyperparameter.
    """
    # go through search_space dict in config and build search space
    search_space = {}
    for hp in hyperparameter_defaults.keys():
        if hp == "units":
            continue  # will take care of units later
        if hp in run_config.search_space.keys():
            # for 'loss_function', the value could be 'all', in which case we set it to a list of all available loss functions
            if hp == "loss_function" and run_config.search_space[hp] == "all":
                loss_function_list = ["BinaryCrossentropy", "CategoricalCrossentropy", "KLDivergence"]
                search_space[hp] = run_config_to_tune_converter(loss_function_list)
            else:
                search_space[hp] = run_config_to_tune_converter(run_config.search_space[hp])
        else:
            search_space[hp] = hyperparameter_defaults[hp]

    # need to add units separately since the number of parameters potentially depends on the maximum number of layers
    # first check if the number of units in each layer should be optimized separately, but the ranges for each layer are the same
    if run_config.optimize_units_per_layer and "units" in run_config.search_space.keys():
        if isinstance(search_space["num_layers"], int) or isinstance(search_space["num_layers"], float):
            max_num_layers = search_space["num_layers"]
        elif isinstance(search_space["num_layers"], tune.search.sample.Categorical):
            max_num_layers = max(
                run_config.search_space["num_layers"]
            )  # default values will never be lists --> this must be defined in the config
        else:
            max_num_layers = run_config.search_space["num_layers"][2]
        for i in range(1, max_num_layers + 1):
            search_space["units_" + str(i)] = run_config_to_tune_converter(run_config.search_space["units"])

    # next check if each layer should be optimized separately and the range for each layer is different (can also be a fixed value)
    elif run_config.optimize_units_per_layer:
        units_i_in_conf = False
        # we assume that the user specified entries for sufficiently many layers, we won't check that here
        for hp in run_config.search_space.keys():
            if "units" in hp:
                units_i_in_conf = True
                search_space[hp] = run_config_to_tune_converter(run_config.search_space[hp])
        # if user did not specify units or units_i, set fixed default units for each layer
        if not units_i_in_conf:
            search_space["units"] = hyperparameter_defaults["units"]
    # next, check if each layer should have the same size and the range is specified by the user
    elif "units" in run_config.search_space.keys():
        search_space["units"] = run_config_to_tune_converter(run_config.search_space["units"])
    # if none of the above, use default value for all layers
    else:
        search_space["units"] = hyperparameter_defaults["units"]

    # finally, add any remaining search_space entries
    for hp in run_config.search_space.keys():
        if hp not in search_space.keys() and hp != "units":
            search_space[hp] = run_config_to_tune_converter(run_config.search_space[hp])

    return search_space


def prepare_search_space_for_PBT(
    search_space: tune_search_space_type, replacements_dict: model_config_type
) -> tune_search_space_type:
    """Replaces the search space entries for hyperparameters that do not support mutation.

    Not all hyperparameters allow mutation, thus their search space entries need to be replaced with fixed values. When
    an `Optuna` optimization was performed prior, the optimized values will be given as in the ``replacements_dict``,
    otherwise the ``replacements_dict`` will contain the default values.

    This function is specific to the built-in ``build``-function for classification using multilayer perceptrons. With
    this implementation, the hyperparameters ``'num_layers'``, ``'activation'``, ``'kernel_initializer'``,
    ``'bias_initializer'``, ``'loss_function'`` and all hyperparameters containing ``'units'`` are replaced. This
    function can be overwritten by defining a ``prepare_search_space_for_PBT``-function in the run-config.

    Parameters
    ----------
    search_space : tune_search_space_type
        Dictionary containing the search space for each hyperparameter.
    replacements_dict : model_config_type
        Dictionary containing fixed values for each hyperparameter that does not support mutation.

    Returns
    -------
    tune_search_space_type
        Dictionary containing the search space for each hyperparameter, with fixed values for hyperparameters that do
        not support mutation.
    """
    # make a copy of the search space
    # search_space = {k: v for k, v in search_space.items()}
    search_space = search_space.copy()

    for hp, values in search_space.items():
        if hp == "num_layers" and not (isinstance(values, float) or isinstance(values, int)):
            print(
                "INFO: mutating the number of layers with PBT is not possible, choosing fixed value of {}".format(
                    replacements_dict["num_layers"]
                )
            )
            search_space[hp] = replacements_dict["num_layers"]
        elif hp == "activation" and not isinstance(values, str):
            print(
                "INFO: mutating activation functions with PBT is not possible, choosing fixed activation {}".format(
                    replacements_dict["activation"]
                )
            )
            search_space[hp] = replacements_dict["activation"]
        elif hp == "kernel_initializer" and not isinstance(values, str):
            print(
                "INFO: mutating kernel initializer with PBT is not possible, choosing fixed kernel initializer {}".format(
                    replacements_dict["kernel_initializer"]
                )
            )
            search_space[hp] = replacements_dict["kernel_initializer"]
        elif hp == "bias_initializer" and not isinstance(values, str):
            print(
                "INFO: mutating bias initializer with PBT is not possible, choosing fixed bias initializer {}".format(
                    replacements_dict["bias_initializer"]
                )
            )
            search_space[hp] = replacements_dict["bias_initializer"]
        elif hp == "loss_function" and not isinstance(values, str):
            print(
                "INFO: mutating loss function with PBT is not possible, choosing fixed loss function {}".format(
                    replacements_dict["loss_function"]
                )
            )
            search_space[hp] = replacements_dict["loss_function"]
        elif "units" in hp and not (isinstance(values, float) or isinstance(values, int)):
            print(
                "INFO: mutating the number of units per layer with PBT is not possible, choosing fixed value of {}. "
                "(note: this message will appear once per key in search space containing 'units')".format(
                    replacements_dict["units"]
                )
            )
            search_space[hp] = replacements_dict["units"]
    return search_space


def limit_and_round_hyperparameters(model_config: model_config_type) -> model_config_type:
    """Enforces limits and rounds the values of specific hyperparameters in the model-config.

    During PBT, hyperparameters can be mutated beyond the limits specified in the hyperparameter search space. Since
    some hyperparameters can have hard limits, they must be enforced manually. Additionally, not all learning algorithms
    support quantization. To support quantized hyperparameters, a continuous search space can be used and the quantization
    is performed here (note: this should only be done for hyperparameters that support a large number of possible values,
    e.g. the batch size, but not for e.g. the number of layers).

    This function is specific to the built-in ``build``-function for classification using multilayer perceptrons and can
    be overwritten by defining a ``limit_and_round_hyperparameters``-function in the run-config. With this implementation,
    limits are enforced for the following hyperparameters:

    - ``'learning_rate'``: min: ``1e-7``, max: `unlimited`
    - ``'Adam_beta_1'``: min: ``1e-7``, max: ``1 - 1e-8``
    - ``'one_minus_Adam_beta_2'``: min: ``1e-8``, max: ``1 - 1e-7``
    - ``'l1_lambda'``: min: ``0``, max: `unlimited`
    - ``'l2_lambda'``: min: ``0``, max: `unlimited`
    - ``'dropout'``: min: ``0``, max: ``1 - 1e-8``

    Additionally, the ``'batch_size'`` is rounded to the nearest integer.

    Parameters
    ----------
    model_config : model_config_type
        Dictionary containing the values for each hyperparameter

    Returns
    -------
    model_config_type
        Dictionary containing the values for each hyperparameter, with limits and roundings applied where necessary.
    """
    # make a copy of the model config
    model_config = model_config.copy()

    # some parameters have limited range that may be exceeded during population based training
    model_config["learning_rate"] = max(model_config["learning_rate"], 1e-7)
    model_config["Adam_beta_1"] = max(min(model_config["Adam_beta_1"], 1.0 - 1e-8), 1e-7)
    model_config["one_minus_Adam_beta_2"] = min(max(model_config["one_minus_Adam_beta_2"], 1e-8), 1.0 - 1e-7)
    model_config["l1_lambda"] = max(model_config["l1_lambda"], 0.0)
    model_config["l2_lambda"] = max(model_config["l2_lambda"], 0.0)
    model_config["dropout"] = max(min(model_config["dropout"], 1.0 - 1e-8), 0.0)

    # some parameters need to be quantized, but not all learning algorithms support quantized parameters; rounding them here
    model_config["batch_size"] = int(round(model_config["batch_size"], 0))
    return model_config
