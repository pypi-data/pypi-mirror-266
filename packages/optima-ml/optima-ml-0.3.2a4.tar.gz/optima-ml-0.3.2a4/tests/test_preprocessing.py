# -*- coding: utf-8 -*-
"""Collection of unit tests related to the loading, splitting and preprocessing of the input data; both core and built-in."""
import os
from functools import partial

import numpy as np

import pytest
import ray

from .context import inputs, builtin_inputs
from . import config as run_config


def get_input_handler():
    return builtin_inputs.InputHandler(run_config)


def test_input_handler():
    # get the input handler
    input_handler = get_input_handler()
    assert input_handler.get_vars() == run_config.input_vars
    for var, scaling in input_handler.get_nonlinear_scaling().items():
        assert scaling == run_config.input_scaling[var]

    # set a subset of input variables,
    small_var_set = run_config.input_vars[:5]
    input_handler.set_vars(small_var_set)
    assert input_handler.get_vars() == small_var_set
    for var, scaling in input_handler.get_nonlinear_scaling().items():
        assert scaling == run_config.input_scaling[var]

    # test the copy
    input_handler_copy = input_handler.copy()
    assert input_handler.get_vars() == input_handler_copy.get_vars()
    assert input_handler.get_nonlinear_scaling() == input_handler_copy.get_nonlinear_scaling()


def test_dummy_scaler():
    # get a dummy scaler
    dummy_scaler = builtin_inputs.DummyScaler()
    pseudo_data = np.array([1, 2, 3, 4])
    pseudo_weights = np.ones((4,))
    dummy_scaler.fit(pseudo_data, sample_weight=pseudo_weights)
    assert (pseudo_data == dummy_scaler.transform(pseudo_data)).all()


def test_manual_scaler():
    input_handler = get_input_handler()
    manual_scaler = builtin_inputs.ManualScaler(input_handler)

    assert len(input_handler.get_vars()) == 13
    pseudo_data = np.array([[1000., 1., 0., 100., 0., 1., 10., -2., 1., 1., 1., 100., -2.]])
    pseudo_weights = np.ones((1,))
    manual_scaler.fit(pseudo_data, sample_weight=pseudo_weights)
    assert (manual_scaler.transform(pseudo_data) == np.array([[3., 1., 0., 2., 0, 1., 1., -2., 0., 1., 1., 2., -2.]])).all()


def test_custom_manual_plus_standard_scaler():
    input_handler = get_input_handler()
    scaler = builtin_inputs.CustomManualPlusStandardScaler(input_handler)

    # constant values should be shifted to zero
    pseudo_data = np.array(3 * [[1000., 1., 0., 100., 0., 1., 10., -2., 1., 1., 1., 100., -2.]])
    pseudo_weights = np.ones((3,))
    scaler.fit(pseudo_data, sample_weight=pseudo_weights)
    scaled_pseudo_data = np.array(3*[[0., 0., 0., 0., 0, 0., 0., 0., 0., 0., 0., 0., 0.]])
    assert (scaler.transform(pseudo_data) == scaled_pseudo_data).all()

    # now with simple pseudo data
    pseudo_data = np.array(
        [
            [1000., 2., -2., 1000., 0., 0., 1000., 2., 10., 2., -2., 10., 0.],
            [100., 1., -1., 100., 1., 1., 100., 1., 100., 1., -1., 100., -1.],
            [10., 0., 0., 10., 2., 2., 10., 0., 1000., 0., 0., 1000., -2.],
        ]
    )
    x = np.sqrt(3 / 2)
    scaled_pseudo_data = np.array(
        [
            [x, x, -x, x, -x, -x, x, x, -x, x, -x, -x, x],
            [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
            [-x, -x, x, -x, x, x, -x, -x, x, -x, x, x, -x],
        ]
    )
    scaler.fit(pseudo_data, sample_weight=pseudo_weights)
    assert (scaler.transform(pseudo_data) == scaled_pseudo_data).all()

    # test sample weights
    pseudo_weights = np.array([1., 1., 0])
    scaled_pseudo_data = np.array(
        [
            [1, 1, -1, 1, -1, -1, 1, 1, -1, 1, -1, -1, 1],
            [-1, -1, 1, -1, 1, 1, -1, -1, 1, -1, 1, 1, -1],
            [-3, -3, 3, -3, 3, 3, -3, -3, 3, -3, 3, 3, -3],
        ]
    )
    scaler.fit(pseudo_data, sample_weight=pseudo_weights)
    assert (scaler.transform(pseudo_data) == scaled_pseudo_data).all()

    # test saving and reloading
    scaler_path = "temp_scaler.pickle"
    scaler.save(scaler_path)
    del scaler
    with pytest.raises(UnboundLocalError):
        scaler.transform(pseudo_data)
    scaler = builtin_inputs.CustomManualPlusStandardScaler(input_handler)
    with pytest.raises(AssertionError):
        scaler.transform(pseudo_data)
    scaler.load(scaler_path)
    assert (scaler.transform(pseudo_data) == scaled_pseudo_data).all()
    os.remove("temp_scaler.pickle")


def test_load_input_data():
    input_handler = get_input_handler()

    # load test dataset of 10000 events, 5000 signal and 5000 background. 13 input variables are set in test config.
    (inputs,
     targets,
     weights,
     normalized_weights,
     event_nums) = builtin_inputs.get_inputs(run_config,
                                                    nevts=run_config.max_num_events,
                                                    input_vars_list=input_handler.get_vars())
    # verify shapes
    nevents = 10000
    assert inputs.shape == (nevents, 13)
    assert targets.shape == (nevents, 1)
    assert weights.shape == (nevents,)
    assert normalized_weights.shape == (nevents,)
    assert event_nums.shape == (nevents,)

    # verify first few entries
    assert np.max(inputs[:2, :2] - np.array([[118.25695, 1.89344], [153.33139, 3.37611]])) < 1e-5
    assert (targets[:5, 0] == np.array([0., 1., 1., 1., 1.])).all()
    assert np.max(weights[:5] - np.array([3.34210e-4, 1.26920e-4, 1.10627e-4, 9.5176e-5, 1.11107e-4])) < 1e-9
    assert np.max(normalized_weights[:5] - np.array([0.916951, 1.23007,  1.07217,  0.92242,  1.07682])) < 1e-5
    assert (event_nums[:5] == np.array([2146094, 1273346, 3395091, 855136, 2947049])).all()

    # verify nevts
    nevents_list = [10000, 30, (5000, 5000), (30, 30), (30, 10)]
    for nevents in nevents_list:
        (inputs,
         targets,
         weights,
         normalized_weights,
         event_nums) = builtin_inputs.get_inputs(run_config,
                                                        nevts=nevents,
                                                        input_vars_list=input_handler.get_vars())
        if isinstance(nevents, int):
            num = nevents
        else:
            num = nevents[0] + nevents[1]
        assert inputs.shape == (num, 13)
        assert targets.shape == (num, 1)
        assert weights.shape == (num,)
        assert normalized_weights.shape == (num,)
        assert event_nums.shape == (num,)

        if isinstance(nevents, tuple):
            for i in range(2):
                assert inputs[targets[:, 0] == i].shape == (nevents[1-i], 13)
                assert targets[targets[:, 0] == i].shape == (nevents[1-i], 1)
                assert weights[targets[:, 0] == i].shape == (nevents[1-i],)
                assert normalized_weights[targets[:, 0] == i].shape == (nevents[1-i],)
                assert event_nums[targets[:, 0] == i].shape == (nevents[1-i],)

    # verify input variables
    nevents = 10000
    (inputs,
     targets,
     weights,
     normalized_weights,
     event_nums) = builtin_inputs.get_inputs(run_config,
                                                    nevts=run_config.max_num_events,
                                                    input_vars_list=run_config.input_vars[:5])
    # verify shapes
    assert inputs.shape == (nevents, 5)
    assert targets.shape == (nevents, 1)
    assert weights.shape == (nevents,)
    assert normalized_weights.shape == (nevents,)
    assert event_nums.shape == (nevents,)

    # verify first few entries
    assert np.max(inputs[:2, :2] - np.array([[118.25695, 1.89344], [153.33139, 3.37611]])) < 1e-5
    assert (targets[:5, 0] == np.array([0., 1., 1., 1., 1.])).all()
    assert np.max(weights[:5] - np.array([3.34210e-4, 1.26920e-4, 1.10627e-4, 9.5176e-5, 1.11107e-4])) < 1e-9
    assert np.max(normalized_weights[:5] - np.array([0.916951, 1.23007, 1.07217, 0.92242, 1.07682])) < 1e-5
    assert (event_nums[:5] == np.array([2146094, 1273346, 3395091, 855136, 2947049])).all()

    # verify max event weight
    # for 1.1, two of 20 events are duplicated
    run_config.max_event_weight = 1.1
    (inputs,
     targets,
     weights,
     normalized_weights,
     event_nums) = builtin_inputs.get_inputs(run_config,
                                                    nevts=20,
                                                    input_vars_list=run_config.input_vars)
    run_config.max_event_weight = np.inf
    assert inputs.shape == (22, 13)
    assert targets.shape == (22, 1)
    assert weights.shape == (22,)
    assert normalized_weights.shape == (22,)
    assert event_nums.shape == (22,)

    # total weight (not normalized weight!) should be unchanged
    (inputs,
     targets,
     weights,
     normalized_weights,
     event_nums) = builtin_inputs.get_inputs(run_config,
                                                    nevts=run_config.max_num_events,
                                                    input_vars_list=run_config.input_vars)
    total_weight_no_duplication = np.sum(weights)
    run_config.max_event_weight = 1.3
    (inputs,
     targets,
     weights,
     normalized_weights,
     event_nums) = builtin_inputs.get_inputs(run_config,
                                                    nevts=run_config.max_num_events,
                                                    input_vars_list=run_config.input_vars)
    run_config.max_event_weight = np.inf
    assert np.sum(weights) - total_weight_no_duplication < 1e-8


def test_get_training_data():
    # TODO: add more thorough checks if random splitting is correct, i.e. no overlap between train, val and test + KFold
    #       is doing what it is expected to do

    input_handler = get_input_handler()

    # load test dataset of 10000 events, 5000 signal and 5000 background. 13 input variables are set in test config.
    (input_data,
     targets,
     weights,
     normalized_weights,
     event_nums) = builtin_inputs.get_inputs(run_config,
                                                    nevts=run_config.max_num_events,
                                                    input_vars_list=input_handler.get_vars())

    # use custom manual plus standard scaler for all tests
    scaler_class = [builtin_inputs.CustomManualPlusStandardScaler, (input_handler,)]

    # randomly split into training and validation data
    (preprocessor,
     inputs_split,
     targets_split,
     weights_split,
     normalized_weights_split) = builtin_inputs.get_training_data(input_data,
                                                                         targets,
                                                                         weights,
                                                                         normalized_weights,
                                                                         splitting_cond=0.2,
                                                                         preprocessor=scaler_class)
    # check that preprocessor was fitted
    # since preprocessor is fitted to weighted inputs, we need to apply weighting here as well (at least for training
    # set, for the others the difference is small)
    transformed_inputs = preprocessor.transform(input_data)
    assert (np.abs(np.average(input_data, axis=0, weights=normalized_weights)) > 1e-2 * np.ones((13,))).any()
    assert (np.abs(np.average(transformed_inputs, axis=0, weights=normalized_weights)) < 1e-2 * np.ones((13,))).all()

    # check splitting
    assert len(inputs_split) == 2
    assert len(targets_split) == 2
    assert len(weights_split) == 2
    assert len(normalized_weights_split) == 2
    assert inputs_split[0].shape == (8000, 13)
    assert targets_split[0].shape == (8000, 1)
    assert weights_split[0].shape == (8000,)
    assert normalized_weights_split[0].shape == (8000,)
    assert inputs_split[1].shape == (2000, 13)
    assert targets_split[1].shape == (2000, 1)
    assert weights_split[1].shape == (2000,)
    assert normalized_weights_split[1].shape == (2000,)

    # randomly split into training, validation and testing data
    (preprocessor,
     inputs_split,
     targets_split,
     weights_split,
     normalized_weights_split) = builtin_inputs.get_training_data(input_data,
                                                                         targets,
                                                                         weights,
                                                                         normalized_weights,
                                                                         splitting_cond=(0.2, 0.1),
                                                                         preprocessor=scaler_class)
    # check that preprocessor was fitted
    transformed_inputs = preprocessor.transform(input_data)
    assert (np.abs(np.average(input_data, axis=0, weights=normalized_weights)) > 2e-2 * np.ones((13,))).any()
    assert (np.abs(np.average(transformed_inputs, axis=0, weights=normalized_weights)) < 2e-2 * np.ones((13,))).all()

    # check splitting
    assert len(inputs_split) == 3
    assert len(targets_split) == 3
    assert len(weights_split) == 3
    assert len(normalized_weights_split) == 3
    assert inputs_split[0].shape == (7000, 13)
    assert targets_split[0].shape == (7000, 1)
    assert weights_split[0].shape == (7000,)
    assert normalized_weights_split[0].shape == (7000,)
    assert inputs_split[1].shape == (1000, 13)
    assert targets_split[1].shape == (1000, 1)
    assert weights_split[1].shape == (1000,)
    assert normalized_weights_split[1].shape == (1000,)
    assert inputs_split[2].shape == (2000, 13)
    assert targets_split[2].shape == (2000, 1)
    assert weights_split[2].shape == (2000,)
    assert normalized_weights_split[2].shape == (2000,)

    # split into training and validation using custom splitting condition
    val_condition = lambda x: ((x+1) % 3) == 0
    test_condition = lambda x: (x % 3) == 0
    (preprocessor,
     inputs_split,
     targets_split,
     weights_split,
     normalized_weights_split) = builtin_inputs.get_training_data(input_data,
                                                                         targets,
                                                                         weights,
                                                                         normalized_weights,
                                                                         splitting_cond=test_condition,
                                                                         preprocessor=scaler_class,
                                                                         event_nums=event_nums)
    # check that preprocessor was fitted
    transformed_inputs = preprocessor.transform(input_data)
    assert (np.abs(np.average(input_data, axis=0, weights=normalized_weights)) > 2e-2 * np.ones((13,))).any()
    assert (np.abs(np.average(transformed_inputs, axis=0, weights=normalized_weights)) < 2e-2 * np.ones((13,))).all()

    # check splitting
    exp_train = np.logical_not(test_condition(event_nums))
    exp_val = test_condition(event_nums)
    assert len(inputs_split) == 2
    assert len(targets_split) == 2
    assert len(weights_split) == 2
    assert len(normalized_weights_split) == 2

    # check correct event assignment
    assert (preprocessor.transform(input_data[exp_train, :]) == inputs_split[0]).all()
    assert (targets[exp_train, :] == targets_split[0]).all()
    assert (weights[exp_train] == weights_split[0]).all()
    assert (normalized_weights[exp_train] == normalized_weights_split[0]).all()
    assert (preprocessor.transform(input_data[exp_val, :]) == inputs_split[1]).all()
    assert (targets[exp_val, :] == targets_split[1]).all()
    assert (weights[exp_val] == weights_split[1]).all()
    assert (normalized_weights[exp_val] == normalized_weights_split[1]).all()

    # split into training, validation and testing using custom splitting condition
    (preprocessor,
     inputs_split,
     targets_split,
     weights_split,
     normalized_weights_split) = builtin_inputs.get_training_data(input_data,
                                                                         targets,
                                                                         weights,
                                                                         normalized_weights,
                                                                         splitting_cond=(test_condition, val_condition),
                                                                         preprocessor=scaler_class,
                                                                         event_nums=event_nums)

    # check that preprocessor was fitted
    transformed_inputs = preprocessor.transform(input_data)
    assert (np.abs(np.average(input_data, axis=0, weights=normalized_weights)) > 2e-2 * np.ones((13,))).any()
    assert (np.abs(np.average(transformed_inputs, axis=0, weights=normalized_weights)) < 2e-2 * np.ones((13,))).all()

    # check splitting
    exp_train = np.logical_not(test_condition(event_nums) + val_condition(event_nums))
    exp_val = val_condition(event_nums)
    exp_test = test_condition(event_nums)
    assert len(inputs_split) == 3
    assert len(targets_split) == 3
    assert len(weights_split) == 3
    assert len(normalized_weights_split) == 3

    # check correct event assignment
    assert (preprocessor.transform(input_data[exp_train, :]) == inputs_split[0]).all()
    assert (targets[exp_train, :] == targets_split[0]).all()
    assert (weights[exp_train] == weights_split[0]).all()
    assert (normalized_weights[exp_train] == normalized_weights_split[0]).all()
    assert (preprocessor.transform(input_data[exp_val, :]) == inputs_split[1]).all()
    assert (targets[exp_val, :] == targets_split[1]).all()
    assert (weights[exp_val] == weights_split[1]).all()
    assert (normalized_weights[exp_val] == normalized_weights_split[1]).all()
    assert (preprocessor.transform(input_data[exp_test, :]) == inputs_split[2]).all()
    assert (targets[exp_test, :] == targets_split[2]).all()
    assert (weights[exp_test] == weights_split[2]).all()
    assert (normalized_weights[exp_test] == normalized_weights_split[2]).all()

    # test k-fold for sklearn train/val splitting
    (preprocessor,
     inputs_split,
     targets_split,
     weights_split,
     normalized_weights_split) = builtin_inputs.get_training_data(input_data,
                                                                         targets,
                                                                         weights,
                                                                         normalized_weights,
                                                                         splitting_cond=0.2,
                                                                         preprocessor=scaler_class,
                                                                         do_kfold=True)
    # check splitting
    assert len(inputs_split) == 2
    assert len(targets_split) == 2
    assert len(weights_split) == 2
    assert len(normalized_weights_split) == 2

    # check folds
    for i_fold in range(5):
        # check that preprocessor was fitted
        transformed_inputs = preprocessor[i_fold].transform(input_data)
        assert (np.abs(np.average(input_data, axis=0, weights=normalized_weights)) > 2e-2 * np.ones((13,))).any()
        assert (np.abs(np.average(transformed_inputs, axis=0, weights=normalized_weights)) < 2e-2 * np.ones((13,))).all()

        # check event assignment
        # validation datasets
        assert (inputs_split[1][i_fold] == preprocessor[i_fold].transform(input_data[2000 * i_fold:2000 * (i_fold + 1)])).all()
        assert (targets_split[1][i_fold] == targets[2000 * i_fold:2000 * (i_fold + 1)]).all()
        assert (weights_split[1][i_fold] == weights[2000 * i_fold:2000 * (i_fold + 1)]).all()
        assert (normalized_weights_split[1][i_fold] == normalized_weights[2000 * i_fold:2000 * (i_fold + 1)]).all()

        # training datasets
        assert (inputs_split[0][i_fold] == preprocessor[i_fold].transform(np.concatenate((input_data[:2000 * i_fold], input_data[2000 * (i_fold + 1):])))).all()
        assert (targets_split[0][i_fold] == np.concatenate((targets[:2000 * i_fold], targets[2000 * (i_fold + 1):]))).all()
        assert (weights_split[0][i_fold] == np.concatenate((weights[:2000 * i_fold], weights[2000 * (i_fold + 1):]))).all()
        assert (normalized_weights_split[0][i_fold] == np.concatenate((normalized_weights[:2000 * i_fold], normalized_weights[2000 * (i_fold + 1):]))).all()

    # test k-fold for sklearn train/val/test splitting
    (preprocessor,
     inputs_split,
     targets_split,
     weights_split,
     normalized_weights_split) = builtin_inputs.get_training_data(input_data,
                                                                         targets,
                                                                         weights,
                                                                         normalized_weights,
                                                                         splitting_cond=(0.2, 0.2),
                                                                         preprocessor=scaler_class,
                                                                         do_kfold=True)

    # check splitting
    assert len(inputs_split) == 3
    assert len(targets_split) == 3
    assert len(weights_split) == 3
    assert len(normalized_weights_split) == 3

    # check folds; testing dataset is split randomly, thus event assignment can only be checked by concatenating training and
    # validation sets
    for i_fold in range(4):
        # check that preprocessor was fitted
        transformed_inputs = preprocessor[i_fold].transform(input_data)
        assert (np.abs(np.average(input_data, axis=0, weights=normalized_weights)) > 3e-2 * np.ones((13,))).any()
        assert (np.abs(np.average(transformed_inputs, axis=0, weights=normalized_weights)) < 3e-2 * np.ones((13,))).all()

        # check event assignments; the inputs are not expected to be identical due to the
        # different scalers
        assert np.max(np.concatenate((inputs_split[1][0], inputs_split[0][0])) -
                np.concatenate((inputs_split[0][i_fold][:2000 * i_fold], inputs_split[1][i_fold], inputs_split[0][i_fold][2000 * i_fold:]))) < 0.06
        assert (np.concatenate((targets_split[1][0], targets_split[0][0])) ==
                np.concatenate((targets_split[0][i_fold][:2000 * i_fold], targets_split[1][i_fold], targets_split[0][i_fold][2000 * i_fold:]))).all()
        assert (np.concatenate((weights_split[1][0], weights_split[0][0])) ==
                np.concatenate((weights_split[0][i_fold][:2000 * i_fold], weights_split[1][i_fold], weights_split[0][i_fold][2000 * i_fold:]))).all()
        assert (np.concatenate((normalized_weights_split[1][0], normalized_weights_split[0][0])) ==
                np.concatenate((normalized_weights_split[0][i_fold][:2000 * i_fold], normalized_weights_split[1][i_fold], normalized_weights_split[0][i_fold][2000 * i_fold:]))).all()

        # verify that test set is the same for all folds; the inputs are not expected to be identical due to the
        # different scalers
        assert np.max(np.abs(inputs_split[2][i_fold] - inputs_split[2][0])) < 0.06
        assert (np.abs(targets_split[2][i_fold] == targets_split[2][0])).all()
        assert (np.abs(weights_split[2][i_fold] == weights_split[2][0])).all()
        assert (np.abs(normalized_weights_split[2][i_fold] == normalized_weights_split[2][0])).all()

    # test k-fold for random train/val/test splitting with fixed_test_dataset == False
    (preprocessor,
     inputs_split,
     targets_split,
     weights_split,
     normalized_weights_split) = builtin_inputs.get_training_data(input_data,
                                                                         targets,
                                                                         weights,
                                                                         normalized_weights,
                                                                         splitting_cond=(0.2, 0.2),
                                                                         preprocessor=scaler_class,
                                                                         do_kfold=True,
                                                                         fixed_test_dataset=False)

    # check splitting
    assert len(inputs_split) == 3
    assert len(targets_split) == 3
    assert len(weights_split) == 3
    assert len(normalized_weights_split) == 3

    # check folds
    for i_fold in range(5):
        # check that preprocessor was fitted
        transformed_inputs = preprocessor[i_fold].transform(input_data)
        assert (np.abs(np.average(input_data, axis=0, weights=normalized_weights)) > 4e-2 * np.ones((13,))).any()
        assert (np.abs(np.average(transformed_inputs, axis=0, weights=normalized_weights)) < 4e-2 * np.ones((13,))).all()

        # check event assignment
        # training datasets
        if i_fold != 4:
            assert (inputs_split[0][i_fold] == preprocessor[i_fold].transform(np.concatenate((input_data[:2000 * i_fold], input_data[2000 * (i_fold + 2):])))).all()
            assert (targets_split[0][i_fold] == np.concatenate((targets[:2000 * i_fold], targets[2000 * (i_fold + 2):]))).all()
            assert (weights_split[0][i_fold] == np.concatenate((weights[:2000 * i_fold], weights[2000 * (i_fold + 2):]))).all()
            assert (normalized_weights_split[0][i_fold] == np.concatenate((normalized_weights[:2000 * i_fold], normalized_weights[2000 * (i_fold + 2):]))).all()
        else:
            assert (inputs_split[0][i_fold] == preprocessor[i_fold].transform(input_data[2000:8000])).all()
            assert (targets_split[0][i_fold] == targets[2000:8000]).all()
            assert (weights_split[0][i_fold] == weights[2000:8000]).all()
            assert (normalized_weights_split[0][i_fold] == normalized_weights[2000:8000]).all()

        # validation datasets
        assert np.max(inputs_split[1][i_fold] - inputs_split[2][(i_fold+1) % 5] < 0.04)
        assert (targets_split[1][i_fold] == targets_split[2][(i_fold+1) % 5]).all()
        assert (weights_split[1][i_fold] == weights_split[2][(i_fold+1) % 5]).all()
        assert (normalized_weights_split[1][i_fold] == normalized_weights_split[2][(i_fold+1) % 5]).all()

        # testing datasets
        assert (inputs_split[2][i_fold] == preprocessor[i_fold].transform(input_data[2000 * i_fold:2000 * (i_fold + 1)])).all()
        assert (targets_split[2][i_fold] == targets[2000 * i_fold:2000 * (i_fold + 1)]).all()
        assert (weights_split[2][i_fold] == weights[2000 * i_fold:2000 * (i_fold + 1)]).all()
        assert (normalized_weights_split[2][i_fold] == normalized_weights[2000 * i_fold:2000 * (i_fold + 1)]).all()

    # now test with custom splitting conditions
    val_condition = partial(inputs._event_nums_splitting_cond_kfold, run_config=run_config, split='val', use_testing_set=False)
    val_withTest_condition = partial(inputs._event_nums_splitting_cond_kfold, run_config=run_config, split='val', use_testing_set=True)
    test_condition = partial(inputs._event_nums_splitting_cond_kfold, run_config=run_config, split='test', use_testing_set=True)
    val_withVariableTest_condition = partial(inputs._event_nums_splitting_cond_kfold, run_config=run_config, split='val', use_testing_set=True, fixed_testing_set=False)
    variableTest_condition = partial(inputs._event_nums_splitting_cond_kfold, run_config=run_config, split='test', use_testing_set=True, fixed_testing_set=False)

    # test train/val splitting
    (preprocessor,
     inputs_split,
     targets_split,
     weights_split,
     normalized_weights_split) = builtin_inputs.get_training_data(input_data,
                                                                  targets,
                                                                  weights,
                                                                  normalized_weights,
                                                                  splitting_cond=val_condition,
                                                                  preprocessor=scaler_class,
                                                                  event_nums=event_nums,
                                                                  do_kfold=True)
    # check splitting
    assert len(inputs_split) == 2
    assert len(targets_split) == 2
    assert len(weights_split) == 2
    assert len(normalized_weights_split) == 2

    # check folds
    exp_train = np.logical_not(val_condition(event_nums))
    exp_val = val_condition(event_nums)
    for i_fold in range(5):
        # check that preprocessor was fitted
        transformed_inputs = preprocessor[i_fold].transform(input_data)
        assert (np.abs(np.average(input_data, axis=0, weights=normalized_weights)) > 3e-2 * np.ones((13,))).any()
        assert (np.abs(np.average(transformed_inputs, axis=0, weights=normalized_weights)) < 3e-2 * np.ones((13,))).all()

        # check correct event assignment
        assert (preprocessor[i_fold].transform(input_data[exp_train[i_fold], :]) == inputs_split[0][i_fold]).all()
        assert (targets[exp_train[i_fold], :] == targets_split[0][i_fold]).all()
        assert (weights[exp_train[i_fold]] == weights_split[0][i_fold]).all()
        assert (normalized_weights[exp_train[i_fold]] == normalized_weights_split[0][i_fold]).all()
        assert (preprocessor[i_fold].transform(input_data[exp_val[i_fold], :]) == inputs_split[1][i_fold]).all()
        assert (targets[exp_val[i_fold], :] == targets_split[1][i_fold]).all()
        assert (weights[exp_val[i_fold]] == weights_split[1][i_fold]).all()
        assert (normalized_weights[exp_val[i_fold]] == normalized_weights_split[1][i_fold]).all()

    # now train/val/test splitting
    (preprocessor,
     inputs_split,
     targets_split,
     weights_split,
     normalized_weights_split) = builtin_inputs.get_training_data(input_data,
                                                                         targets,
                                                                         weights,
                                                                         normalized_weights,
                                                                         splitting_cond=(test_condition, val_withTest_condition),
                                                                         preprocessor=scaler_class,
                                                                         event_nums=event_nums,
                                                                         do_kfold=True)
    # check splitting
    assert len(inputs_split) == 3
    assert len(targets_split) == 3
    assert len(weights_split) == 3
    assert len(normalized_weights_split) == 3

    # check folds
    exp_train = np.logical_not(np.logical_or(val_withTest_condition(event_nums), test_condition(event_nums)))
    exp_val = val_withTest_condition(event_nums)
    exp_test = test_condition(event_nums)
    for i_fold in range(4):
        # check that preprocessor was fitted
        transformed_inputs = preprocessor[i_fold].transform(input_data)
        assert (np.abs(np.average(input_data, axis=0, weights=normalized_weights)) > 3e-2 * np.ones((13,))).any()
        assert (np.abs(np.average(transformed_inputs, axis=0, weights=normalized_weights)) < 3e-2 * np.ones((13,))).all()

        # check correct event assignment
        assert (preprocessor[i_fold].transform(input_data[exp_train[i_fold], :]) == inputs_split[0][i_fold]).all()
        assert (targets[exp_train[i_fold], :] == targets_split[0][i_fold]).all()
        assert (weights[exp_train[i_fold]] == weights_split[0][i_fold]).all()
        assert (normalized_weights[exp_train[i_fold]] == normalized_weights_split[0][i_fold]).all()
        assert (preprocessor[i_fold].transform(input_data[exp_val[i_fold], :]) == inputs_split[1][i_fold]).all()
        assert (targets[exp_val[i_fold], :] == targets_split[1][i_fold]).all()
        assert (weights[exp_val[i_fold]] == weights_split[1][i_fold]).all()
        assert (normalized_weights[exp_val[i_fold]] == normalized_weights_split[1][i_fold]).all()
        assert (preprocessor[i_fold].transform(input_data[exp_test[i_fold], :]) == inputs_split[2][i_fold]).all()
        assert (targets[exp_test[i_fold], :] == targets_split[2][i_fold]).all()
        assert (weights[exp_test[i_fold]] == weights_split[2][i_fold]).all()
        assert (normalized_weights[exp_test[i_fold]] == normalized_weights_split[2][i_fold]).all()

    # train/val/test splitting with NOT fixed testing set
    (preprocessor,
     inputs_split,
     targets_split,
     weights_split,
     normalized_weights_split) = builtin_inputs.get_training_data(input_data,
                                                                         targets,
                                                                         weights,
                                                                         normalized_weights,
                                                                         splitting_cond=(variableTest_condition, val_withVariableTest_condition),
                                                                         preprocessor=scaler_class,
                                                                         event_nums=event_nums,
                                                                         do_kfold=True)
    # check splitting
    assert len(inputs_split) == 3
    assert len(targets_split) == 3
    assert len(weights_split) == 3
    assert len(normalized_weights_split) == 3

    # check folds
    exp_train = np.logical_not(np.logical_or(val_withVariableTest_condition(event_nums), variableTest_condition(event_nums)))
    exp_val = val_withVariableTest_condition(event_nums)
    exp_test = variableTest_condition(event_nums)
    for i_fold in range(5):
        # check that preprocessor was fitted
        transformed_inputs = preprocessor[i_fold].transform(input_data)
        assert (np.abs(np.average(input_data, axis=0, weights=normalized_weights)) > 3e-2 * np.ones((13,))).any()
        assert (np.abs(np.average(transformed_inputs, axis=0, weights=normalized_weights)) < 3e-2 * np.ones((13,))).all()

        # check correct event assignment
        assert (preprocessor[i_fold].transform(input_data[exp_train[i_fold], :]) == inputs_split[0][i_fold]).all()
        assert (targets[exp_train[i_fold], :] == targets_split[0][i_fold]).all()
        assert (weights[exp_train[i_fold]] == weights_split[0][i_fold]).all()
        assert (normalized_weights[exp_train[i_fold]] == normalized_weights_split[0][i_fold]).all()
        assert (preprocessor[i_fold].transform(input_data[exp_val[i_fold], :]) == inputs_split[1][i_fold]).all()
        assert (targets[exp_val[i_fold], :] == targets_split[1][i_fold]).all()
        assert (weights[exp_val[i_fold]] == weights_split[1][i_fold]).all()
        assert (normalized_weights[exp_val[i_fold]] == normalized_weights_split[1][i_fold]).all()
        assert (preprocessor[i_fold].transform(input_data[exp_test[i_fold], :]) == inputs_split[2][i_fold]).all()
        assert (targets[exp_test[i_fold], :] == targets_split[2][i_fold]).all()
        assert (weights[exp_test[i_fold]] == weights_split[2][i_fold]).all()
        assert (normalized_weights[exp_test[i_fold]] == normalized_weights_split[2][i_fold]).all()


def test_custom_splitting_cond_kfold():
    condition_list_val = inputs._event_nums_splitting_cond_kfold(
        np.array([1, 2, 3, 4, 5, 6, 7]),
        run_config,
        split='val',
        use_testing_set=False
    )
    condition_list_val_withTest = inputs._event_nums_splitting_cond_kfold(
        np.array([1, 2, 3, 4, 5, 6, 7]),
        run_config,
        split='val',
        use_testing_set=True
    )
    condition_list_test = inputs._event_nums_splitting_cond_kfold(
        np.array([1, 2, 3, 4, 5, 6, 7]),
        run_config,
        split='test',
        use_testing_set=True
    )
    condition_list_val_withVariableTest = inputs._event_nums_splitting_cond_kfold(
        np.array([1, 2, 3, 4, 5, 6, 7]),
        run_config,
        split='val',
        use_testing_set=True,
        fixed_testing_set=False
    )
    condition_list_variableTest = inputs._event_nums_splitting_cond_kfold(
        np.array([1, 2, 3, 4, 5, 6, 7]),
        run_config,
        split='test',
        use_testing_set=True,
        fixed_testing_set=False
    )
    condition_list_val_exp = np.array(
        [
            [False, False, False, False, True, False, False],
            [True, False, False, False, False, True, False],
            [False, True, False, False, False, False, True],
            [False, False, True, False, False, False, False],
            [False, False, False, True, False, False, False],
        ]
    )
    condition_list_val_withTest_exp = np.array(
        np.array(
            [
                [False, False, False, False, True, False, False],
                [True, False, False, False, False, True, False],
                [False, True, False, False, False, False, True],
                [False, False, True, False, False, False, False],
            ]
        )
    )
    condition_list_test_exp = np.array(
        np.array(
            [
                [False, False, False, True, False, False, False],
                [False, False, False, True, False, False, False],
                [False, False, False, True, False, False, False],
                [False, False, False, True, False, False, False],
            ]
        )
    )
    condition_list_variableTest_exp = np.array(
        np.array(
            [
                [False, False, False, True, False, False, False],
                [False, False, False, False, True, False, False],
                [True, False, False, False, False, True, False],
                [False, True, False, False, False, False, True],
                [False, False, True, False, False, False, False],
            ]
        )
    )
    assert (condition_list_val == condition_list_val_exp).all()
    assert (condition_list_val_withTest == condition_list_val_withTest_exp).all()
    assert (condition_list_test == condition_list_test_exp).all()
    assert (condition_list_val_withVariableTest == condition_list_val_exp).all()
    assert (condition_list_variableTest == condition_list_variableTest_exp).all()


def test_get_experiment_inputs():
    input_handler = builtin_inputs.InputHandler(run_config)

    # run-config currently says train/val split with custom splitting condition, C_val = 0
    inputs_split, targets_split, weights_split, normalized_weights_split = inputs.get_experiment_inputs(
        run_config, input_handler
    )
    inputs_split = ray.get(inputs_split)
    targets_split = ray.get(targets_split)
    weights_split = ray.get(weights_split)
    normalized_weights_split = ray.get(normalized_weights_split)
    assert len(inputs_split) == 2
    assert len(targets_split) == 2
    assert len(weights_split) == 2
    assert len(normalized_weights_split) == 2

    # verify that event splitting is correct
    (input_data,
     targets,
     weights,
     normalized_weights,
     event_nums) = builtin_inputs.get_inputs(run_config,
                                             nevts=run_config.max_num_events,
                                             input_vars_list=input_handler.get_vars())
    train_condition = lambda x: np.mod(x, 5) != 0
    val_condition = lambda x: np.mod(x, 5) == 0
    assert input_data[train_condition(event_nums), :].shape == inputs_split[0].shape
    assert input_data[val_condition(event_nums), :].shape == inputs_split[1].shape
    assert targets[train_condition(event_nums)].shape == targets_split[0].shape
    assert targets[val_condition(event_nums)].shape == targets_split[1].shape
    assert weights[train_condition(event_nums)].shape == weights_split[0].shape
    assert weights[val_condition(event_nums)].shape == weights_split[1].shape
    assert normalized_weights[train_condition(event_nums)].shape == normalized_weights_split[0].shape
    assert normalized_weights[val_condition(event_nums)].shape == normalized_weights_split[1].shape

    # now use random splitting
    run_config.use_eventNums_splitting = False
    inputs_split, targets_split, weights_split, normalized_weights_split = inputs.get_experiment_inputs(
        run_config, input_handler
    )
    inputs_split = ray.get(inputs_split)
    targets_split = ray.get(targets_split)
    weights_split = ray.get(weights_split)
    normalized_weights_split = ray.get(normalized_weights_split)
    assert len(inputs_split) == 2
    assert len(targets_split) == 2
    assert len(weights_split) == 2
    assert len(normalized_weights_split) == 2
    assert inputs_split[0].shape == (8000, 13)
    assert inputs_split[1].shape == (2000, 13)
    assert targets_split[0].shape == (8000, 1)
    assert (targets_split[0][:10] == [[0.], [0.], [0.], [0.], [0.], [0.], [1.], [0.], [1.], [1.]]).all()  # verify that loading inputs is deterministic
    assert targets_split[1].shape == (2000, 1)
    assert weights_split[0].shape == (8000,)
    assert weights_split[1].shape == (2000,)
    assert normalized_weights_split[0].shape == (8000,)
    assert normalized_weights_split[1].shape == (2000,)
    run_config.use_eventNums_splitting = True

    # now also use testing set; C_test is 1
    run_config.use_testing_dataset = True
    inputs_split, targets_split, weights_split, normalized_weights_split = inputs.get_experiment_inputs(
        run_config, input_handler
    )
    inputs_split = ray.get(inputs_split)
    targets_split = ray.get(targets_split)
    weights_split = ray.get(weights_split)
    normalized_weights_split = ray.get(normalized_weights_split)
    assert len(inputs_split) == 3
    assert len(targets_split) == 3
    assert len(weights_split) == 3
    assert len(normalized_weights_split) == 3
    train_condition = lambda x: np.mod(x, 5) * np.mod(x + 1, 5) != 0
    val_condition = lambda x: np.mod(x, 5) == 0
    test_condition = lambda x: np.mod(x + 1, 5) == 0
    assert input_data[train_condition(event_nums), :].shape == inputs_split[0].shape
    assert input_data[val_condition(event_nums), :].shape == inputs_split[1].shape
    assert input_data[test_condition(event_nums), :].shape == inputs_split[2].shape
    assert targets[train_condition(event_nums)].shape == targets_split[0].shape
    assert targets[val_condition(event_nums)].shape == targets_split[1].shape
    assert targets[test_condition(event_nums)].shape == targets_split[2].shape
    assert weights[train_condition(event_nums)].shape == weights_split[0].shape
    assert weights[val_condition(event_nums)].shape == weights_split[1].shape
    assert weights[test_condition(event_nums)].shape == weights_split[2].shape
    assert normalized_weights[train_condition(event_nums)].shape == normalized_weights_split[0].shape
    assert normalized_weights[val_condition(event_nums)].shape == normalized_weights_split[1].shape
    assert normalized_weights[test_condition(event_nums)].shape == normalized_weights_split[2].shape

    # and now use random splitting with testing dataset
    run_config.use_eventNums_splitting = False
    inputs_split, targets_split, weights_split, normalized_weights_split = inputs.get_experiment_inputs(
        run_config, input_handler
    )
    inputs_split = ray.get(inputs_split)
    targets_split = ray.get(targets_split)
    weights_split = ray.get(weights_split)
    normalized_weights_split = ray.get(normalized_weights_split)
    assert len(inputs_split) == 3
    assert len(targets_split) == 3
    assert len(weights_split) == 3
    assert len(normalized_weights_split) == 3
    assert inputs_split[0].shape == (6000, 13)
    assert inputs_split[1].shape == (2000, 13)
    assert inputs_split[2].shape == (2000, 13)
    assert targets_split[0].shape == (6000, 1)
    assert (targets_split[0][:10] == [[0.], [1.], [0.], [1.], [0.], [1.], [0.], [0.], [0.], [0.]]).all()  # verify that loading inputs is deterministic
    assert targets_split[1].shape == (2000, 1)
    assert targets_split[2].shape == (2000, 1)
    assert weights_split[0].shape == (6000,)
    assert weights_split[1].shape == (2000,)
    assert weights_split[2].shape == (2000,)
    assert normalized_weights_split[0].shape == (6000,)
    assert normalized_weights_split[1].shape == (2000,)
    assert normalized_weights_split[2].shape == (2000,)
    run_config.use_eventNums_splitting = True
    run_config.use_testing_dataset = False

    # now try inputs for crossvalidation with custom splitting, no testing dataset
    inputs_split, targets_split, weights_split, normalized_weights_split = inputs.get_experiment_inputs(
        run_config, input_handler, inputs_for_crossvalidation=True
    )
    inputs_split = [ray.get(e) for e in inputs_split]
    targets_split = [ray.get(e) for e in targets_split]
    weights_split = [ray.get(e) for e in weights_split]
    normalized_weights_split = [ray.get(e) for e in normalized_weights_split]
    splitting_cond_val = inputs._event_nums_splitting_cond_kfold(
        event_nums,
        run_config,
        split='val',
        use_testing_set=False,
    )
    splitting_cond_train = np.logical_not(splitting_cond_val)
    assert len(inputs_split) == 2
    assert len(targets_split) == 2
    assert len(weights_split) == 2
    assert len(normalized_weights_split) == 2

    for split in range(run_config.eventNums_splitting_N):
        assert input_data[splitting_cond_train[split]].shape == inputs_split[0][split].shape
        assert targets[splitting_cond_train[split]].shape == targets_split[0][split].shape
        assert weights[splitting_cond_train[split]].shape == weights_split[0][split].shape
        assert normalized_weights[splitting_cond_train[split]].shape == normalized_weights_split[0][split].shape
        assert input_data[splitting_cond_val[split]].shape == inputs_split[1][split].shape
        assert targets[splitting_cond_val[split]].shape == targets_split[1][split].shape
        assert weights[splitting_cond_val[split]].shape == weights_split[1][split].shape
        assert normalized_weights[splitting_cond_val[split]].shape == normalized_weights_split[1][split].shape

    # with testing dataset
    run_config.use_testing_dataset = True
    inputs_split, targets_split, weights_split, normalized_weights_split = inputs.get_experiment_inputs(
        run_config, input_handler, inputs_for_crossvalidation=True
    )
    inputs_split = [ray.get(e) for e in inputs_split]
    targets_split = [ray.get(e) for e in targets_split]
    weights_split = [ray.get(e) for e in weights_split]
    normalized_weights_split = [ray.get(e) for e in normalized_weights_split]
    splitting_cond_val = inputs._event_nums_splitting_cond_kfold(
        event_nums,
        run_config,
        split='val',
        use_testing_set=True,
    )
    splitting_cond_test = inputs._event_nums_splitting_cond_kfold(
        event_nums,
        run_config,
        split='test',
        use_testing_set=True,
    )
    splitting_cond_train = np.logical_not(np.logical_or(splitting_cond_val, splitting_cond_test))
    assert len(inputs_split) == 3
    assert len(targets_split) == 3
    assert len(weights_split) == 3
    assert len(normalized_weights_split) == 3

    for split in range(run_config.eventNums_splitting_N-1):
        assert input_data[splitting_cond_train[split]].shape == inputs_split[0][split].shape
        assert targets[splitting_cond_train[split]].shape == targets_split[0][split].shape
        assert weights[splitting_cond_train[split]].shape == weights_split[0][split].shape
        assert normalized_weights[splitting_cond_train[split]].shape == normalized_weights_split[0][split].shape
        assert input_data[splitting_cond_val[split]].shape == inputs_split[1][split].shape
        assert targets[splitting_cond_val[split]].shape == targets_split[1][split].shape
        assert weights[splitting_cond_val[split]].shape == weights_split[1][split].shape
        assert normalized_weights[splitting_cond_val[split]].shape == normalized_weights_split[1][split].shape
        assert input_data[splitting_cond_test[split]].shape == inputs_split[2][split].shape
        assert targets[splitting_cond_test[split]].shape == targets_split[2][split].shape
        assert weights[splitting_cond_test[split]].shape == weights_split[2][split].shape
        assert normalized_weights[splitting_cond_test[split]].shape == normalized_weights_split[2][split].shape
    run_config.use_testing_dataset = False

    # with variable testing dataset
    run_config.use_testing_dataset = True
    run_config.fixed_testing_dataset = False
    inputs_split, targets_split, weights_split, normalized_weights_split = inputs.get_experiment_inputs(
        run_config, input_handler, inputs_for_crossvalidation=True
    )
    inputs_split = [ray.get(e) for e in inputs_split]
    targets_split = [ray.get(e) for e in targets_split]
    weights_split = [ray.get(e) for e in weights_split]
    normalized_weights_split = [ray.get(e) for e in normalized_weights_split]
    splitting_cond_val = inputs._event_nums_splitting_cond_kfold(
        event_nums,
        run_config,
        split='val',
        use_testing_set=True,
        fixed_testing_set=False
    )
    splitting_cond_test = inputs._event_nums_splitting_cond_kfold(
        event_nums,
        run_config,
        split='test',
        use_testing_set=True,
        fixed_testing_set=False
    )
    splitting_cond_train = np.logical_not(np.logical_or(splitting_cond_val, splitting_cond_test))
    assert len(inputs_split) == 3
    assert len(targets_split) == 3
    assert len(weights_split) == 3
    assert len(normalized_weights_split) == 3

    for split in range(run_config.eventNums_splitting_N):
        assert input_data[splitting_cond_train[split]].shape == inputs_split[0][split].shape
        assert targets[splitting_cond_train[split]].shape == targets_split[0][split].shape
        assert weights[splitting_cond_train[split]].shape == weights_split[0][split].shape
        assert normalized_weights[splitting_cond_train[split]].shape == normalized_weights_split[0][split].shape
        assert input_data[splitting_cond_val[split]].shape == inputs_split[1][split].shape
        assert targets[splitting_cond_val[split]].shape == targets_split[1][split].shape
        assert weights[splitting_cond_val[split]].shape == weights_split[1][split].shape
        assert normalized_weights[splitting_cond_val[split]].shape == normalized_weights_split[1][split].shape
        assert input_data[splitting_cond_test[split]].shape == inputs_split[2][split].shape
        assert targets[splitting_cond_test[split]].shape == targets_split[2][split].shape
        assert weights[splitting_cond_test[split]].shape == weights_split[2][split].shape
        assert normalized_weights[splitting_cond_test[split]].shape == normalized_weights_split[2][split].shape
    run_config.fixed_testing_dataset = True
    run_config.use_testing_dataset = False

    # now random splitting, no testing dataset
    run_config.use_eventNums_splitting = False
    inputs_split, targets_split, weights_split, normalized_weights_split = inputs.get_experiment_inputs(
        run_config, input_handler, inputs_for_crossvalidation=True
    )
    inputs_split = [ray.get(e) for e in inputs_split]
    targets_split = [ray.get(e) for e in targets_split]
    weights_split = [ray.get(e) for e in weights_split]
    normalized_weights_split = [ray.get(e) for e in normalized_weights_split]
    assert len(inputs_split) == 2
    assert len(targets_split) == 2
    assert len(weights_split) == 2
    assert len(normalized_weights_split) == 2
    assert (targets_split[0][0][:10] == [[0.], [1.], [1.], [0.], [0.], [0.], [0.], [0.], [1.], [1.]]).all()  # verify that loading inputs is deterministic
    for split in range(round(run_config.test_fraction / run_config.validation_fraction)):
        assert inputs_split[0][split].shape == (8000, 13)
        assert inputs_split[1][split].shape == (2000, 13)
        assert targets_split[0][split].shape == (8000, 1)
        assert targets_split[1][split].shape == (2000, 1)
        assert weights_split[0][split].shape == (8000,)
        assert weights_split[1][split].shape == (2000,)
        assert normalized_weights_split[0][split].shape == (8000,)
        assert normalized_weights_split[1][split].shape == (2000,)
    run_config.use_eventNums_splitting = True

    # with testing dataset
    run_config.use_eventNums_splitting = False
    run_config.use_testing_dataset = True
    inputs_split, targets_split, weights_split, normalized_weights_split = inputs.get_experiment_inputs(
        run_config, input_handler, inputs_for_crossvalidation=True
    )
    inputs_split = [ray.get(e) for e in inputs_split]
    targets_split = [ray.get(e) for e in targets_split]
    weights_split = [ray.get(e) for e in weights_split]
    normalized_weights_split = [ray.get(e) for e in normalized_weights_split]
    assert len(inputs_split) == 3
    assert len(targets_split) == 3
    assert len(weights_split) == 3
    assert len(normalized_weights_split) == 3
    assert (targets_split[0][0][:10] == [[0.], [1.], [0.], [0.], [1.], [0.], [0.], [1.], [0.], [0.]]).all()  # verify that loading inputs is deterministic
    for split in range(round((1 - run_config.test_fraction) / run_config.validation_fraction)):
        assert inputs_split[0][split].shape == (6000, 13)
        assert inputs_split[1][split].shape == (2000, 13)
        assert inputs_split[2][split].shape == (2000, 13)
        assert np.max(inputs_split[2][split] - inputs_split[2][0]) < 0.05
        assert targets_split[0][split].shape == (6000, 1)
        assert targets_split[1][split].shape == (2000, 1)
        assert targets_split[2][split].shape == (2000, 1)
        assert (targets_split[2][split] == targets_split[2][0]).all()
        assert weights_split[0][split].shape == (6000,)
        assert weights_split[1][split].shape == (2000,)
        assert weights_split[2][split].shape == (2000,)
        assert (weights_split[2][split] == weights_split[2][0]).all()
        assert normalized_weights_split[0][split].shape == (6000,)
        assert normalized_weights_split[1][split].shape == (2000,)
        assert normalized_weights_split[2][split].shape == (2000,)
        assert (normalized_weights_split[2][split] == normalized_weights_split[2][0]).all()
    run_config.use_eventNums_splitting = True
    run_config.use_testing_dataset = False

    # with variable testing dataset
    run_config.use_eventNums_splitting = False
    run_config.use_testing_dataset = True
    run_config.fixed_testing_dataset = False
    inputs_split, targets_split, weights_split, normalized_weights_split = inputs.get_experiment_inputs(
        run_config, input_handler, inputs_for_crossvalidation=True
    )
    inputs_split = [ray.get(e) for e in inputs_split]
    targets_split = [ray.get(e) for e in targets_split]
    weights_split = [ray.get(e) for e in weights_split]
    normalized_weights_split = [ray.get(e) for e in normalized_weights_split]
    assert len(inputs_split) == 3
    assert len(targets_split) == 3
    assert len(weights_split) == 3
    assert len(normalized_weights_split) == 3
    print(inputs_split[2][0][:5])
    print(inputs_split[2][1][:5])
    print(inputs_split[2][2][:5])
    print(inputs_split[2][3][:5])
    print(inputs_split[2][4][:5])
    for split in range(round(1 / run_config.test_fraction)):
        assert inputs_split[0][split].shape == (6000, 13)
        assert inputs_split[1][split].shape == (2000, 13)
        assert inputs_split[2][split].shape == (2000, 13)
        if split > 0: assert np.max(inputs_split[2][split] - inputs_split[2][0]) > 0.05
        assert targets_split[0][split].shape == (6000, 1)
        assert targets_split[1][split].shape == (2000, 1)
        assert targets_split[2][split].shape == (2000, 1)
        if split > 0: assert np.max(targets_split[2][split] - targets_split[2][0]) > 0.01
        assert weights_split[0][split].shape == (6000,)
        assert weights_split[1][split].shape == (2000,)
        assert weights_split[2][split].shape == (2000,)
        if split > 0: assert np.max(weights_split[2][split] - weights_split[2][0]) > 0.01 * np.mean(weights_split[2][split])
        assert normalized_weights_split[0][split].shape == (6000,)
        assert normalized_weights_split[1][split].shape == (2000,)
        assert normalized_weights_split[2][split].shape == (2000,)
        if split > 0: assert np.max(normalized_weights_split[2][split] - normalized_weights_split[2][0]) > 0.01
    run_config.use_eventNums_splitting = True
    run_config.use_testing_dataset = False
    run_config.fixed_testing_dataset = True
