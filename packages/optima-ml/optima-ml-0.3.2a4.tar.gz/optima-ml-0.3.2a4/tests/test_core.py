# -*- coding: utf-8 -*-
"""Collection of unit tests core functionality."""
import os
import shutil
import pickle
import zipfile

import pytest

import numpy as np

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # run tests on CPU
from ray import tune

from .context import optima, evaluation, search_space, inputs, builtin_inputs, builtin_search_space
from . import config as run_config


def test_run_config_to_tune_converter():
    # verify the returned types
    assert isinstance(search_space.run_config_to_tune_converter(1), int)
    assert isinstance(search_space.run_config_to_tune_converter(1.0), float)
    assert isinstance(search_space.run_config_to_tune_converter("relu"), str)
    assert isinstance(search_space.run_config_to_tune_converter([1, 2, 3]), tune.search.sample.Categorical)
    assert isinstance(search_space.run_config_to_tune_converter(('uniform', 1., 3.)), tune.search.sample.Float)
    assert isinstance(search_space.run_config_to_tune_converter(('uniform', 1, 100)), tune.search.sample.Integer)
    assert isinstance(search_space.run_config_to_tune_converter(('uniform', 1., 3., 0.02)), tune.search.sample.Float)
    assert isinstance(search_space.run_config_to_tune_converter(('uniform', 1, 100, 5)), tune.search.sample.Integer)
    assert isinstance(search_space.run_config_to_tune_converter(('log', 1., 3.)), tune.search.sample.Float)
    assert isinstance(search_space.run_config_to_tune_converter(('log', 1, 100)), tune.search.sample.Integer)
    assert isinstance(search_space.run_config_to_tune_converter(('log', 1., 3., 0.02)), tune.search.sample.Float)
    assert isinstance(search_space.run_config_to_tune_converter(('log', 1, 100, 5)), tune.search.sample.Integer)
    assert isinstance(search_space.run_config_to_tune_converter(('normal', 1., 0.5)), tune.search.sample.Float)
    assert isinstance(search_space.run_config_to_tune_converter(('normal', 1., 0.5, 0.02)), tune.search.sample.Float)

    # for non-categorical distributions, verify the distributions are correct
    uniform = search_space.run_config_to_tune_converter(('uniform', 0.1, 10.))
    log = search_space.run_config_to_tune_converter(('log', 0.1, 10.))
    normal = search_space.run_config_to_tune_converter(('normal', 0, 1))
    uniform_samples = [uniform.sample() for _ in range(100000)]
    log_samples = np.log([log.sample() for _ in range(100000)])  # applying log to samples from log-uniform distribution returns uniformly distributed samples
    normal_samples = [normal.sample() for _ in range(100000)]
    uniform_hist = np.histogram(uniform_samples, bins=5)[0]
    log_hist = np.histogram(log_samples, bins=5)[0]
    uniform_hist = uniform_hist / np.mean(uniform_hist)
    log_hist = log_hist / np.mean(log_hist)
    assert np.std(uniform_hist) < 0.05
    assert np.std(log_hist) < 0.05

    import scipy
    assert scipy.stats.normaltest(normal_samples).pvalue > 0.01

    # check if quantization works
    quniform = search_space.run_config_to_tune_converter(('uniform', 0.1, 10., 0.01))
    qlog = search_space.run_config_to_tune_converter(('log', 0.1, 10., 0.01))
    qnormal = search_space.run_config_to_tune_converter(('normal', 0, 100, 2))
    quniform_samples = [quniform.sample() for _ in range(100000)]
    qlog_samples = [qlog.sample() for _ in range(100000)]
    qnormal_samples = [qnormal.sample() for _ in range(100000)]
    assert (np.minimum(np.mod(np.array(quniform_samples) / 0.01, 1), 1 - np.mod(np.array(quniform_samples) / 0.01, 1)) < 1e-8).all()
    assert (np.minimum(np.mod(np.array(qlog_samples) / 0.01, 1), 1 - np.mod(np.array(qlog_samples) / 0.01, 1)) < 1e-8).all()
    assert (np.minimum(np.mod(np.array(qnormal_samples) / 2, 1), 1 - np.mod(np.array(qnormal_samples) / 2, 1)) < 1e-8).all()
    quniform_hist = np.histogram(quniform_samples, bins=5)[0]
    qlog_hist = np.histogram(np.log(qlog_samples), bins=5)[0]
    quniform_hist = quniform_hist / np.mean(quniform_hist)
    qlog_hist = qlog_hist / np.mean(qlog_hist)
    assert np.std(quniform_hist) < 0.05
    assert np.std(qlog_hist) < 0.05
    assert scipy.stats.normaltest(qnormal_samples).pvalue > 0.001


@pytest.mark.skipif(os.environ.get('TEST_QUICK') == '1', reason='Test takes more than 5 seconds to run.')
def test_evaluate_experiment():  # TODO: add verification of plots?
    # get the necessary files from old evaluation; we need configs.pickle, dfs.pickle and analysis.pickle to perform the
    # evaluation
    if os.path.exists("tests/temp_test_evaluation"):
        shutil.rmtree("tests/temp_test_evaluation")
    if os.path.exists("tests/test_optimization"):
        shutil.rmtree("tests/test_optimization")
    with zipfile.ZipFile("tests/resources/test_optimization.zip", "r") as archive:
        archive.extractall("tests/temp_test_evaluation")
    os.makedirs("tests/temp_test_evaluation/optimization_evaluation/")
    shutil.copy2("tests/temp_test_evaluation/test_optimization/results/variable_optimization/configs.pickle", "tests/temp_test_evaluation/optimization_evaluation/configs.pickle")
    shutil.copy2("tests/temp_test_evaluation/test_optimization/results/variable_optimization/dfs.pickle", "tests/temp_test_evaluation/optimization_evaluation/dfs.pickle")
    with open("tests/temp_test_evaluation/test_optimization/results/variable_optimization/analysis.pickle", "rb") as file:
        analysis = pickle.load(file)

    # do necessary setup for evaluation
    input_handler = builtin_inputs.InputHandler(run_config)
    (inputs_split,
     targets_split,
     weights_split,
     normalized_weights_split) = inputs.get_experiment_inputs(run_config, input_handler, output_dir=None)
    search_space = builtin_search_space.build_search_space(builtin_search_space.get_hp_defaults(), run_config)
    search_space["max_epochs"] = run_config.max_epochs
    custom_metrics = run_config.custom_metrics
    composite_metrics = run_config.composite_metrics
    native_metrics = run_config.native_metrics
    weighted_native_metrics = run_config.weighted_native_metrics

    # evaluation; get the raw metric values to compare
    best_trials_test, best_trials_fit_test, configs_df_test, _, raw_metric_values_test = \
        evaluation.evaluate_experiment(analysis,
                                       optima.train_model,
                                       run_config,
                                       run_config.monitor_name,
                                       run_config.monitor_op,
                                       search_space,
                                       run_config.search_space,
                                         "tests/temp_test_evaluation/optimization_evaluation",
                                       inputs_split,
                                       targets_split,
                                       weights_split,
                                       normalized_weights_split,
                                       input_handler,
                                       custom_metrics=custom_metrics,
                                       composite_metrics=composite_metrics,
                                       native_metrics=native_metrics,
                                       weighted_native_metrics=weighted_native_metrics,
                                       cpus_per_model=1,
                                       gpus_per_model=0,
                                       overtraining_conditions=run_config.overtraining_conditions,
                                       return_results_str=True,
                                       return_unfilled=True)

    # get the results of the previous evaluation
    with open("tests/temp_test_evaluation/optimization_evaluation/evaluation.pickle", "rb") as evaluation_file:
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

    # we assume that the results of the optimization are identical, and the results of the evaluation are close (but need
    # not be identical due to numerical differences on different systems arising during the crossvalidation)
    assert best_trials.equals(best_trials_test)
    assert best_trials_fit.equals(best_trials_fit_test)
    assert configs_df.equals(configs_df_test)
    for raw, raw_test in zip(raw_metric_values, raw_metric_values_test):
        if raw != 0 or raw_test != 0:
            assert abs(2 * (raw - raw_test) / (raw + raw_test)) < 1e-3

    # cleanup
    shutil.rmtree("tests/temp_test_evaluation")
