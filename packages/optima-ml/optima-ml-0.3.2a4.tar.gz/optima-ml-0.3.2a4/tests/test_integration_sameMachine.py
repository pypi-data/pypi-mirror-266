import functools
import os
import shutil
import pickle
import zipfile
import numpy as np

from unittest.mock import patch

from .context import optima

def test_integration():
    # # perform the optimization
    with patch("sys.argv", ["OPTIMA-runner.py", '--cpus', '1', '--gpus', '0', '--cluster', 'local', '--mem_per_cpu', '600',
                            '--cpus_per_trial', '1', '--config', 'tests/config.py']):
        optima.main()

    # unzip the saved optimization output
    with zipfile.ZipFile("tests/resources/test_optimization.zip", "r") as archive:
        archive.extractall("tests/temp_integration_test")

    # check the first optimization step
    # load the evaluation results
    with open("tests/test_optimization/results/variable_optimization/evaluation.pickle", "rb") as evaluation_file:
        (
            best_trials,
            best_trials_fit,
            configs_df,
            _,
            _,
            _,
            _,
            evaluation_string,
            raw_metric_values
        ) = pickle.load(evaluation_file)
    with open("tests/temp_integration_test/test_optimization/results/variable_optimization/evaluation.pickle", "rb") as evaluation_file:
        (
            best_trials_reference,
            best_trials_fit_reference,
            configs_df_reference,
            _,
            _,
            _,
            _,
            evaluation_string_reference,
            raw_metric_values_reference
        ) = pickle.load(evaluation_file)

    # we assume that the results of the optimization are identical, and the results of the evaluation are close (but need
    # not be identical due to numerical differences on different systems arising during the crossvalidation). The path
    # to the trial of cause is expected to be different.
    assert (2 * (best_trials.drop(columns="trial") - best_trials_reference.drop(columns="trial")) / (best_trials.drop(columns="trial") + best_trials_reference.drop(columns="trial"))).abs().max().max() < 1e-8
    assert (2 * (best_trials_fit.drop(columns="trial") - best_trials_fit_reference.drop(columns="trial")) / (best_trials_fit.drop(columns="trial") + best_trials_fit_reference.drop(columns="trial"))).abs().max().max() < 1e-8
    assert configs_df.equals(configs_df_reference)
    for raw, raw_test in zip(raw_metric_values, raw_metric_values_reference):
        if raw != 0 or raw_test != 0:
            assert abs(2 * (raw - raw_test) / (raw + raw_test)) < 1e-8

    # check the variable optimization
    with open("tests/test_optimization/results/variable_optimization/optimized_vars.pickle", "rb") as f:
        optimized_vars = pickle.load(f)
    with open("tests/test_optimization/results/variable_optimization/variable_optimization.pickle", "rb") as f:
        var_opt_baseline, var_opt_results = pickle.load(f)
    with open("tests/temp_integration_test/test_optimization/results/variable_optimization/optimized_vars.pickle", "rb") as f:
        optimized_vars_reference = pickle.load(f)
    with open("tests/temp_integration_test/test_optimization/results/variable_optimization/variable_optimization.pickle", "rb") as f:
        var_opt_baseline_reference, var_opt_results_reference = pickle.load(f)

    assert optimized_vars == optimized_vars_reference
    assert np.max(np.abs(var_opt_baseline - var_opt_baseline_reference)) < 1e-8
    for it in range(len(var_opt_results_reference)):
        for var_set in var_opt_results_reference[it].keys():
            assert np.max(np.abs(np.array(var_opt_results[it][var_set]) - np.array(var_opt_results_reference[it][var_set]))) < 1e-8

    # check the main optimization step
    with open("tests/test_optimization/results/optuna+ASHA/evaluation.pickle", "rb") as evaluation_file:
        (
            best_trials,
            best_trials_fit,
            configs_df,
            _,
            _,
            _,
            _,
            evaluation_string,
            raw_metric_values
        ) = pickle.load(evaluation_file)
    with open("tests/temp_integration_test/test_optimization/results/optuna+ASHA/evaluation.pickle", "rb") as evaluation_file:
        (
            best_trials_reference,
            best_trials_fit_reference,
            configs_df_reference,
            _,
            _,
            _,
            _,
            evaluation_string_reference,
            raw_metric_values_reference
        ) = pickle.load(evaluation_file)
    assert (2 * (best_trials.drop(columns="trial") - best_trials_reference.drop(columns="trial")) / (best_trials.drop(columns="trial") + best_trials_reference.drop(columns="trial"))).abs().max().max() < 1e-8
    assert (2 * (best_trials_fit.drop(columns="trial") - best_trials_fit_reference.drop(columns="trial")) / (best_trials_fit.drop(columns="trial") + best_trials_fit_reference.drop(columns="trial"))).abs().max().max() < 1e-8
    assert configs_df.equals(configs_df_reference)
    for raw, raw_test in zip(raw_metric_values, raw_metric_values_reference):
        if raw != 0 or raw_test != 0:
            assert abs(2 * (raw - raw_test) / (raw + raw_test)) < 1e-8

    # check the PBT step
    with open("tests/test_optimization/results/PBT/evaluation.pickle", "rb") as evaluation_file:
        (
            best_trials,
            _,
            configs_df,
            _,
            _,
            _,
            _,
            evaluation_string,
            raw_metric_values
        ) = pickle.load(evaluation_file)
    with open("tests/temp_integration_test/test_optimization/results/PBT/evaluation.pickle", "rb") as evaluation_file:
        (
            best_trials_reference,
            _,
            configs_df_reference,
            _,
            _,
            _,
            _,
            evaluation_string_reference,
            raw_metric_values_reference
        ) = pickle.load(evaluation_file)
    assert (2 * (best_trials.drop(columns="trial") - best_trials_reference.drop(columns="trial")) / (best_trials.drop(columns="trial") + best_trials_reference.drop(columns="trial"))).abs().max().max() < 1e-8
    assert configs_df.equals(configs_df_reference)
    for raw, raw_test in zip(raw_metric_values, raw_metric_values_reference):
        if raw != 0 or raw_test != 0:
            assert abs(2 * (raw - raw_test) / (raw + raw_test)) < 1e-8

    # cleanup
    shutil.rmtree("tests/test_optimization")
    shutil.rmtree("tests/temp_integration_test")

