# -*- coding: utf-8 -*-
"""A module that provides functionality to evaluate the trained models."""
from types import ModuleType
from typing import Callable, Union, Literal, Any, Optional

import copy
import os
import pickle

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from sklearn.model_selection import KFold

import tabulate
from matplotlib import pyplot as plt

# This way of providing the model specific functionality allows supporting different machine learning libraries besides
# Keras
import importlib.util

if importlib.util.find_spec("lightning") is not None:
    import torch

import ray
from ray import tune

import OPTIMA.core.training
import OPTIMA.core.model
import OPTIMA.builtin.evaluation
import OPTIMA.builtin.inputs
import OPTIMA.builtin.search_space
from OPTIMA.core.search_space import tune_search_space_type, run_config_search_space_entry_type


def evaluate_experiment(
    analysis: tune.ExperimentAnalysis,
    training_func: Callable,
    run_config: ModuleType,
    optimize_name: str,
    optimize_op: Union[Literal["max"], Literal["min"]],
    search_space: tune_search_space_type,
    run_config_search_space: dict[str, run_config_search_space_entry_type],
    results_dir: str,
    inputs_split: list[ray.ObjectRef],
    targets_split: list[ray.ObjectRef],
    weights_split: list[ray.ObjectRef],
    normalized_weights_split: list[ray.ObjectRef],
    input_handler: OPTIMA.builtin.inputs.InputHandler,
    custom_metrics: Optional[list[tuple[str, Callable]]] = None,
    composite_metrics: Optional[list[tuple[str, tuple[str, str], Callable]]] = None,
    native_metrics: Optional[list] = None,
    weighted_native_metrics: Optional[list] = None,
    cpus_per_model: int = 1,
    gpus_per_model: int = 0,
    overtraining_conditions: Optional[list] = None,
    write_results: bool = True,
    return_results_str: bool = False,
    return_unfilled: bool = False,
    return_crossval_models: bool = False,
    PBT: bool = False,
    PBT_replay_getter: Optional[Callable] = None,
    seed: Optional[int] = None,
) -> Union[
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame],
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str],
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str, list],
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict, dict],
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str, dict, dict],
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str, list, dict, dict],
]:
    """Performs the evaluation of an experiment to find the best trial, run the crossvalidation and evaluate the models.

    After removing any reports containing ``inf`` or ``NaN`` values, the dictionary of dataframes containing the reports
    of all trials is saved to ``'dfs.pickle'`` in the provided ``results_dir``. If this file already exists, it is not
    overwritten.

    Two sets of plots are produced to give an overview of the entire experiment:

    - A set of overview plots (one per metric) containing the values of the target metric, all `custom metrics` on the
      training and validation datasets and all `composite metrics` for each report of every trial, i.e. the metric values
      after every epoch throughout the entire experiment, sorted by the time of the report. Reports corresponding to
      overfitted epochs (i.e. if any of the `overfitting conditions` defined in the run-config if not satisfied) are
      shown semi-transparent. The plots are saved in the subdirectory ``'overview_plots'`` in the provided ``results_dir``.
    - A set of progress plots (one per metric) containing the value of the target metric, all `custom metrics` on the
      training and validation datasets and all `composite metrics` corresponding to the best epoch up to a certain point
      during the optimization. E.g., at epoch 100, the values of the best epoch in the first 100 epochs is drawn. Thus,
      the shown curves can be interpreted as a convergence of the optimization.

    From the reported metric values, the best trial is selected using two independent methods (except if ``PBT`` is
    ``True``, in which case only the `best value`-method is used):

    - `best value`: the best trial is given by the best reported value of the target metric while passing all
      `overfitting conditions`.
    - `best fit`: the evolution of all metrics of each trial is fitted (see ``evaluation.get_best_trials_from_fit``
      for details). The best trial is given by the best target metric fit function value that passed all overfitting
      conditions. The overfitting conditions are evaluated using the fit function values of all necessary metrics at
      each epoch (if ``run_config.check_overtraining_with_fit`` is ``True``) or using the reported values (if
      ``run_config.check_overtraining_with_fit`` is ``False``).

    For both methods, the hyperparameters corresponding to the best trial and the number of epochs to reach the best
    target metric value are extracted. Both are given to the ``perform_crossvalidation``-function to perform the k-fold
    crossvalidation, resulting in `k` trained models per method.

    The ``evaluate``-function is called for the 2*k models trained during the crossvalidation. After the evaluation, the
    mean and standard deviation of the `k` values for each metric provided by the evaluation is calculated for both sets
    of hyperparameters. The results are printed to console.

    If ``write_results`` is True, the results and a summary of the experiment (the used input variables as given by the
    provided ``input_handler``-instance, the shape of the training, validation and (if used) testing dataset as well as
    the search space) are saved to `results.txt` in the ``results_dir``.

    The full results of the experiment evaluation is saved to `evaluation.pickle` in the ``results_dir`` which allows to
    reload the evaluation results. This is useful when e.g. resuming a partially finished optimization run because the
    evaluation of finished steps does not need to be repeated. Thus, the evaluation is automatically skipped when a
    `evaluation.pickle`-file is present in ``results_dir`` and the results are instead reloaded from that file.

    Parameters
    ----------
    analysis : tune.ExperimentAnalysis
        The ``tune.ExperimentAnalysis``-object extracted from the ``tune.ResultsGrid`` returned by the ``Tuner``.
    training_func : Callable
        Reference to the function performing the training. This is given to ``perform_crossvalidation``.
    run_config : ModuleType
        Reference to the imported run-config file.
    optimize_name : str
        Name of the target metric.
    optimize_op : Union[Literal["max"], Literal["min"]]
        Specifies if the target metric is to be maximized or minimized. Can be either ``'max'`` or ``'min'``.
    search_space : tune_search_space_type
        The tune search space provided to the Tuner.
    run_config_search_space : dict[str, run_config_search_space_entry_type]
        The search space as defined in the run-config.
    results_dir : str
        Path to the directory where the results are to be saved.
    inputs_split : list[ray.ObjectRef]
        List containing the object reference to the numpy array of input features for the training, validation and (if
        used) testing sets.
    targets_split : list[ray.ObjectRef]
        List containing the object reference to the numpy array of target labels for the training, validation and (if
        used) testing sets.
    weights_split : list[ray.ObjectRef]
        List containing the object reference to the numpy array of event weights for the training, validation and (if
        used) testing sets.
    normalized_weights_split : list[ray.ObjectRef]
        List containing the object reference to the numpy array of normalized event weights for the training, validation
        and (if used) testing sets.
    input_handler : OPTIMA.builtin.inputs.InputHandler
        Instance of the ``OPTIMA.builtin.inputs.InputHandler``-class
    custom_metrics : Optional[list[tuple[str, Callable]]]
        A list of `custom metrics` as defined in the run-config. (Default value = None)
    composite_metrics : Optional[list[tuple[str, tuple[str, str], Callable]]]
        A list of `composite metrics` as defined in the run-config. (Default value = None)
    native_metrics : Optional[list]
        A list of native metrics as defined in the run-config. (Default value = None)
    weighted_native_metrics : Optional[list]
        A list of weighted native metrics as defined in the run-config. (Default value = None)
    cpus_per_model : int
        The number of CPUs to use to train each model. This is given to ``perform_crossvalidation``. (Default value = 1)
    gpus_per_model : int
        The number of GPUs to use to train each model. This is given to ``perform_crossvalidation``. (Default value = 0)
    overtraining_conditions : Optional[list]
        A list of `overtraining conditions` as defined in the run-config. (Default value = None)
    write_results : bool
        If ``True``, the results are written to `results.txt` in ``results_dir``. (Default value = True)
    return_results_str : bool
        If ``True``, the results string that is printed to console is also returned. (Default value = False)
    return_unfilled : bool
        If ``True``, the evaluation part of the results string (containing the metric values returned by the
        ``evaluate``-function) will be provided "unfilled", i.e. with ``{}`` instead of the metric values.
        Additionally, the list of raw metric values is provided. This can be useful for testing. (Default value = False)
    return_crossval_models : bool
        If ``True``, a dictionary containing file names of the saved crossvalidation models, the corresponding indices
        denoting which of the `k` crossvalidation-splittings was used for the training, the model config and a dictionary
        containing the training, validation and (if used) testing datasets for each splitting are returned. (Default value = False)
    PBT : bool
        Signifies if this is the evaluation of the Population Based Training step. This is given to ``perform_crossvalidation``
        and used to skip the fit evaluation. (Default value = False)
    PBT_replay_getter : Optional[Callable]
        A callable that returns a fully configured ``tune.Tuner``-instance to be able to replay a PBT trial (using a
        ``PopulationBasedTrainingReplay``-scheduler). This is given to ``perform_crossvalidation`` and is only necessary
        for the Population Based Training step. (Default value = None)
    seed : Optional[int]
        Seed given to ``perform_crossvalidation``. (Default value = None)

    Returns
    -------
    Union[
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame],
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str],
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str, list],
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict, dict],
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str, dict, dict],
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str, list, dict, dict],
    ]
        Two pandas dataframes containing the values of all metrics, the trial-id, the training iteration and the path to
        the checkpoint directory of the two best checkpoints and a dataframe containing the corresponding hyperparameters
        (that were used to train the crossvalidation models) are returned. If ``return_results_str`` is ``True``, the
        results string that was printed to console is also returned. Finally, if ``return_crossval_models`` is ``True``,
        dictionaries containing the file names of the saved crossvalidation models, the corresponding indices denoting
        which of the `k` crossvalidation-splittings was used for the training, the model config and the corresponding
        training, validation and (if used) testing data are returned as well.
    """
    if overtraining_conditions is None:
        overtraining_conditions = []
    if native_metrics is None:
        native_metrics = []
    if weighted_native_metrics is None:
        weighted_native_metrics = []
    if custom_metrics is None:
        custom_metrics = []
    if composite_metrics is None:
        composite_metrics = []

    # if we are doing the evaluation for the PBT step, we want to skip the fit evaluation
    skip_fit_evaluation = PBT

    # check if evaluation was already done previously
    if not os.path.isfile(os.path.join(results_dir, "evaluation.pickle")):
        # create the results directory if not present
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

        # build a list containing the names of all metrics, grouped together like [[train_loss, val_loss], [train_accuracy, val_accuracy], ...]
        metric_names = []
        optimize_name_included = False
        for metric, _ in native_metrics + weighted_native_metrics + custom_metrics:
            group = ("train_" + metric, "val_" + metric)
            metric_names.append(group)
            if optimize_name in group:
                optimize_name_included = True
        for metric, _, _ in composite_metrics:
            metric_names.append(metric)
            if metric == optimize_name:
                optimize_name_included = True
        if not optimize_name_included:
            metric_names = [optimize_name] + metric_names

        # get the results dataframes and remove all NaN and inf values in columns corresponding to metrics
        if not os.path.isfile(os.path.join(results_dir, "dfs.pickle")):
            dfs_dirty = analysis.trial_dataframes
            dfs = clean_analysis_results(dfs_dirty, metric_names)

            # now also save the dataframes (if not already present)
            with open(os.path.join(results_dir, "dfs.pickle"), "wb") as file:
                pickle.dump(dfs, file)
        else:
            print(f"{os.path.join(results_dir, 'dfs.pickle')} already exists, reloading...")
            with open(os.path.join(results_dir, "dfs.pickle"), "rb") as file:
                dfs = pickle.load(file)

        # go through dataframes and explicitly check if overtraining conditions are fulfilled, and add results (True/False)
        # as new column "overtrained"
        dfs_overtraining_checked = check_overtraining(dfs, overtraining_conditions)

        # produce two sets of plots showing the overall progress of the experiment, one set containing all trials as datapoints,
        # and one showing the evolution of the "best" trial; both as a function of epoch (total epochs across all trials)
        draw_total_progress(
            dfs_overtraining_checked,
            optimize_name,
            optimize_op,
            metric_names,
            figs_dir=results_dir,
            reject_overtrained=True,
        )

        # find best trials by going through the dataframes and finding the extreme value of the metrics we are interested in
        optimization_results_string = ""  # will be printed and saved to file later
        best_trials = get_best_trials(
            dfs_overtraining_checked,
            optimize_name,
            optimize_op,
            metric_names,
            figs_dir=results_dir,
            reject_overtrained=True,
        )
        optimization_results_string += "Best trials according to best achieved value for the metrics to monitor:\n"
        optimization_results_string += tabulate.tabulate(
            best_trials, headers=[best_trials.index.name] + list(best_trials.columns), tablefmt="fancy_grid"
        )

        if not skip_fit_evaluation:
            # get best trials from fit: apply fit to target metrics for each trial, get the minimum of the fit, find the nearest
            # checkpoint that is not overtrained, and write down the fit value at that point; then find the lowest fit value
            # over all trials; when conf.check_overtraining_with_fit is set, give the overtraining conditions to the function
            # which are then used to evaluate the overtraining using the fit function value for all relevant metrics,
            # otherwise the "overtrained" column in the dfs is used
            if run_config.check_overtraining_with_fit:
                best_trials_fit = get_best_trials_from_fit(
                    run_config,
                    dfs_overtraining_checked,
                    optimize_name,
                    optimize_op,
                    metric_names,
                    figs_dir=results_dir,
                    overtraining_conditions=overtraining_conditions,
                    min_R_squared=run_config.fit_min_R_squared,
                )
            else:
                best_trials_fit = get_best_trials_from_fit(
                    run_config,
                    dfs_overtraining_checked,
                    optimize_name,
                    optimize_op,
                    metric_names,
                    figs_dir=results_dir,
                    reject_overtrained=True,
                    min_R_squared=run_config.fit_min_R_squared,
                )
            if best_trials_fit is None:
                print(
                    "WARNING: The fit evaluation failed. This indicates that no trial resulted in a sensible fit, which "
                    "might indicate a problem with the optimization. Skipping the fit evaluation..."
                )
                skip_fit_evaluation = True
            else:
                optimization_results_string += (
                    "\n\nBest trials according to best fit of the metrics to monitor: (all metric values from fit)\n"
                )
                optimization_results_string += tabulate.tabulate(
                    best_trials_fit,
                    headers=[best_trials_fit.index.name] + list(best_trials_fit.columns),
                    tablefmt="fancy_grid",
                )

        # go through results by iterating over the best trials for each target metric, print the corresponding configs,
        # copy best checkpoints to results folder and save output paths for later evaluation
        # first prepare the dataframe that will contain the best configs, meaning the hyperparameters of the best trials
        # for each target metric, once determined using the best value and once using the fit
        optimize_name_list = optimize_name if isinstance(optimize_name, list) else [optimize_name]
        model_configs_df = pd.DataFrame(
            index=list(search_space.keys()) + ["epochs", "seed"],
            columns=list(*zip(optimize_name_list, [f"{metric} fit" for metric in optimize_name_list]))
            if not skip_fit_evaluation
            else optimize_name_list,
        )
        model_configs_df.index.name = "Hyperparameter"
        optimization_results_string += "\n\nBest configs:\n"

        # start by fetching dictionary containing the configs of all trials
        if not os.path.isfile(os.path.join(results_dir, "configs.pickle")):
            all_model_configs = analysis.get_all_configs()
            assert all_model_configs != {}, "Dictionary of configs could not be loaded, was the optimization deleted?"
            trial_ids = [trial.trial_id for trial in analysis.trials]
            with open(os.path.join(results_dir, "configs.pickle"), "wb") as file:
                pickle.dump((all_model_configs, trial_ids), file)
        else:
            print(f"{os.path.join(results_dir, 'configs.pickle')} already exists, reloading...")
            with open(os.path.join(results_dir, "configs.pickle"), "rb") as file:
                all_model_configs, trial_ids = pickle.load(file)

        # start with results from the best metric values
        # get the hp limit and rounding function
        if hasattr(run_config, "limit_and_round_hyperparameters"):
            limit_and_round_hps = run_config.limit_and_round_hyperparameters
        else:
            limit_and_round_hps = OPTIMA.builtin.search_space.limit_and_round_hyperparameters

        dirs_to_evaluate = (
            []
        )  # will contain the paths to the directories containing the models to evaluate (best model from optimization + crossvalidation models)
        model_configs_to_evaluate = []  # will contain the configs of the best models
        for metric, best_trial, best_epoch in zip(best_trials.index, best_trials["trial"], best_trials["best epoch"]):
            # get the config of this trial, add the best epoch and save it to the model_configs_to_evaluate list; this is
            # later given to the crossvalidation function to train multiple models for each config
            model_config_to_evaluate = all_model_configs[best_trial].copy()
            model_config_to_evaluate["epochs"] = int(best_epoch)
            for trial_id in trial_ids:
                if trial_id in best_trial:
                    model_config_to_evaluate[
                        "trial_id"
                    ] = trial_id  # best_trail is full path to the optimization folder while trails in trial_list as only the names
                    break
            model_configs_to_evaluate.append(model_config_to_evaluate)

            # round the config where necessary (in the same way as during the optimization), and add the hyperparameters to
            # the dataframe containing the configs of the best trials
            model_config = limit_and_round_hps(model_configs_to_evaluate[-1])
            for hp in model_configs_df.index:
                model_configs_df.loc[hp, metric] = model_config[hp]

            # create the target folder for the following crossvalidation
            target_folder = os.path.join(results_dir, metric if len(best_trials.index) > 1 else "", "best_value")
            dirs_to_evaluate.append(target_folder)  # mark target_folder to be evaluated later
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

        # then the results from the fit
        if not skip_fit_evaluation:
            for metric, best_trial, best_epoch in zip(
                best_trials_fit.index,
                best_trials_fit["trial"],
                best_trials_fit["best epoch"],
            ):
                model_config_to_evaluate = all_model_configs[best_trial].copy()
                model_config_to_evaluate["epochs"] = int(best_epoch)
                for trial_id in trial_ids:
                    if trial_id in best_trial:
                        model_config_to_evaluate[
                            "trial_id"
                        ] = trial_id  # best_trail is full path to the optimization folder while trails in trial_list as only the names
                        break
                model_configs_to_evaluate.append(model_config_to_evaluate)
                model_config = limit_and_round_hps(model_configs_to_evaluate[-1])
                for hp in model_configs_df.index:
                    model_configs_df.loc[hp, f"{metric} fit"] = model_config[hp]
                target_folder = os.path.join(results_dir, metric if len(best_trials_fit.index) > 1 else "", "best_fit")
                dirs_to_evaluate.append(target_folder)  # mark target_folder to be evaluated later
                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)

        optimization_results_string += tabulate.tabulate(
            model_configs_df,
            headers=[model_configs_df.index.name] + list(model_configs_df.columns),
            tablefmt="fancy_grid",
        )
        print("\n" + optimization_results_string)

        # give the list of best configs to perform_crossvalidation which will perform crossvalidation for each of the
        # configs, applying the same EarlyStopping criteria as during the optimization.
        print("Starting k-fold cross-validation for the best model-configs...")
        crossval_model_info, crossval_input_data = OPTIMA.core.training.perform_crossvalidation(
            model_configs_to_evaluate,
            dirs_to_evaluate,
            training_func,
            run_config,
            input_handler,
            cpus_per_model,
            gpus_per_model,
            custom_metrics,
            composite_metrics,
            native_metrics,
            weighted_native_metrics,
            PBT=PBT,
            PBT_replay_getter=PBT_replay_getter,
            seed=seed,
        )
        print("Cross-validation finished!")

        # reload best models from the optimization and the corresponding crossvalidation models and do the evaluation
        evaluation_string = "Evaluation:"
        print("\nReloading the cross-validation models for evaluation...")

        # get the evaluation function
        if hasattr(run_config, "evaluate"):
            evaluate_func = run_config.evaluate
        else:
            evaluate_func = OPTIMA.builtin.evaluation.evaluate

        # wrap the evaluation function in a ray task
        evaluate_remote = ray.remote(num_cpus=cpus_per_model, num_gpus=gpus_per_model)(evaluate_func).remote

        # go through all the dirs containing models to evaluate
        raw_values_list = (
            []
        )  # will contain all raw values so that they can be returned as numbers; can be useful for testing
        futures = []  # will contain the futures for the remote execution of the evaluation
        for model_dir in dirs_to_evaluate:
            # loop over all models from the crossvalidation and perform an evaluation for each. The evaluation is
            # executed as a Ray task, so we save the returned futures for later.
            print(f"Evaluating {model_dir}")
            for model_info in crossval_model_info[model_dir]:
                # get the inputs
                inputs_split_k, targets_split_k, weights_split_k, normalized_weights_split_k = crossval_input_data[
                    model_info["split"]
                ]

                # do the evaluation
                futures.append(
                    evaluate_remote(
                        run_config,
                        os.path.join(model_dir, model_info["name"]),
                        inputs_split_k,
                        targets_split_k,
                        weights_split_k,
                        normalized_weights_split_k,
                        os.path.join(model_dir, "plots", "evaluation", "crossval_{}".format(model_info["split"])),
                        cpus=cpus_per_model,
                        print_results=False,
                        native_metrics=native_metrics,
                        weighted_native_metrics=weighted_native_metrics,
                        custom_FoMs=custom_metrics,
                        class_labels=run_config.evaluation_class_labels,
                        return_unfilled=True,
                    )
                )

        # save the values of the metrics returned by the evaluation to a list to then calculate mean and std, which
        # are then inserted into the unfilled results string
        for model_dir in dirs_to_evaluate:
            results_str_unfilled = ""
            metrics = []
            for model_info in crossval_model_info[model_dir]:
                # get and save the evaluation results
                results_str_unfilled_k, metrics_k = ray.get(futures.pop(0))
                if results_str_unfilled == "":
                    results_str_unfilled = results_str_unfilled_k
                metrics.append(metrics_k)

                # if defined, execute the finalize function for this model
                if hasattr(run_config, "finalize_model"):
                    # get the inputs for potential use in the finalize function
                    inputs_split_k, targets_split_k, weights_split_k, normalized_weights_split_k = crossval_input_data[
                        model_info["split"]
                    ]

                    # execute the finalize function as ray task in case it does predictions or something else with the
                    # models. However, we can't know if the finalize-function is written thread-safe, so execute them
                    # sequentially
                    f = ray.remote(num_cpus=cpus_per_model, num_gpus=gpus_per_model)(run_config.finalize_model).remote(
                        run_config,
                        inputs_split_k,
                        targets_split_k,
                        weights_split_k,
                        normalized_weights_split_k,
                        results_dir=results_dir,
                        model_dir=model_dir,
                        model_info=model_info,
                        input_handler=input_handler,
                    )
                    ray.get(f)
                    del f

            # calculate the mean and std for the returned metrics and fill them into the results string
            metrics_array = np.array(metrics)
            metrics_mean = np.mean(metrics_array, axis=0)
            metrics_std = np.std(metrics_array, axis=0)
            metrics_with_errors_strs = []
            for mean, std, raw_values in zip(metrics_mean, metrics_std, metrics_array.transpose()):
                if std != 0:
                    err_significant_digit = max(-int(np.floor(np.log10(abs(std)))), 0)
                    metric_with_error_str = "{{:.{}f}} +- {{:.{}f}}".format(
                        err_significant_digit + 1, err_significant_digit + 1
                    )
                else:
                    metric_with_error_str = "{} +- {}"
                    err_significant_digit = 4
                metric_with_error_str += (
                    " (" + ", ".join(["{{:.{}f}}".format(err_significant_digit + 1) for _ in raw_values]) + ")"
                )
                raw_values_list += [mean, std] + list(raw_values)
                metrics_with_errors_strs.append(metric_with_error_str)
            evaluation_string += f"\n{model_dir}:\n"
            evaluation_string += results_str_unfilled.format(*metrics_with_errors_strs)

        # get summary of the optimization for the results file
        if run_config.use_testing_dataset:
            targets_train, targets_val, targets_test = ray.get(targets_split)
        else:
            targets_train, targets_val = ray.get(targets_split)

        if targets_train.shape[1] == 1:
            optimization_str = (
                f"training events: {targets_train[targets_train[:, 0] == 1].shape[0]} signal, "
                f"{targets_train[targets_train[:, 0] == 0].shape[0]} background\n"
            )
            optimization_str += (
                f"validation events: {targets_val[targets_val[:, 0] == 1].shape[0]} signal, "
                f"{targets_val[targets_val[:, 0] == 0].shape[0]} background\n"
            )
            if run_config.use_testing_dataset:
                optimization_str += (
                    f"test events: {targets_test[targets_test[:, 0] == 1].shape[0]} signal, "
                    f"{targets_test[targets_test[:, 0] == 0].shape[0]} background\n"
                )
        else:
            optimization_str = f"training events: {[targets_train[targets_train[:, j] == 1].shape[0] for j in range(targets_train.shape[1])]}\n"
            optimization_str += f"validation events: {[targets_val[targets_val[:, j] == 1].shape[0] for j in range(targets_val.shape[1])]}\n"
            if run_config.use_testing_dataset:
                optimization_str += f"test events: {[targets_test[targets_test[:, j] == 1].shape[0] for j in range(targets_test.shape[1])]}\n"
        optimization_str += "input variables: {}\n\n".format(", ".join(input_handler.get_vars()))
        optimization_str += "search space:\n"
        for hp in search_space.keys():
            if hp in run_config_search_space.keys():
                optimization_str += f"\t{hp}: {run_config_search_space[hp]}\n"
            else:
                optimization_str += f"\t{hp}: {search_space[hp]}\n"

        # write results to file
        if write_results:
            with open(os.path.join(results_dir, "results.txt"), "w") as results_file:
                results_file.write(
                    optimization_str
                    + "\n"
                    + optimization_results_string
                    + "\n\n"
                    + evaluation_string.format(*raw_values_list)
                )

        # saving results of the evaluation to file to reload the evaluation should the experiment be stopped and resumed in
        # the future
        with open(os.path.join(results_dir, "evaluation.pickle"), "wb") as evaluation_file:
            pickle.dump(
                (
                    best_trials,
                    best_trials_fit if not skip_fit_evaluation else None,
                    model_configs_df,
                    optimization_str,
                    optimization_results_string,
                    crossval_model_info,
                    {
                        k: [ray.get(e) for e in v] for k, v in crossval_input_data.items()
                    },  # we want to save the actual data here!
                    evaluation_string,
                    raw_values_list,
                ),
                evaluation_file,
            )
    else:
        print(
            f"Found previous evaluation at {os.path.join(results_dir, 'evaluation.pickle')}, reloading previous results "
            f"and skipping the evaluation. If this is not intentional, delete the evaluation.pickle file or "
            f"the {results_dir} directory."
        )
        with open(os.path.join(results_dir, "evaluation.pickle"), "rb") as evaluation_file:
            (
                best_trials,
                best_trials_fit,
                model_configs_df,
                optimization_str,
                optimization_results_string,
                crossval_model_info,
                crossval_input_data,
                evaluation_string,
                raw_values_list,
            ) = pickle.load(evaluation_file)

        # check if the crossvalidation should be done again; could be useful when crossvalidation should be repeated but
        # the optimization folder was already deleted, but should be avoided when possible because the evaluation cannot
        # be redone in that case (because the configs of each trial are saved inside the optimization folder and are
        # thus not available anymore)
        print(
            "Checking if crossvalidation needs to be repeated. Note that the evaluation will not be repeated even when"
            " the crossvalidation is redone! If you want to repeat the evaluation, it's necessary to delete the "
            "'evaluation.pickle' file."
        )
        model_configs_to_evaluate = []
        dirs_to_evaluate = []
        for metric in best_trials.index:
            model_config = {}
            model_config_fit = {}
            for hp in model_configs_df.index:
                model_config[hp] = model_configs_df.loc[hp, metric]
                if not skip_fit_evaluation:
                    model_config_fit[hp] = model_configs_df.loc[hp, f"{metric} fit"]
            model_configs_to_evaluate.append(model_config)
            if not skip_fit_evaluation:
                model_configs_to_evaluate.append(model_config_fit)
            dirs_to_evaluate.append(
                os.path.join(results_dir, metric if len(best_trials.index) > 1 else "", "best_value")
            )
            if not skip_fit_evaluation:
                dirs_to_evaluate.append(
                    os.path.join(results_dir, metric if len(best_trials.index) > 1 else "", "best_fit")
                )

        crossval_model_info, crossval_input_data = OPTIMA.core.training.perform_crossvalidation(
            model_configs_to_evaluate,
            dirs_to_evaluate,
            training_func,
            run_config,
            input_handler,
            cpus_per_model,
            gpus_per_model,
            custom_metrics,
            composite_metrics,
            native_metrics,
            weighted_native_metrics,
            PBT=PBT,
            PBT_replay_getter=PBT_replay_getter,
            seed=seed,
        )

    print(
        "\nResults:\n"
        + optimization_str
        + "\n"
        + optimization_results_string
        + "\n\n"
        + evaluation_string.format(*raw_values_list)
    )

    if not return_results_str:
        if return_crossval_models:
            return (
                best_trials,
                best_trials_fit if not skip_fit_evaluation else None,
                model_configs_df,
                crossval_model_info,
                crossval_input_data,
            )
        else:
            return best_trials, best_trials_fit if not skip_fit_evaluation else None, model_configs_df
    else:
        if return_crossval_models:
            if not return_unfilled:
                return (
                    best_trials,
                    best_trials_fit if not skip_fit_evaluation else None,
                    model_configs_df,
                    optimization_str
                    + "\n"
                    + optimization_results_string
                    + "\n\n"
                    + evaluation_string.format(*raw_values_list),
                    crossval_model_info,
                    crossval_input_data,
                )
            else:
                return (
                    best_trials,
                    best_trials_fit if not skip_fit_evaluation else None,
                    model_configs_df,
                    optimization_str + "\n" + optimization_results_string + "\n\n" + evaluation_string,
                    raw_values_list,
                    crossval_model_info,
                    crossval_input_data,
                )
        else:
            if not return_unfilled:
                return (
                    best_trials,
                    best_trials_fit if not skip_fit_evaluation else None,
                    model_configs_df,
                    optimization_str
                    + "\n"
                    + optimization_results_string
                    + "\n\n"
                    + evaluation_string.format(*raw_values_list),
                )
            else:
                return (
                    best_trials,
                    best_trials_fit if not skip_fit_evaluation else None,
                    model_configs_df,
                    optimization_str + "\n" + optimization_results_string + "\n\n" + evaluation_string,
                    raw_values_list,
                )


def evaluate_search_algorithm_test_step(
    analysis: tune.ExperimentAnalysis,
    optimize_name: str,
    optimize_op: Union[Literal["max"], Literal["min"]],
    search_space: tune_search_space_type,
    run_config_search_space: dict[str, run_config_search_space_entry_type],
    results_dir: str,
    inputs_split: list[np.ndarray],
    targets_split: list[np.ndarray],
    weights_split: list[np.ndarray],
    input_handler: OPTIMA.builtin.inputs.InputHandler,
    preprocessor: Any,
    custom_metrics: Optional[list[tuple[str, Callable]]] = None,
    composite_metrics: Optional[list[tuple[str, tuple[str, str], Callable]]] = None,
    overtraining_conditions: Optional[list] = None,
    write_results: bool = True,
    return_results_str: bool = False,
) -> None:
    """(unmaintained!) Performs the evaluation of one of an optimization step when running with option ``--test_search_algorithm``.

    This function performs the same evaluations done in ``evaluate_experiment`` to determine the best trial with the
    two evaluation methods but skips the crossvalidation and evaluation of the individual models.

    Parameters
    ----------
    analysis : tune.ExperimentAnalysis
        The ``tune.ExperimentAnalysis``-object extracted from the ``tune.ResultsGrid`` returned by the ``Tuner``.
    optimize_name : str
        Name of the target metric.
    optimize_op : Union[Literal["max"], Literal["min"]]
        Specifies if the target metric is to be maximized or minimized. Can be either ``'max'`` or ``'min'``.
    search_space : tune_search_space_type
        The tune search space provided to the Tuner.
    run_config_search_space : dict[str, run_config_search_space_entry_type]
        The search space as defined in the run-config.
    results_dir : str
        Path to the directory where the results are to be saved.
    inputs_split : list[np.ndarray]
        List containing the numpy array of input features for the training, validation and (if used) testing sets.
    targets_split : list[np.ndarray]
        List containing the numpy array of target labels for the training, validation and (if used) testing sets.
    weights_split : list[np.ndarray]
        List containing the numpy array of event weights for the training, validation and (if used) testing sets.
    input_handler : OPTIMA.builtin.inputs.InputHandler
        Instance of the ``preprocessing.InputHandler``-class
    preprocessor : Any
        The fitted scaler used to preprocess the input features that were used for training during the optimization.
    custom_metrics : Optional[list[tuple[str, Callable]]]
        A list of `custom metrics` as defined in the run-config. (Default value = None)
    composite_metrics : Optional[list[tuple[str, tuple[str, str], Callable]]]
        A list of `composite metrics` as defined in the run-config. (Default value = None)
    overtraining_conditions : Optional[list]
        A list of `overtraining conditions` as defined in the run-config. (Default value = None)
    write_results : bool
        If ``True``, the results are written to `results.txt` in ``results_dir``. (Default value = True)
    return_results_str : bool
        If ``True``, the results string that is printed to console is also returned. (Default value = False)
    """
    if overtraining_conditions is None:
        overtraining_conditions = []
    if composite_metrics is None:
        composite_metrics = []
    if custom_metrics is None:
        custom_metrics = []

    # save analysis to disk for later manual evaluation
    with open(os.path.join(results_dir, "analysis.pickle"), "wb") as file:
        pickle.dump(analysis, file)

    # build a list containing the names of all metrics, grouped together like [[train_loss, val_loss], [train_accuracy, val_accuracy], ...]
    metric_names = []
    optimize_name_included = False
    for metric, _ in custom_metrics:
        group = ("train_" + metric, "val_" + metric)
        metric_names.append(group)
        if optimize_name in group:
            optimize_name_included = True
    for metric, _, _ in composite_metrics:
        metric_names.append(metric)
        if metric == optimize_name:
            optimize_name_included = True
    if not optimize_name_included:
        metric_names = [optimize_name] + metric_names

    # get the results dataframes and remove all NaN and inf values
    dfs_dirty = analysis.fetch_trial_dataframes()
    dfs = clean_analysis_results(dfs_dirty, metric_names)

    # now also save the dataframes
    with open(os.path.join(results_dir, "dfs.pickle"), "wb") as file:
        pickle.dump(dfs, file)

    # go through dataframes and explicitly check if overtraining conditions are fulfilled, and add results (True/False)
    # as new column "overtrained"
    dfs_overtraining_checked = check_overtraining(dfs, overtraining_conditions)

    # produce two sets of plots showing the overall progress of the experiment, one set containing all trials as datapoints,
    # and one showing the evolution of the "best" trial; both as a function of time
    draw_total_progress(
        dfs_overtraining_checked,
        optimize_name,
        optimize_op,
        metric_names,
        figs_dir=results_dir,
        reject_overtrained=True,
    )


def scientific_rounding(value, err, notation="separate"):
    """Helper function to perform scientific rounding based on the provided uncertainty.

    Notation can be 'bracket', meaning 0.0123 +- 0.0234 will become 0.012(23), or 'separate' where the rounded value and
    error will be returned separately

    Parameters
    ----------
    value : _type_
        _description_
    err : _type_
        _description_
    notation : _type_
        _description_ (Default value = 'separate')
    """
    if abs(err) > 0:
        significant_digit = max(-int(np.floor(np.log10(abs(err)))), 0)
        error_digits = round(err * 10**significant_digit)
        if error_digits < 4:
            significant_digit += 1
            error_digits = round(err * 10**significant_digit)
        if notation == "bracket":
            value_rounded = "{{:.{}f}}({{}})".format(significant_digit).format(value, error_digits)
            return value_rounded
        elif notation == "separate":
            value_rounded = "{{:.{}f}}".format(significant_digit).format(value)
            err_rounded = "{{:.{}f}}".format(significant_digit).format(err)
            return value_rounded, err_rounded
    else:
        if notation == "bracket":
            return f"{value}(0)"
        elif notation == "separate":
            return value, err


def clean_analysis_results(dfs, metric_names):
    """_summary_.

    Parameters
    ----------
    dfs : _type_
        _description_
    metric_names : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    # ungroup the metric names
    metric_names_ungrouped = []
    for group in metric_names:
        if not isinstance(group, list) and not isinstance(group, tuple):
            metric_names_ungrouped.append(group)
        else:
            for metric in group:
                metric_names_ungrouped.append(metric)

    dfs_cleaned = {}
    for trial, df in dfs.items():
        df_cleaned = df.replace([np.inf, -np.inf], np.nan, inplace=False)  # first replace infs with NaNs
        df_cleaned.dropna(
            subset=metric_names_ungrouped, how="any", inplace=True
        )  # then drop all the rows containing NaNs
        df_cleaned.reset_index(drop=True, inplace=True)  # reindex to get rid of the gaps
        dfs_cleaned[trial] = df_cleaned

    return dfs_cleaned


def check_overtraining(dfs, overtraining_conditions):
    """_summary_.

    Parameters
    ----------
    dfs : _type_
        _description_
    overtraining_conditions : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """

    def _check_overtraining_for_df(df):
        """_summary_.

        Parameters
        ----------
        df : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        # skip if df is empty
        if len(df) == 0:
            return df

        df_overtraining_checked = copy.deepcopy(df)
        overtrained = np.zeros_like(df_overtraining_checked.index, dtype=bool)

        for _, input_metric_names, condition in overtraining_conditions:
            input_values = [df[input_name] for input_name in input_metric_names]
            overtrained += condition(*input_values)  # boolean addition is supported by numpy

        df_overtraining_checked["overtrained"] = overtrained

        return df_overtraining_checked

    if isinstance(dfs, dict):
        dfs_overtraining_checked = {}
        for trial, df in dfs.items():
            df_overtraining_checked = _check_overtraining_for_df(df)
            dfs_overtraining_checked[trial] = df_overtraining_checked
    elif isinstance(dfs, pd.DataFrame):
        dfs_overtraining_checked = _check_overtraining_for_df(dfs)
    else:
        raise TypeError

    return dfs_overtraining_checked


def draw_total_progress(dfs, optimize_name, optimize_op, metric_names, figs_dir=None, reject_overtrained=False):
    """_summary_.

    Parameters
    ----------
    dfs : _type_
        _description_
    optimize_name : _type_
        _description_
    optimize_op : _type_
        _description_
    metric_names : _type_
        can be grouped by giving list of lists or list of tuples -> groups will be plotted together in one diagram
    figs_dir : _type_
        _description_ (Default value = None)
    reject_overtrained : _type_
        _description_ (Default value = False)
    """
    if not isinstance(optimize_name, list):
        optimize_name = [optimize_name]
    if not isinstance(optimize_op, list):
        optimize_op = [optimize_op]

    # ungroup the metric names (to give e.g. both train_loss and val_loss their own columns)
    metric_names_ungrouped = []
    metric_names_grouped = []
    for group in metric_names:
        if not isinstance(group, list) and not isinstance(group, tuple):
            metric_names_ungrouped.append(group)
            metric_names_grouped.append([group])
        else:
            for metric in group:
                metric_names_ungrouped.append(metric)
            metric_names_grouped.append(group)

    # create a single large dataframe  and sort it by "timestamp"
    large_df = pd.concat(dfs.values(), ignore_index=True, sort=False)
    large_df = large_df.sort_values(by=["timestamp"], ignore_index=True)

    # get alpha values from the overtraining flag
    alpha_array = copy.deepcopy(
        large_df["overtrained"].to_numpy(dtype=np.float64)
    )  # need the copy here, otherwise we modify df
    alpha_array[alpha_array == True] = 0.2  # noqa: E712
    alpha_array[alpha_array == False] = 1.0  # noqa: E712

    for metric_group in metric_names_grouped:
        for metric in metric_group:
            plt.gcf().set_figheight(6)
            plt.gcf().set_figwidth(8)
            # plt.scatter(large_df["timestamp"]-start_time, large_df[metric], s=3., label=metric, alpha=alpha_array)
            plt.scatter(large_df.index, large_df[metric], s=3.0, label=metric, alpha=alpha_array)
        plt.title("Optimization overview: {}".format(", ".join(metric_group)))
        # plt.xlabel("runtime [s]")
        plt.xlabel("iterations")
        plt.legend()
        plt.gcf().set_figheight(6)
        plt.gcf().set_figwidth(8)
        plt.tight_layout()
        if figs_dir is not None:
            if not os.path.exists(os.path.join(figs_dir, "overview_plots")):
                os.makedirs(os.path.join(figs_dir, "overview_plots"))
            plt.savefig(os.path.join(figs_dir, "overview_plots", "{}.png".format("+".join(metric_group))), dpi=600)
        else:
            plt.show()
        plt.clf()

    # extract only those epochs that improved the optimization metrics
    for target_metric, target_op in zip(optimize_name, optimize_op):
        # calculate cumulative min/max for each target metric and remove duplicates (which only leaves entries which improved
        # the target metric)
        cumextr = large_df[target_metric].cummin() if target_op == "min" else large_df[target_metric].cummax()
        cumextr_index = cumextr.drop_duplicates().index

        # get the indices of large_df and replace all values that are not in cumext_index (i. e. those that did not result
        # in an improvement) with NaN, then frontfill the NaNs to get repeating indices
        repeating_indices = large_df.index.to_series().where(large_df.index.isin(cumextr_index))
        repeating_indices.fillna(method="ffill", inplace=True)

        # apply repeating indices to large_df to only have the entries that were improvements
        pruned_large_df = large_df.iloc[repeating_indices][metric_names_ungrouped]

        # we want to keep the original "timestamp" and indices, so reinsert them
        pruned_large_df.index = large_df.index
        pruned_large_df["timestamp"] = large_df["timestamp"]

        # plot progress for all metrics
        for metric_group in metric_names_grouped:
            for metric in metric_group:
                plt.gcf().set_figheight(6)
                plt.gcf().set_figwidth(8)
                # plt.plot(pruned_large_df["timestamp"]-start_time, pruned_large_df[metric], label=metric)
                plt.plot(pruned_large_df.index, pruned_large_df[metric], label=metric)
            plt.title("Optimization progress: {}, target: {}".format(", ".join(metric_group), target_metric))
            # plt.xlabel("runtime [s]")
            plt.xlabel("iterations")
            plt.legend()
            plt.gcf().set_figheight(6)
            plt.gcf().set_figwidth(8)
            plt.tight_layout()
            if figs_dir is not None:
                if not os.path.exists(os.path.join(figs_dir, "progress_plots")):
                    os.makedirs(os.path.join(figs_dir, "progress_plots"))
                plt.savefig(
                    os.path.join(
                        figs_dir,
                        "progress_plots",
                        target_metric if len(optimize_name) > 1 else "",
                        "{}.png".format("+".join(metric_group)),
                    ),
                    dpi=600,
                )
            else:
                plt.show()
            plt.clf()


def get_best_trials(dfs, optimize_name, optimize_op, metric_names, figs_dir=None, reject_overtrained=False):
    """_summary_.

    Parameters
    ----------
    dfs : _type_
        _description_
    optimize_name : _type_
        _description_
    optimize_op : _type_
        _description_
    metric_names : _type_
        can be grouped by giving list of lists or list of tuples -> groups will be plotted together in one diagram
    figs_dir : _type_
        _description_ (Default value = None)
    reject_overtrained : _type_
        _description_ (Default value = False)
    """
    if not isinstance(optimize_name, list):
        optimize_name = [optimize_name]
    if not isinstance(optimize_op, list):
        optimize_op = [optimize_op]

    # ungroup the metric names (to give e.g. both train_loss and val_loss their own columns)
    metric_names_ungrouped = []
    metric_names_grouped = []
    for group in metric_names:
        if not isinstance(group, list) and not isinstance(group, tuple):
            metric_names_ungrouped.append(group)
            metric_names_grouped.append([group])
        else:
            for metric in group:
                metric_names_ungrouped.append(metric)
            metric_names_grouped.append(group)

    best_trials = pd.DataFrame(
        index=optimize_name,
        columns=metric_names_ungrouped + ["trial", "best epoch", "best index", "best checkpoint"],
        dtype=np.float64,
    )
    best_trials.index.name = "target"
    for metric, op in zip(optimize_name, optimize_op):
        for trial, df in dfs.items():
            # skip if df is empty
            if len(df) == 0:
                continue

            # need to find the index of the best epoch because for PBT, epochs don't always increase monotonically
            if reject_overtrained:
                df_nonovertrained = df.where(df["overtrained"] == False)  # reject overtrained epochs  # noqa: E712
                best_index = df_nonovertrained[metric].idxmax() if op == "max" else df_nonovertrained[metric].idxmin()
            else:
                best_index = df[metric].idxmax() if op == "max" else df[metric].idxmin()

            # if every epoch is overtrained, best index will be NaN
            if not np.isnan(best_index):
                metric_best = df.iloc[best_index][metric]
                best_epoch = df.iloc[best_index]["training_iteration"]
                best_checkpoint = (
                    df.iloc[best_index]["iterations_since_restore"] - 1
                )  # when restoring during PBT, checkpoint numbering will be restarted from 0, overwriting previous checkpoints
                if (
                    metric_best > best_trials.loc[metric, metric]
                    if op == "max"
                    else metric_best < best_trials.loc[metric, metric]
                ) or np.isnan(best_trials.loc[metric, metric]):
                    best_trials.loc[[metric], metric_names_ungrouped] = df.loc[
                        best_index, metric_names_ungrouped
                    ].to_numpy()
                    best_trials.loc[[metric], ["trial", "best epoch", "best index", "best checkpoint"]] = [
                        trial,
                        best_epoch,
                        best_index,
                        best_checkpoint,
                    ]

    # plotting the evolution of the metrics for best trial
    for target_metric_name, best_trial, best_epoch, best_index in zip(
        optimize_name, best_trials["trial"], best_trials["best epoch"], best_trials["best index"]
    ):
        df = dfs[best_trial]
        alpha_array = copy.deepcopy(
            df["overtrained"].to_numpy(dtype=np.float64)
        )  # need the copy here, otherwise we modify df
        alpha_array[alpha_array == True] = 0.2  # noqa: E712
        alpha_array[alpha_array == False] = 1.0  # noqa: E712
        for metric_group in metric_names_grouped:
            for metric in metric_group:
                plt.gcf().set_figheight(6)
                plt.gcf().set_figwidth(8)
                plt.scatter(df["training_iteration"], df[metric], s=11.0, label=metric, alpha=alpha_array)
                plt.scatter(
                    best_epoch, df.iloc[int(best_index)][metric], s=40.0, marker="x", c="r"
                )  # need to use the index because for PBT, epochs don't always increase monotonically
            plt.title(f"target: {target_metric_name}")
            plt.xlabel("training iteration")
            plt.legend()
            plt.gcf().set_figheight(6)
            plt.gcf().set_figwidth(8)
            plt.tight_layout()
            if figs_dir is not None:
                if not os.path.exists(
                    os.path.join(
                        figs_dir,
                        target_metric_name if len(optimize_name) > 1 else "",
                        "best_value",
                        "plots",
                        "optimization",
                    )
                ):
                    os.makedirs(
                        os.path.join(
                            figs_dir,
                            target_metric_name if len(optimize_name) > 1 else "",
                            "best_value",
                            "plots",
                            "optimization",
                        )
                    )
                plt.savefig(
                    os.path.join(
                        figs_dir,
                        target_metric_name if len(optimize_name) > 1 else "",
                        "best_value",
                        "plots",
                        "optimization",
                        "+".join(metric_group) + ".png",
                    ),
                    dpi=600,
                )
            else:
                plt.show()
            plt.clf()

    return best_trials


def get_best_trials_from_fit(
    run_config: ModuleType,
    dfs,
    optimize_name,
    optimize_op,
    metric_names,
    fit_function="custom_2",
    fit_xtol=1e-5,
    fit_maxfev=10000,
    figs_dir=None,
    overtraining_conditions=None,
    reject_overtrained=False,
    min_R_squared=0.9,
):
    """_summary_.

    Parameters
    ----------
    run_config : ModuleType
        Reference to the imported run-config file.
    dfs : _type_
        dict of pandas dataframes
    optimize_name : _type_
        string or list of strings
    optimize_op : _type_
        string ('min'/'max') or list of strings of same length as metric_name
    metric_names : _type_
        _description_
    fit_function : _type_
        defining which function should be used for fitting. Can either be single value or list of same length (Default value = 'custom_2')
    fit_xtol : _type_
        _description_ (Default value = 1e-5)
    fit_maxfev : _type_
        _description_ (Default value = 10000)
    figs_dir : _type_
        _description_ (Default value = None)
    overtraining_conditions : _type_
        _description_ (Default value = None)
    reject_overtrained : _type_
        _description_ (Default value = False)
    min_R_squared : _type_
        _description_ (Default value = 0.9)
    """

    def _custom_fit_function(x, A, a, c, B, b, C, D, const):
        """_summary_.

        Parameters
        ----------
        x : _type_
            _description_
        A : _type_
            _description_
        a : _type_
            _description_
        c : _type_
            _description_
        B : _type_
            _description_
        b : _type_
            _description_
        C : _type_
            _description_
        D : _type_
            _description_
        const : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        return A * np.exp(-a / 1e-4 * (x - c) ** 2) + B * np.exp(-b / 100 * x) + C * x + D * x * x + const

    def _custom_fit_function_2(x, A, B, C, D, const):
        """_summary_.

        Parameters
        ----------
        x : _type_
            _description_
        A : _type_
            _description_
        B : _type_
            _description_
        C : _type_
            _description_
        D : _type_
            _description_
        const : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        return A / x**2 + B / x + C * x**2 + D * x + const

    def _custom_fit_function_3(x, A, a, c, B, b, C, D, E, F, const):
        """_summary_.

        Parameters
        ----------
        x : _type_
            _description_
        A : _type_
            _description_
        a : _type_
            _description_
        c : _type_
            _description_
        B : _type_
            _description_
        b : _type_
            _description_
        C : _type_
            _description_
        D : _type_
            _description_
        E : _type_
            _description_
        F : _type_
            _description_
        const : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        return (
            A * np.exp(-a / 1e-4 * (x - c) ** 2)
            + B * np.exp(-b / 100 * x)
            + C * x
            + D * x * x
            + E / x**2
            + F / x
            + const
        )

    def _crossval_fit(fit_function, x, y, bounds=(-np.inf, np.inf), p0=None, **kwargs):
        """Function to perform a crossvalidation-like fit to assess the goodness of fit.

        It applies scipy.optimize's curve_fit multiple times to a subset of the data (using kfold splitting),
        calculates the average deviation between the fit function and the fitting and testing data, gets the ratio between
        the two errors for each splitting, and then looks at the median value. if that is > 3, the fit is rejected,
        otherwise the fit is repeated on the full dataset and the fit parameters are returned

        Parameters
        ----------
        fit_function : _type_
            _description_
        x : _type_
            _description_
        y : _type_
            _description_
        bounds : _type_
            _description_ (Default value = (-np.inf, np.inf))
        p0 : _type_
            _description_ (Default value = None)
        **kwargs : _type_
            _description_
        """
        fit_errors = []
        test_errors = []
        error_ratios = []
        fit_R_squared = []
        kfold = KFold(n_splits=5, shuffle=True, random_state=1234)
        for fit_indices, test_indices in kfold.split(x):
            x_fit = x[fit_indices]
            x_test = x[test_indices]
            y_fit = y[fit_indices]
            y_test = y[test_indices]
            parameters, covariance = curve_fit(fit_function, x_fit, y_fit, bounds=bounds, p0=p0, **kwargs)
            fitted_func = lambda x, p=parameters: fit_function(x, *p)

            y_fit_pred = fitted_func(x_fit)
            y_test_pred = fitted_func(x_test)
            mean_abs_fit_error = np.mean(np.abs(y_fit_pred - y_fit))
            mean_abs_test_error = np.mean(np.abs(y_test_pred - y_test))
            error_fraction = mean_abs_test_error / mean_abs_fit_error
            fit_errors.append(mean_abs_fit_error)
            test_errors.append(mean_abs_test_error)
            error_ratios.append(error_fraction)

            R_squared_fit = np.sum((y_fit - y_fit_pred) ** 2) / np.sum((y_fit - np.mean(y_fit)) ** 2)
            fit_R_squared.append(R_squared_fit)

        parameters, covariance = curve_fit(fit_function, x, y, bounds=bounds, p0=p0, **kwargs)

        fitted_func = lambda x: fit_function(x, *parameters)
        R_squared = 1 - np.sum((y - fitted_func(x)) ** 2) / np.sum((y - np.mean(y)) ** 2)

        if R_squared < min_R_squared:  # np.median(error_ratios) > 3.:
            return None, None
        else:
            # plt.scatter(x, y, s=11.)
            # xs_plot = np.linspace(x.iloc[0], x.iloc[-1], 1000)
            # ys_plot = fitted_func(xs_plot)
            # plt.plot(xs_plot, ys_plot, color='blue')
            # plt.title("MedER: {:.4f}, MedFE: {:.5f}, MedTE: {:.5f}, \n"
            #           "MedRS: {:.4f}, MedRSF: {:.4f}".format(np.median(error_ratios),
            #                                                  np.median(fit_errors),
            #                                                  np.median(test_errors),
            #                                                  np.median(R_squared),
            #                                                  np.median(fit_R_squared)))
            # plt.show()
            return parameters, covariance

    def _fit_and_plot(
        df,
        metric_name,
        fit_function,
        xtol,
        maxfev,
        metric_op=None,
        return_at_x=None,
        color="C0",
        plot=True,
        figs_dir=None,
        reject_overtrained=False,
        overtraining_conditions=None,
        crossval=False,
        return_plotting_df=False,
    ):
        """Either metric_op or return_at_x must not be None!.

        Parameters
        ----------
        df : _type_
            _description_
        metric_name : _type_
            _description_
        fit_function : _type_
            _description_
        xtol : _type_
            _description_
        maxfev : _type_
            _description_
        metric_op : _type_
            _description_ (Default value = None)
        return_at_x : _type_
            if given, will return the value of the fit function at this point instead of the extreme value (Default value = None)
        color : _type_
            _description_ (Default value = "C0")
        plot : _type_
            _description_ (Default value = True)
        figs_dir : _type_
            _description_ (Default value = None)
        reject_overtrained : _type_
            _description_ (Default value = False)
        overtraining_conditions : _type_
            _description_ (Default value = None)
        crossval : _type_
            _description_ (Default value = False)
        return_plotting_df : _type_
            _description_ (Default value = False)
        """

        def _fit(metric_to_fit, metric_to_fit_op=None):
            """Helper function that fits the fitting function to a metric in df.

            Parameters
            ----------
            metric_to_fit : _type_
                _description_
            metric_to_fit_op : _type_
                _description_ (Default value = None)
            """
            if hasattr(run_config, "fit_function"):
                fitted_func = run_config.fit_function(df, metric_to_fit, metric_to_fit_op, overtraining_conditions)
            elif fit_function == "custom":
                # fewer data points than twice the number of function parameters
                if len(df) < 16:
                    return

                # fit curve to metric; choose initial values to be exponential convergence to the observed extreme value
                if metric_to_fit_op is not None:
                    best_metric_guess = (
                        df[metric_to_fit].max() if metric_to_fit_op == "max" else df[metric_to_fit].min()
                    )
                    best_epoch_guess = (
                        df.loc[df[metric_to_fit].idxmax()]["training_iteration"]
                        if metric_to_fit_op == "max"
                        else df.loc[df[metric_to_fit].idxmin()]["training_iteration"]
                    )
                else:
                    # assume the progress is in the correct direction
                    progress = df[metric_to_fit].iloc[-1] - df[metric_to_fit].iloc[0]
                    best_metric_guess = df[metric_to_fit].max() if progress > 0 else df[metric_to_fit].min()
                    best_epoch_guess = df["training_iteration"].iloc[-1]
                metric_first = df[metric_to_fit][0]
                B_init = -(best_metric_guess - metric_first)
                b_init = 5 * 100 / (best_epoch_guess)
                const_init = best_metric_guess
                init = [0, 0, 0, B_init, b_init, 0, 0, const_init]
                # f = A * exp(-a * (x-c)^2) + B * exp(-bx) + Cx + Dx^2 + const
                # --> make sure the exponentials are always getting smaller with larger x!
                bounds = (
                    [-np.inf, 0, -np.inf, -np.inf, 0, -np.inf, -np.inf, -np.inf],
                    [np.inf, np.inf, 0, np.inf, np.inf, np.inf, np.inf, np.inf],
                )

                if crossval:
                    parameters, covariance = _crossval_fit(
                        _custom_fit_function,
                        df["training_iteration"],
                        df[metric_to_fit],
                        bounds=bounds,
                        p0=init,
                        xtol=xtol,
                        maxfev=maxfev,
                    )
                    if parameters is None:
                        return
                else:
                    parameters, covariance = curve_fit(
                        _custom_fit_function,
                        df["training_iteration"],
                        df[metric_to_fit],
                        bounds=bounds,
                        p0=init,
                        xtol=xtol,
                        maxfev=maxfev,
                    )
                fitted_func = lambda x: _custom_fit_function(x, *parameters)
            elif fit_function == "custom_2":
                # fewer data points than twice the number of function parameters
                if len(df) < 10:
                    return
                if crossval:
                    parameters, covariance = _crossval_fit(
                        _custom_fit_function_2, df["training_iteration"], df[metric_to_fit], xtol=xtol, maxfev=maxfev
                    )
                    if parameters is None:
                        return
                else:
                    parameters, covariance = curve_fit(
                        _custom_fit_function_2, df["training_iteration"], df[metric_to_fit], xtol=xtol, maxfev=maxfev
                    )
                fitted_func = lambda x: _custom_fit_function_2(x, *parameters)
            elif fit_function == "custom_3":
                # fewer data points than twice the number of function parameters
                if len(df) < 20:
                    return

                # fit curve to metric; choose initial values to be exponential convergence to the observed extreme value
                if metric_to_fit_op is not None:
                    best_metric_guess = (
                        df[metric_to_fit].max() if metric_to_fit_op == "max" else df[metric_to_fit].min()
                    )
                    best_epoch_guess = (
                        df.loc[df[metric_to_fit].idxmax()]["training_iteration"]
                        if metric_to_fit_op == "max"
                        else df.loc[df[metric_to_fit].idxmin()]["training_iteration"]
                    )
                else:
                    best_metric_guess = df[metric_to_fit].median()
                    best_epoch_guess = df["training_iteration"].iloc[-1]
                metric_first = df[metric_to_fit][0]
                B_init = -(best_metric_guess - metric_first)
                b_init = 5 * 100 / (best_epoch_guess)
                const_init = best_metric_guess
                init = [0, 0, 0, B_init, b_init, 0, 0, 0, 0, const_init]
                # f = A * exp(-a * (x-c)^2) + B * exp(-bx) + Cx + Dx^2 + const
                # --> make sure the exponentials are always getting smaller with larger x!
                bounds = (
                    [-np.inf, 0, -np.inf, -np.inf, 0, -np.inf, -np.inf, -np.inf, -np.inf, -np.inf],
                    [np.inf, np.inf, 0, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf],
                )

                if crossval:
                    parameters, covariance = _crossval_fit(
                        _custom_fit_function_3,
                        df["training_iteration"],
                        df[metric_to_fit],
                        bounds=bounds,
                        p0=init,
                        xtol=xtol,
                        maxfev=maxfev,
                    )
                    if parameters is None:
                        return
                else:
                    parameters, covariance = curve_fit(
                        _custom_fit_function_3,
                        df["training_iteration"],
                        df[metric_to_fit],
                        bounds=bounds,
                        p0=init,
                        xtol=xtol,
                        maxfev=maxfev,
                    )
                fitted_func = lambda x: _custom_fit_function_3(x, *parameters)
            else:
                if crossval:
                    parameters, covariance = _crossval_fit(
                        fit_function, df["training_iteration"], df[metric_to_fit], xtol=xtol, maxfev=maxfev
                    )
                    if parameters is None:
                        return
                else:
                    parameters, covariance = curve_fit(
                        fit_function, df["training_iteration"], df[metric_to_fit], xtol=xtol, maxfev=maxfev
                    )
                fitted_func = lambda x: fit_function(x, *parameters)

            return fitted_func

        if len(df[~df["overtrained"]]) == 0:
            return None, None, None

        fitted_func = _fit(metric_name, metric_op)
        if fitted_func is None:
            return None, None, None

        if plot:
            # create a df that contains all values for plotting the fit
            df_for_plotting = pd.DataFrame()
            df_for_plotting["training_iteration"] = np.linspace(
                df["training_iteration"].iloc[0], df["training_iteration"].iloc[-1], 1000
            )
            df_for_plotting[metric_name] = fitted_func(df_for_plotting["training_iteration"])

            # when overtraining conditions are given, also fit all metrics necessary to evaluate the overtraining conditions
            # using the fit values
            if overtraining_conditions is not None:
                df_for_plotting.loc[:, "overtrained"] = 0.0

                # iterate over all overtraining conditions to get a full set of metrics that need to be fitted
                metrics_for_overtraining_check = []
                for _, input_metric_names, _ in overtraining_conditions:
                    metrics_for_overtraining_check += list(input_metric_names)
                metrics_for_overtraining_check = list(set(metrics_for_overtraining_check))  # remove duplicate entries
                if metric_name in metrics_for_overtraining_check:
                    metrics_for_overtraining_check.remove(
                        metric_name
                    )  # remove metric_name as we already have done the fit for that

                # iterate over all metrics for the overtraining conditions and apply a fit to each, then fill the dfs
                for metric_to_fit in metrics_for_overtraining_check:
                    fitted_func_overtraining = _fit(metric_to_fit)

                    # when one of the metrics could not be fitted well, we'll skip this trial (one could also fall back
                    # to simply checking the overtraining flag of the raw values, but that would not be consistent with
                    # the over trials)
                    if fitted_func_overtraining is None:
                        return None, None, None

                    df_for_plotting[metric_to_fit] = fitted_func_overtraining(df_for_plotting["training_iteration"])

                # update the overtrained column using the fit values
                df_for_plotting = check_overtraining(df_for_plotting, overtraining_conditions)

                # plot the raw metric values
                alpha_array = copy.deepcopy(df["overtrained"].to_numpy(dtype=np.float64))
                alpha_array[alpha_array == True] = 0.2  # noqa: E712
                alpha_array[alpha_array == False] = 1.0  # noqa: E712
                plt.gcf().set_figheight(6)
                plt.gcf().set_figwidth(8)
                plt.scatter(
                    df["training_iteration"], df[metric_name], s=11.0, color=color, alpha=alpha_array, label=metric_name
                )
                plt.xlabel("training iteration")

        # find the best epoch according to the fit (while checking for overtraining, if requested)
        if return_at_x is None:
            fit_values_epochs = fitted_func(df["training_iteration"])

            # when overtraining conditions are given, also fit all metrics necessary to evaluate the overtraining conditions
            # using the fit values
            if overtraining_conditions is not None:
                # build a new df and fill all necessary columns with fit values; also create a df with intermediate values
                # when plotting is requested
                df_from_fit = df.copy()
                df_from_fit[metric_name] = fit_values_epochs
                df_from_fit.loc[:, "overtrained"] = 0.0

                # iterate over all overtraining conditions to get a full set of metrics that need to be fitted
                metrics_for_overtraining_check = []
                for _, input_metric_names, _ in overtraining_conditions:
                    metrics_for_overtraining_check += list(input_metric_names)
                metrics_for_overtraining_check = list(set(metrics_for_overtraining_check))  # remove duplicate entries
                if metric_name in metrics_for_overtraining_check:
                    metrics_for_overtraining_check.remove(
                        metric_name
                    )  # remove metric_name as we already have done the fit for that

                # iterate over all metrics for the overtraining conditions and apply a fit to each, then fill the dfs
                for metric_to_fit in metrics_for_overtraining_check:
                    fitted_func_overtraining = _fit(metric_to_fit)

                    # when one of the metrics could not be fitted well, we'll skip this trial (one could also fall back
                    # to simply checking the overtraining flag of the raw values, but that would not be consistent with
                    # the other trials)
                    if fitted_func_overtraining is None:
                        return None, None, None

                    df_from_fit[metric_to_fit] = fitted_func_overtraining(df_from_fit["training_iteration"])

                # update the overtrained column using the fit values
                df_from_fit = check_overtraining(df_from_fit, overtraining_conditions)

                # replace values for overtrained epochs with NaN --> will never be extremum
                fit_values_epochs = fit_values_epochs.where(df_from_fit["overtrained"] == False)  # noqa: E712

            # when no overtraining conditions are given, but reject_overtrained is True, then check the overtraining
            # conditions using the raw metric values (by looking at the "overtrained" column)
            elif reject_overtrained:
                # replace values for overtrained epochs with NaN --> will never be extremum
                fit_values_epochs = fit_values_epochs.where(df["overtrained"] == False)  # noqa: E712

            # find the extremum; need to use the indices because for PBT, epochs don't always increase monotonically
            best_index_fit = fit_values_epochs.idxmax() if metric_op == "max" else fit_values_epochs.idxmin()
            if np.isnan(best_index_fit):
                return None, None, None  # if every epoch is overtrained, best index will be NaN
            best_epoch_fit = df.iloc[best_index_fit]["training_iteration"]
            best_checkpoint_fit = df.iloc[best_index_fit]["iterations_since_restore"] - 1
            best_metric_fit = fit_values_epochs.iloc[best_index_fit]
            if plot:
                # plot the data
                plt.scatter(best_epoch_fit, best_metric_fit, s=40.0, marker="x", c="r")

                # plot the fit; when the overtraining conditions are given, use the created plotting df that includes
                # "continous" overtrained flag so that the plotted line can be colored accordingly
                if overtraining_conditions:
                    # get indices where overtraining label changes value and the values it changes to
                    diffs = df_for_plotting["overtrained"][df_for_plotting["overtrained"].diff() != 0]
                    diff_indices = diffs.index.tolist()
                    diff_values = diffs.values.tolist()

                    for i, (diff_index, diff_value) in enumerate(zip(diff_indices, diff_values)):
                        if i + 1 == len(diff_indices):
                            iterations = df_for_plotting["training_iteration"][diff_index:]
                            metrics = df_for_plotting[metric_name][diff_index:]
                        else:
                            next_diff_index = diff_indices[i + 1]
                            iterations = df_for_plotting["training_iteration"][diff_index:next_diff_index]
                            metrics = df_for_plotting[metric_name][diff_index:next_diff_index]

                        if diff_value is False:
                            alpha = 1.0
                        else:
                            alpha = 0.2

                        label = f"{metric_name} fit" if i == 0 else None
                        plt.plot(iterations, metrics, color=color, alpha=alpha, label=label)
                else:
                    plt.plot(df_for_plotting["training_iteration"], df_for_plotting[metric_name], color=color)

                if figs_dir is not None:
                    if not os.path.exists(figs_dir):
                        os.makedirs(figs_dir)
                    plt.gcf().set_figheight(6)
                    plt.gcf().set_figwidth(8)
                    plt.tight_layout()
                    plt.savefig(figs_dir, dpi=600)
                    plt.clf()
            return best_epoch_fit, best_checkpoint_fit, best_metric_fit
        else:
            if plot:
                if overtraining_conditions:
                    # get indices where overtraining label changes value and the values it changes to
                    diffs = df_for_plotting["overtrained"][df_for_plotting["overtrained"].diff() != 0]
                    diff_indices = diffs.index.tolist()
                    diff_values = diffs.values.tolist()

                    for i, (diff_index, diff_value) in enumerate(zip(diff_indices, diff_values)):
                        if i + 1 == len(diff_indices):
                            iterations = df_for_plotting["training_iteration"][diff_index:]
                            metrics = df_for_plotting[metric_name][diff_index:]
                        else:
                            next_diff_index = diff_indices[i + 1]
                            iterations = df_for_plotting["training_iteration"][diff_index:next_diff_index]
                            metrics = df_for_plotting[metric_name][diff_index:next_diff_index]

                        if diff_value is False:
                            alpha = 1.0
                        else:
                            alpha = 0.2

                        label = f"{metric_name} fit" if i == 0 else None
                        plt.plot(iterations, metrics, color=color, alpha=alpha, label=label)
                else:
                    plt.plot(
                        df_for_plotting["training_iteration"],
                        df_for_plotting[metric_name],
                        color=color,
                        label=f"{metric_name} fit",
                    )

                if figs_dir is not None:
                    if not os.path.exists(figs_dir):
                        os.makedirs(figs_dir)
                    plt.gcf().set_figheight(6)
                    plt.gcf().set_figwidth(8)
                    plt.tight_layout()
                    plt.savefig(figs_dir, dpi=600)
                    plt.clf()
            return fitted_func(return_at_x)

    if not isinstance(optimize_name, list):
        optimize_name = [optimize_name]
    if not isinstance(optimize_op, list):
        optimize_op = [optimize_op]

    # ungroup the metric names (to give e.g. both train_loss and val_loss their own columns)
    metric_names_ungrouped = []
    metric_names_grouped = []
    for group in metric_names:
        if not isinstance(group, list) and not isinstance(group, tuple):
            metric_names_ungrouped.append(group)
            metric_names_grouped.append([group])
        else:
            for metric in group:
                metric_names_ungrouped.append(metric)
            metric_names_grouped.append(group)

    fit_best = pd.DataFrame(
        index=optimize_name, columns=["trial", "best epoch", "best checkpoint", "best metric fit"], dtype=np.float64
    )
    for metric, op in zip(optimize_name, optimize_op):
        for trial, df in dfs.items():
            # skip if df is empty
            if len(df) == 0:
                continue

            best_epoch_fit, best_checkpoint_fit, best_metric_fit = _fit_and_plot(
                df,
                metric,
                fit_function,
                fit_xtol,
                fit_maxfev,
                metric_op=op,
                plot=False,
                reject_overtrained=reject_overtrained,
                overtraining_conditions=overtraining_conditions,
                crossval=True,
            )
            if best_epoch_fit is None:
                continue  # can be None if every epoch is overtrained or NaN
            if (
                best_metric_fit > fit_best.loc[metric, "best metric fit"]
                if op == "max"
                else best_metric_fit < fit_best.loc[metric, "best metric fit"]
            ) or np.isnan(fit_best.loc[metric, "best metric fit"]):
                fit_best.loc[metric] = [trial, best_epoch_fit, best_checkpoint_fit, best_metric_fit]

    # for all the best trials, now also fit the remaining metrics
    metrics_fit_best = pd.DataFrame(
        index=optimize_name,
        columns=metric_names_ungrouped + ["trial", "best epoch", "best checkpoint"],
        dtype=np.float64,
    )
    metrics_fit_best.index.name = "target"
    for target_metric_name in optimize_name:
        trial, epoch, checkpoint_num, _ = fit_best.loc[target_metric_name]
        if not isinstance(trial, str):
            return  # no fit succeeded
        for group in metric_names_grouped:
            for metric, plot_color in zip(group, [f"C{i}" for i in range(10)]):
                df = dfs[trial]
                fit_value = _fit_and_plot(
                    df,
                    metric,
                    fit_function,
                    fit_xtol,
                    fit_maxfev,
                    return_at_x=epoch,
                    color=plot_color,
                    overtraining_conditions=overtraining_conditions,
                )
                plt.gcf().set_figheight(6)
                plt.gcf().set_figwidth(8)
                plt.plot(epoch, fit_value, "rx")
                metrics_fit_best.loc[target_metric_name, metric] = fit_value
            plt.title(f"target: {target_metric_name}")
            plt.legend()
            plt.gcf().set_figheight(6)
            plt.gcf().set_figwidth(8)
            plt.tight_layout()
            if figs_dir is not None:
                if not os.path.exists(
                    os.path.join(
                        figs_dir,
                        target_metric_name if len(optimize_name) > 1 else "",
                        "best_fit",
                        "plots",
                        "optimization",
                    )
                ):
                    os.makedirs(
                        os.path.join(
                            figs_dir,
                            target_metric_name if len(optimize_name) > 1 else "",
                            "best_fit",
                            "plots",
                            "optimization",
                        )
                    )
                plt.savefig(
                    os.path.join(
                        figs_dir,
                        target_metric_name if len(optimize_name) > 1 else "",
                        "best_fit",
                        "plots",
                        "optimization",
                        "+".join(group) + ".png",
                    ),
                    dpi=600,
                )
            else:
                plt.show()
            plt.clf()
        metrics_fit_best.loc[target_metric_name, ["trial", "best epoch", "best checkpoint"]] = [
            trial,
            epoch,
            checkpoint_num,
        ]

    return metrics_fit_best


def calc_native_metric(
    run_config: ModuleType,
    native_metric: Any,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sample_weight: Optional[np.ndarray] = None,
) -> Union[int, float]:
    """Calculates the value of a native (stateful) metric for the provided targets and predictions.

    The type of metric provided is assumed to correspond to the backend set in ``model_type`` in the `run-config`. This
    is not verified.

    Before and after the calculation, the state of the metric is reset (if necessary).

    Parameters
    ----------
    run_config : ModuleType
        Reference to the imported run-config file.
    native_metric : Any
        The native metric.
    y_true : np.ndarray
        Numpy array of target labels.
    y_pred : np.ndarray
        Numpy array of model predictions
    sample_weight : Optional[np.ndarray]
        Numpy array of sample weights. (Default value = None)

    Returns
    -------
    Union[int, float]
        The value of the native metric.
    """
    if run_config.model_type == "Keras":
        native_metric.reset_state()
        native_metric.update_state(y_true, y_pred, sample_weight=sample_weight)
        result = native_metric.result().numpy()
        native_metric.reset_state()
        return result
    elif run_config.model_type == "Lightning":
        y_true = y_true.copy()
        y_true_tensor = torch.from_numpy(y_true).type(torch.float)
        y_pred_tensor = torch.from_numpy(y_pred).type(torch.float)
        metric = native_metric(y_pred_tensor, y_true_tensor).cpu().detach().numpy()
        return metric
