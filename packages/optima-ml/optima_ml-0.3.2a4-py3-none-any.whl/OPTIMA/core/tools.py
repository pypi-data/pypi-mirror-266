# -*- coding: utf-8 -*-
"""Collection of helper functions."""
from types import ModuleType
import os
import sys

import numpy as np

from ray import tune


def get_output_dir(run_config: ModuleType, array: bool = False, array_index: int = 0) -> str:
    """Builds the string to be used as the name of the output directory.

    Parameters
    ----------
    run_config : ModuleType
        Reference to the imported `run-config`-file.
    array : bool
        Is the optimization executed using an array job? (Default value = False)
    array_index : int
        If the optimization is running as an array job, the ``array_index`` is needed to prevent file access conflicts. (Default value = 0)

    Returns
    -------
    str
        Path to the output directory.
    """
    if run_config.use_exact_name:
        output_folder = run_config.output_name
    else:
        output_folder = (
            "OPTIMA"
            + ("_varOpt" if run_config.perform_variable_opt else "")
            + (
                (
                    "+optuna+ASHA"
                    if run_config.perform_main_hyperopt and run_config.perform_variable_opt
                    else "_optuna+ASHA"
                )
                if run_config.perform_main_hyperopt
                else ""
            )
            + (
                (
                    "+PBT"
                    if run_config.perform_PBT_hyperopt
                    and (run_config.perform_variable_opt or run_config.perform_main_hyperopt)
                    else "_PBT"
                )
                if run_config.perform_PBT_hyperopt
                else ""
            )
            + (("_" + run_config.output_name) if run_config.output_name != "" else "")
        )

    output_path = os.path.join(run_config.output_path, output_folder)
    if array:
        output_path = os.path.join(output_path, str(array_index))
    return output_path


def check_optimization_finished(
    results_grid: tune.ResultGrid, target_num_samples: int, success_string: str, failure_string: str
) -> None:
    """Checks if the requested number of trials ran and terminated, i.e. the experiment finished successfully.

    Depending on the success of the experiment, one of two strings is printed. If the experiment did not finish successfully,
    the program is terminated with exit code ``1``.

    Parameters
    ----------
    results_grid : tune.ResultGrid
        The ``ResultGrid`` returned by the ``Tuner``.
    target_num_samples : int
        The number of trials that were to be run.
    success_string : str
        The string to print if the experiment was successful.
    failure_string : str
        The string to print if the experiment was not successful.
    """
    # make sure all trails ran and finished successfully
    finished_successfully = (len(results_grid) == target_num_samples) and (
        results_grid.num_terminated == target_num_samples
    )

    if finished_successfully:
        print(success_string)
    else:
        print(failure_string)
        sys.exit(1)


def get_max_seeds() -> tuple[int]:
    """Helper function to check if 32- or 64-bit integers are used by numpy and return a corresponding range of seed values.

    Returns
    -------
    tuple[int]
        Tuple containing the minimal and maximal seed value to use.
    """
    if np.int_ == np.int32:
        max_seeds = (-2147483648, 2147483648)
    else:
        max_seeds = (0, 4294967295)
    return max_seeds
