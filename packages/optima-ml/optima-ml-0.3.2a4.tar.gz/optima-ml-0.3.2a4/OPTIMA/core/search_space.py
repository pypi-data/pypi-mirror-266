# -*- coding: utf-8 -*-
"""A module that provides general functionality to handle the hyperparameter search space."""
from typing import Union, Optional, Callable, Any

import numpy as np

from ray import tune

import OPTIMA.core.tools

run_config_search_space_entry_type = Union[int, float, str, list, tuple]

tune_search_space_entry_type = Union[
    tune.search.sample.Float,
    tune.search.sample.Integer,
    tune.search.sample.Categorical,
    list,
    dict,
    str,
    float,
    int,
]
tune_search_space_type = dict[
    str,
    tune_search_space_entry_type,
]

PBT_search_space_type = dict[
    str, Union[tune.search.sample.Float, tune.search.sample.Integer, tune.search.sample.Categorical, list, dict]
]


def run_config_to_tune_converter(hp_entry: run_config_search_space_entry_type) -> tune_search_space_entry_type:
    """If an entry from ``run_config.search_space`` or ``hyperparameter_defaults`` is given, will return the correct ``tune.sample`` object.

    As of `Ray` version `2.4`, a bug exists causing ``tune.qrandn`` to return unrounded values when the values should be
    rounded to the nearest integer (i.e. ``hp_entry[3] = 1``). A warning message is printed in this case to notify the
    user.

    Parameters
    ----------
    hp_entry : run_config_search_space_entry_type
        Entry from ``run_config.search_space`` or ``hyperparameter_defaults``.

    Returns
    -------
    tune_search_space_entry_type
        The ``tune.sample`` object corresponding to ``hp_entry``.
    """
    # hp in config is fixed
    if isinstance(hp_entry, float) or isinstance(hp_entry, int) or isinstance(hp_entry, str):
        return hp_entry
    # range for hp in config is given as a list
    elif isinstance(hp_entry, list):
        return tune.choice(hp_entry)
    elif isinstance(hp_entry, tuple):
        # range for hp in config is uniform and continous
        if hp_entry[0] == "uniform" and len(hp_entry) == 3:
            if isinstance(hp_entry[1], float):
                return tune.uniform(hp_entry[1], hp_entry[2])
            else:
                return tune.randint(hp_entry[1], hp_entry[2] + 1)  # upper bound is exclusive
        # range for hp in config is log and continous
        elif hp_entry[0] == "log" and len(hp_entry) == 3:
            if isinstance(hp_entry[1], float):
                return tune.loguniform(hp_entry[1], hp_entry[2])
            else:
                return tune.lograndint(hp_entry[1], hp_entry[2] + 1)  # upper bound is exclusive
        # range for hp in config is normal and continous
        elif hp_entry[0] == "normal" and len(hp_entry) == 3:
            return tune.randn(hp_entry[1], hp_entry[2])
        # range for hp in config is uniform and quantized
        elif hp_entry[0] == "uniform" and len(hp_entry) == 4:
            if isinstance(hp_entry[1], float):
                return tune.quniform(hp_entry[1], hp_entry[2], hp_entry[3])
            else:
                return tune.qrandint(hp_entry[1], hp_entry[2], hp_entry[3])  # upper bound is inclusive here!
        # range for hp in config is log and quantized
        elif hp_entry[0] == "log" and len(hp_entry) == 4:
            if isinstance(hp_entry[1], float):
                return tune.qloguniform(hp_entry[1], hp_entry[2], hp_entry[3])
            else:
                return tune.qlograndint(hp_entry[1], hp_entry[2], hp_entry[3])  # upper bound is inclusive here!
        # range for hp in config is normal and quantized
        elif hp_entry[0] == "normal" and len(hp_entry) == 4:
            if hp_entry[3] == 1:
                print(
                    "Warning: due to a bug in tune.qrandn, unrounded values are returned instead of rounding to the"
                    "nearest integer. Other step sizes (both smaller and larger than 1) seem to be fine."
                )
            return tune.qrandn(hp_entry[1], hp_entry[2], hp_entry[3])


def get_PBT_hps_to_mutate(search_space: tune_search_space_type) -> tune_search_space_type:
    """Builds the search space of hyperparameters to mutate that is given to the ``PopulationBasedTraining``-scheduler.

    The ``PopulationBasedTraining``-scheduler only supports `Float`, `Integer` and `Categorical` `Tune` search spaces as
    well as lists and dictionaries. Any other types of values in ``search_space``, specifically constants, are not added
    to the search space of hyperparameters to mutate.

    Parameters
    ----------
    search_space : tune_search_space_type
        The `Tune` search space that potentially contains constant values for some hyperparameters.

    Returns
    -------
    tune_search_space_type
        The pruned search space, containing only those hyperparameters whose search space is supported by PBT, i.e.
        is one of the ``tune.search.sample`` objects, a list or a dict.
    """
    # for the population based training, we have to choose which hyperparameters should be mutated. Since we want to
    # mutate all, it would be convenient to just give the search space to PopulationBasedTraining. However, for PBT all
    # entries in the hyperparam_mutations_dict need to either be a list, a dict, a tune search space object or callables
    # -> constant hyperparameters should be removed.
    hyperparams_to_mutate = {}
    for hp, values in search_space.items():
        if (
            isinstance(values, tune.search.sample.Float)
            or isinstance(values, tune.search.sample.Integer)
            or isinstance(values, tune.search.sample.Categorical)
            or isinstance(values, list)
            or isinstance(values, dict)
        ):
            hyperparams_to_mutate[hp] = values
    return hyperparams_to_mutate


def add_random_seed_suggestions(seed: Optional[int] = None) -> Callable:
    """Decorator function to add a random seed to the dictionary of suggestions produced by a search algorithm.

    In order to prevent the search algorithms from trying to optimize the seed, this simple wrapper creates a subclass
    of the searcher and appends a random seed to the suggestions while leaving the rest of the searcher untouched. To
    make the added seeds deterministic, a seed needs to be provided to the wrapper that is used to generate the `numpy`
    random state.

    Parameters
    ----------
    seed : Optional[int]
        Seed to set the `numpy` random state. (Default value = None)

    Returns
    -------
    Callable
        Decorator function that uses the random state created in the outer function.
    """

    def _add_seed(cls: type) -> type:
        """Inner decorator function.

        Creates a subclass of the decorated class and overwrites the ``suggest``-function. When called, the
        ``suggest``-function of the super-class is executed and a new random number is added as key ``'seed'`` to the
        dictionary of suggestions returned by the super-class. To generate this number, the random state provided in the
        outer function is used.

        Returns
        -------
        type
            The subclass of the decorated class with the ``suggest``-function overwritten
        """

        class SearcherWithSeed(cls):
            """Subclass of the decorated class with the ``suggest``-function overwritten."""

            def suggest(self, *args: Any, **kwargs: Any) -> dict:
                """Overwrites the ``suggest``-function of the super-class to add the random seed to the suggestions.

                Parameters
                ----------
                *args : Any
                    Positional arguments of the ``suggest``-function of the super-class.
                **kwargs : Any
                    Keyword arguments of the ``suggest``-function of the super-class.

                Returns
                -------
                dict
                    The dictionary of suggestions returned by the ``suggest``-function of the super-class with the
                    random seed added as an additional entry with key ``'seed'``.
                """
                suggestion = super(SearcherWithSeed, self).suggest(*args, **kwargs)
                suggestion["seed"] = rng.randint(*OPTIMA.core.tools.get_max_seeds())
                return suggestion

        return SearcherWithSeed

    rng = np.random.RandomState(seed)
    return _add_seed
