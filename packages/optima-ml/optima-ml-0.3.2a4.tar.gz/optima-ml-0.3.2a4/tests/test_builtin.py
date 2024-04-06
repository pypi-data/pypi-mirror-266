"""Collection of unit tests related to the built-in functionality of multilayer perceptrons for classification."""
import os
import sys
import random as python_random
import shutil

if sys.platform == "darwin":
    import multiprocess as mp
else:
    import multiprocessing as mp


import numpy as np
import tensorflow as tf
from ray import tune
from tensorflow import random as tf_random
from tensorflow.keras.utils import set_random_seed as keras_set_seed

import pytest

from .context import tools, training, builtin_inputs, builtin_search_space, builtin_model, keras_tools, keras_training
from . import config as run_config


def get_default_model():
    # get dummy input handler with linear input scaling
    input_handler = builtin_inputs.InputHandler(run_config)
    input_handler.set_vars([f"input_{i}" for i in range(13)])
    input_handler.scaling_dict = {f"input_{i}": ("linear", (1.0, 0.0)) for i in range(13)}
    dummy_inputs = np.concatenate([np.ones((1000, 13)), -1 * np.ones((1000, 13))])  # mean zero, variance one
    dummy_targets = np.ones((2000, 1))
    model = builtin_model.build_model(
        model_config=builtin_search_space.get_hp_defaults(),
        input_handler=input_handler,
        inputs_train=dummy_inputs,
        targets_train=dummy_targets,
        seed=42
    )
    return model


def get_default_custom_objects():
    return {
            "swish": tf.keras.activations.swish,
            "WeightedBinaryCrossentropy": keras_tools.WeightedBinaryCrossentropy,
            }


def get_default_training_data():
    input_handler = builtin_inputs.InputHandler(run_config)

    # load test dataset of 10000 events, 5000 signal and 5000 background. 13 input variables are set in test config.
    (inputs,
     targets,
     weights,
     normalized_weights,
     event_nums) = builtin_inputs.get_inputs(run_config,
                                                    nevts=run_config.max_num_events,
                                                    input_vars_list=input_handler.get_vars())

    # use custom manual plus standard scaler
    scaler_class = [builtin_inputs.CustomManualPlusStandardScaler, (input_handler,)]

    # randomly split into training and validation data
    return builtin_inputs.get_training_data(inputs,
                                                   targets,
                                                   weights,
                                                   normalized_weights,
                                                   splitting_cond=0.2,
                                                   preprocessor=scaler_class)


def test_get_hp_defaults():
    hp_defaults = builtin_search_space.get_hp_defaults()
    assert isinstance(hp_defaults, dict)

    for hp_value in hp_defaults.values():
        assert isinstance(hp_value, str) or isinstance(hp_value, int) or isinstance(hp_value, float)


def test_build_search_space():
    default_hps = builtin_search_space.get_hp_defaults()

    # fixed layer sizes
    search_space = builtin_search_space.build_search_space(default_hps, run_config)
    assert isinstance(search_space, dict)
    for hp, hp_value in search_space.items():
        assert (
            isinstance(hp_value, tune.search.sample.Float)
            or isinstance(hp_value, tune.search.sample.Integer)
            or isinstance(hp_value, tune.search.sample.Categorical)
            or isinstance(hp_value, list)
            or isinstance(hp_value, dict)
            or isinstance(hp_value, type(default_hps[hp]))
        )
    assert "units" in search_space.keys() and not all([f"units_{i}" in search_space.keys() for i in range(1, 5)])

    # variable layer sizes with same search space; can have up to 6 layers, thus need units_1, ..., units_6
    optimize_units_before = run_config.optimize_units_per_layer
    run_config.optimize_units_per_layer = True
    search_space = builtin_search_space.build_search_space(default_hps, run_config)
    assert "units" not in search_space.keys() and all([f"units_{i}" in search_space.keys() for i in range(1, 5)])

    search_space_before = run_config.search_space.copy()
    del run_config.search_space["units"]
    run_config.search_space.update({f"units_{i+1}": ('log', 8, int(32-2*i), 1) for i in range(0, 6)})
    search_space = builtin_search_space.build_search_space(default_hps, run_config)
    assert "units" not in search_space.keys() and all([f"units_{i}" in search_space.keys() for i in range(1, 5)])

    run_config.optimize_units_per_layer = optimize_units_before
    run_config.search_space = search_space_before


def test_prepare_search_space_for_PBT():
    default_hps = builtin_search_space.get_hp_defaults()

    # PBT can only mutate l1, l2, dropout, batch_size, Adam-parameters, loss_function and signal_weight. Thus, num_layers,
    # units, activation and initializers should be replaced with defaults
    search_space = {
        "num_layers": ('uniform', 3, 6, 1),
        "units": ('log', 8, 32, 1),
        "activation": ['swish', 'relu'],
        "kernel_initializer": ['glorot_uniform', tf.keras.initializers.HeNormal(seed=42)],
        "bias_initializer": ['zeros'],
        "l1_lambda": ('log', 1e-18, 1e-1),
        "l2_lambda": ('log', 1e-18, 1e-1),
        "dropout": ('uniform', 0.0, 0.5),
        "batch_size": ('uniform', 64., 256.),
        "learning_rate": ('log', 1e-5, 1e-2),
        "Adam_beta_1": ('uniform', 1e-4, 0.99),
        "one_minus_Adam_beta_2": ('log', 1e-5, 0.9999),
        "Adam_epsilon": ('log', 1e-10, 1.0),
        "loss_function": ['BinaryCrossentropy', 'KLDivergence'],
        "loss_signal_weight": ('uniform', 0.5, 1.5),
    }
    to_replace = ["num_layers", "units", "activation", "kernel_initializer", "bias_initializer", "loss_function"]
    search_space_replaced = search_space.copy()
    for hp in search_space_replaced.keys():
        if hp in to_replace:
            search_space_replaced[hp] = default_hps[hp]
    PBT_search_space = builtin_search_space.prepare_search_space_for_PBT(search_space, default_hps)
    assert PBT_search_space == search_space_replaced


@pytest.mark.skipif(os.environ.get('TEST_QUICK') == '1', reason='Test takes more than 5 seconds to run.')
def test_build_model():
    hp_allowed_values = {
        "num_layers": [3],
        "units": [8],
        "activation": ['relu', 'tanh', 'sigmoid', 'LeakyReLU', 'swish', 'mish', 'selu', 'SPLASH'],
        "kernel_initializer": ['auto', 'he_uniform', (tf.keras.initializers.RandomNormal, {"stddev": 0.05, "seed": 42})],
        "bias_initializer": ['auto', 'zeros', (tf.keras.initializers.RandomNormal, {"stddev": 0.05, "seed": 42})],
        "l1_lambda": [0., 1e-5],
        "l2_lambda": [0., 1e-5],
        "dropout": [0.3, 0.],
        "batch_size": [128],
        "learning_rate": [1e-4],
        "Adam_beta_1": [0.9],
        "one_minus_Adam_beta_2": [0.99],
        "Adam_epsilon": [1e-8],
        "loss_function": ['BinaryCrossentropy'],
        "loss_signal_weight": [1.],
    }

    predictions = {
        "num_layers": [
            0.6111191
        ],
        "units": [
            0.6111191
        ],
        "activation": [
            [
                0.11199405789375305,
                0.11199405789375305,
                0.13122156262397766,
                0.24728567898273468,
                0.24728567898273468,
                0.2562752664089203,
                0.49981728196144104,
                0.49981728196144104,
                0.48765021562576294
            ],
            [
                0.48769962787628174,
                0.4389059841632843,
                0.45763760805130005,
                0.8322291374206543,
                0.4011659026145935,
                0.38794681429862976,
                0.6021961569786072,
                0.49995288252830505,
                0.49950286746025085
            ],
            [
                0.24593836069107056,
                0.24593836069107056,
                0.2433507740497589,
                0.2390574812889099,
                0.2390574812889099,
                0.2366105318069458,
                0.16493849456310272,
                0.16493849456310272,
                0.16492164134979248
            ],
            [
                0.12047722935676575,
                0.12047722935676575,
                0.14015184342861176,
                0.25132814049720764,
                0.25132814049720764,
                0.25459209084510803,
                0.49986428022384644,
                0.49986428022384644,
                0.48883968591690063
            ],
            [
                0.9287115335464478,
                0.16108368337154388,
                0.17931674420833588,
                0.8247283697128296,
                0.38233426213264465,
                0.38340455293655396,
                0.5336682200431824,
                0.49999698996543884,
                0.4995178282260895
            ],
            [
                0.23903368413448334,
                0.23903368413448334,
                0.25384485721588135,
                0.290642648935318,
                0.290642648935318,
                0.29449498653411865,
                0.49999508261680603,
                0.49999508261680603,
                0.49936702847480774
            ],
            [
                0.5326128005981445,
                0.5326128005981445,
                0.5336645245552063,
                0.21461912989616394,
                0.21461912989616394,
                0.21455450356006622,
                0.4999467432498932,
                0.4999467432498932,
                0.50677889585495
            ],
            [
                0.11199405789375305,
                0.11199405789375305,
                0.13122156262397766,
                0.24728567898273468,
                0.24728567898273468,
                0.2562752664089203,
                0.49981728196144104,
                0.49981728196144104,
                0.48765021562576294
            ]
        ],
        "kernel_initializer": [
            0.6111191,
            0.025,
            0.49984
        ],
        "bias_initializer": [
            0.6111191,
            0.6111191,
            0.301061
        ],
        "l1_lambda": [
            0.11199405789375305,
            0.11199405789375305
        ],
        "l2_lambda": [
            0.11199405789375305,
            0.11199405789375305
        ],
        "dropout": [
            0.11199405789375305,
            0.11199405789375305
        ],
        "batch_size": [
            0.6111191
        ],
        "learning_rate": [
            0.6111191
        ],
        "Adam_beta_1": [
            0.6111191
        ],
        "one_minus_Adam_beta_2": [
            0.6111191
        ],
        "Adam_epsilon": [
            0.6111191
        ],
        "loss_function": [
            0.6111191
        ],
        "loss_signal_weight": [
            0.6111191
        ]
    }

    # get dummy input handler with linear input scaling
    input_handler = builtin_inputs.InputHandler(run_config)
    input_handler.set_vars([f"input_{i}" for i in range(13)])
    input_handler.scaling_dict = {f"input_{i}": ("linear", (1.0, 0.0)) for i in range(13)}
    dummy_inputs = np.concatenate([np.ones((1000, 13)), -1 * np.ones((1000, 13))])  # mean zero, variance one
    dummy_targets = np.ones((2000, 1))

    for hp_to_test in hp_allowed_values.keys():
        if len(hp_allowed_values[hp_to_test]) == 1 or "initializer" in hp_to_test:
            continue
        if hp_to_test != "activation":
            for i, (hp_value, pred) in enumerate(zip(hp_allowed_values[hp_to_test], predictions[hp_to_test])):
                model_config = {}
                model_config[hp_to_test] = hp_value

                for hp_fixed in hp_allowed_values.keys():
                    if hp_fixed != hp_to_test:
                        model_config[hp_fixed] = hp_allowed_values[hp_fixed][0]

                model = builtin_model.build_model(model_config=model_config,
                                                  input_handler=input_handler,
                                                  inputs_train=dummy_inputs,
                                                  targets_train=dummy_targets,
                                                  seed=42)
                print(hp_to_test)
                # predictions[hp_to_test][i] = float(model(np.linspace(-1, 1, 13, endpoint=True).reshape((1, 13))).numpy()[0][0])
                assert abs(model(np.linspace(-1, 1, 13, endpoint=True).reshape((1, 13))) - pred) < 1e-6
        else:
            for a, hp_value in enumerate(hp_allowed_values[hp_to_test]):
                for k in range(3):
                    for b in range(3):
                        model_config = {}
                        model_config["activation"] = hp_value
                        model_config["kernel_initializer"] = hp_allowed_values["kernel_initializer"][k]
                        model_config["bias_initializer"] = hp_allowed_values["bias_initializer"][b]

                        for hp_fixed in hp_allowed_values.keys():
                            if hp_fixed not in ["activation", "kernel_initializer", "bias_initializer"]:
                                model_config[hp_fixed] = hp_allowed_values[hp_fixed][0]

                        model = builtin_model.build_model(model_config=model_config,
                                                          input_handler=input_handler,
                                                          inputs_train=dummy_inputs,
                                                          targets_train=dummy_targets,
                                                          seed=42)
                        print(hp_value, k, b)
                        pred = predictions["activation"][a][3 * k + b]
                        # predictions["activation"][a][3 * k + b] = float(model(np.linspace(-1, 1, 13, endpoint=True).reshape((1, 13))).numpy()[0][0])
                        assert abs(model(np.linspace(-1, 1, 13, endpoint=True).reshape((1, 13))) - pred) < 1e-6
    # print(json.dumps(predictions, indent=4))

    # test units_i priority
    hp_allowed_values.update({
        "units_1": [8],
        "units_2": [4],
        "units_3": [2],
    })
    predictions = {
        "num_layers": [
            0.66367704
        ],
        "units": [
            0.66367704
        ],
        "units_1": [
            0.66367704
        ],
        "units_2": [
            0.66367704
        ],
        "units_3": [
            0.66367704
        ],
        "activation": [
            0.5740598440170288,
            0.22188419103622437,
            0.4631745517253876,
            0.5869430303573608,
            0.5426632761955261,
            0.5887803435325623,
            0.6611102223396301,
            0.5740598440170288
        ],
        "kernel_initializer": [
            0.5740598440170288,
            0.6003352403640747,
            0.4999960660934448
        ],
        "bias_initializer": [
            0.5740598440170288,
            0.5740598440170288,
            0.5549465417861938
        ],
        "l1_lambda": [
            0.5740598440170288,
            0.5740598440170288
        ],
        "l2_lambda": [
            0.5740598440170288,
            0.5740598440170288
        ],
        "dropout": [
            0.5740598440170288,
            0.5740598440170288
        ],
        "batch_size": [
            0.66367704
        ],
        "learning_rate": [
            0.66367704
        ],
        "Adam_beta_1": [
            0.66367704
        ],
        "one_minus_Adam_beta_2": [
            0.66367704
        ],
        "Adam_epsilon": [
            0.66367704
        ],
        "loss_function": [
            0.66367704
        ],
        "loss_signal_weight": [
            0.66367704
        ]
    }
    for hp_to_test in hp_allowed_values.keys():
        if len(hp_allowed_values[hp_to_test]) == 1:
            continue
        for i, (hp_value, pred) in enumerate(zip(hp_allowed_values[hp_to_test], predictions[hp_to_test])):
            model_config = {}
            model_config[hp_to_test] = hp_value

            for hp_fixed in hp_allowed_values.keys():
                if hp_fixed != hp_to_test:
                    model_config[hp_fixed] = hp_allowed_values[hp_fixed][0]

            model = builtin_model.build_model(model_config=model_config,
                                              input_handler=input_handler,
                                              inputs_train=dummy_inputs,
                                              targets_train=dummy_targets,
                                              seed=42)
            print(hp_to_test)
            # predictions[hp_to_test][i] = float(model(np.linspace(-1, 1, 13, endpoint=True).reshape((1, 13))).numpy()[0][0])
            assert abs(model.predict(np.linspace(-1, 1, 13, endpoint=True).reshape((1, 13))) - pred) < 1e-6
    # print(json.dumps(predictions, indent=4))
    # assert 1 == 0


def test_update_model():
    max_seeds = tools.get_max_seeds()
    np.random.seed(42)
    python_random.seed(np.random.randint(*max_seeds))
    keras_set_seed(np.random.randint(*max_seeds))
    tf_random.set_seed(np.random.randint(*max_seeds))

    model = tf.keras.models.load_model("tests/models/model_default_100_epochs.h5", custom_objects=get_default_custom_objects())

    # check evaluation
    (_,
     inputs_split,
     targets_split,
     _,
     normalized_weights_split) = get_default_training_data()
    trained_val_loss = model.evaluate(x=inputs_split[1], y=targets_split[1])
    assert abs(trained_val_loss - 0.53826028) < 1e-7

    # check updatable hyperparameters
    default_hps = builtin_search_space.get_hp_defaults()
    for layer in model.layers:
        if isinstance(layer, tf.keras.layers.Dense) and layer.name != "output":
            assert layer.kernel_regularizer.l1 == default_hps["l1_lambda"]
            assert layer.kernel_regularizer.l2 == default_hps["l2_lambda"]

    # continue training for 1 epoch, loss should be low and evaluation similar
    history = model.fit(
        x=inputs_split[0],
        y=targets_split[0],
        sample_weight=normalized_weights_split[0],
        batch_size=default_hps["batch_size"],
        shuffle=False,
        epochs=1
    )
    assert abs(history.history["loss"][-1] - 0.51616) < 1e-5
    trained_val_loss = model.evaluate(x=inputs_split[1], y=targets_split[1])
    assert abs(trained_val_loss - 0.53792) < 1e-5

    # update regularization, train for 1 epoch; loss should be high, evaluation still similar (weights not reset!)
    default_hps.update({
        "dropout": 0.3,
        "l1_lambda": 1e-6,
        "l2_lambda": 1e-6,
    })
    model = builtin_model.update_model(model, default_hps)
    model = builtin_model.compile_model(model, default_hps, first_compile=False)  # preserve optimizer state
    history = model.fit(
        x=inputs_split[0],
        y=targets_split[0],
        sample_weight=normalized_weights_split[0],
        batch_size=default_hps["batch_size"],
        shuffle=False,
        epochs=1
    )
    assert abs(history.history["loss"][-1] - 0.59596) < 1e-5
    trained_val_loss = model.evaluate(x=inputs_split[1], y=targets_split[1])
    assert abs(trained_val_loss - 0.54785) < 1e-4


@pytest.mark.skipif(os.environ.get('TEST_QUICK') == '1', reason='Test takes more than 5 seconds to run.')
def test_compile_model():
    # get the default model
    default_hps = builtin_search_space.get_hp_defaults()
    model = get_default_model()

    # some example metrics
    metrics = [tf.keras.metrics.AUC(name="AUC")]
    weighted_metrics = [tf.keras.metrics.BinaryAccuracy(name="weighted_BA"),
                        tf.keras.metrics.AUC(name="weighted_AUC"),
                        tf.keras.metrics.BinaryCrossentropy(name="weighted_BCE")]

    # first compile
    model = builtin_model.compile_model(model, default_hps, metrics=metrics, weighted_metrics=weighted_metrics)

    # fit for 3 epochs
    (_,
     inputs_split,
     targets_split,
     _,
     normalized_weights_split) = get_default_training_data()
    history = model.fit(
        x=inputs_split[0],
        y=targets_split[0],
        sample_weight=normalized_weights_split[0],
        batch_size=default_hps["batch_size"],
        shuffle=False,
        epochs=3
    )

    # check if metrics were added
    assert [metric in history.history.keys() for metric in metrics]
    assert [weighted_metric in history.history.keys() for weighted_metric in weighted_metrics]

    # save model for following tests, will be deleted later
    model.save("tests/model_test_compile.h5")

    # change nothing, training should continue normally
    model_unchanged = tf.keras.models.load_model("tests/model_test_compile.h5", custom_objects=get_default_custom_objects())
    model_unchanged = builtin_model.compile_model(model_unchanged, default_hps, metrics=metrics,
                                                          weighted_metrics=weighted_metrics, first_compile=False)
    history_unchanged = model_unchanged.fit(
        x=inputs_split[0],
        y=targets_split[0],
        sample_weight=normalized_weights_split[0],
        batch_size=default_hps["batch_size"],
        shuffle=False,
        epochs=3
    )
    assert history_unchanged.history["loss"][0] < history.history["loss"][-1]  # loss decreased after first epoch compared to before
    assert history_unchanged.history["loss"][-1] < history_unchanged.history["loss"][0]  # loss decreased throughout training
    assert history_unchanged.history["weighted_AUC"][0] > history.history["weighted_AUC"][-1]  # same for AUC
    assert history_unchanged.history["weighted_AUC"][-1] > history_unchanged.history["weighted_AUC"][0]

    # change Adam hyperparameters; setting learning rate to zero still changes weights due to BatchNormalization.
    # Instead, choose really high LR to see if training diverges. Since the updates are scaled down over time, we train
    # for one epoch, then increase the learning rate, which should result in a continous diversion
    model_lr = tf.keras.models.load_model("tests/model_test_compile.h5", custom_objects=get_default_custom_objects())
    hps_lr = default_hps.copy()
    hps_lr["learning_rate"] = 1
    model_lr = builtin_model.compile_model(model_lr, hps_lr, metrics=metrics, weighted_metrics=weighted_metrics,
                                                   first_compile=False)
    history_lr_1 = model_lr.fit(
        x=inputs_split[0],
        y=targets_split[0],
        sample_weight=normalized_weights_split[0],
        batch_size=hps_lr["batch_size"],
        shuffle=False,
        epochs=1
    )
    hps_lr["learning_rate"] = 10
    model_lr = builtin_model.compile_model(model_lr, hps_lr, metrics=metrics, weighted_metrics=weighted_metrics,
                                                   first_compile=False)
    history_lr_2 = model_lr.fit(
        x=inputs_split[0],
        y=targets_split[0],
        sample_weight=normalized_weights_split[0],
        batch_size=hps_lr["batch_size"],
        shuffle=False,
        epochs=1
    )
    hps_lr["learning_rate"] = 100
    model_lr = builtin_model.compile_model(model_lr, hps_lr, metrics=metrics, weighted_metrics=weighted_metrics,
                                                   first_compile=False)
    history_lr_3 = model_lr.fit(
        x=inputs_split[0],
        y=targets_split[0],
        sample_weight=normalized_weights_split[0],
        batch_size=hps_lr["batch_size"],
        shuffle=False,
        epochs=1
    )
    assert history_lr_3.history["loss"][0] > history_lr_2.history["loss"][0] and \
           history_lr_2.history["loss"][0] > history_lr_1.history["loss"][0] and \
           history_lr_1.history["loss"][0] > history.history["loss"][-1]

    # Adam momentum parameters are harder to test, just verify that the result changes
    model_beta_1 = tf.keras.models.load_model("tests/model_test_compile.h5", custom_objects=get_default_custom_objects())
    hps_beta_1 = default_hps.copy()
    hps_beta_1["Adam_beta_1"] = 0.5
    model_beta_1 = builtin_model.compile_model(model_beta_1, hps_beta_1, metrics=metrics, weighted_metrics=weighted_metrics,
                                                       first_compile=False)
    history_beta_1 = model_beta_1.fit(
        x=inputs_split[0],
        y=targets_split[0],
        sample_weight=normalized_weights_split[0],
        batch_size=hps_lr["batch_size"],
        shuffle=False,
        epochs=3
    )
    assert all([history_beta_1.history["loss"][i] != history_unchanged.history["loss"][i] for i in range(3)])

    model_beta_2 = tf.keras.models.load_model("tests/model_test_compile.h5", custom_objects=get_default_custom_objects())
    hps_beta_2 = default_hps.copy()
    hps_beta_2["one_minus_Adam_beta_2"] = 0.9
    model_beta_2 = builtin_model.compile_model(model_beta_2, hps_beta_2, metrics=metrics, weighted_metrics=weighted_metrics,
                                                       first_compile=False)
    history_beta_2 = model_beta_2.fit(
        x=inputs_split[0],
        y=targets_split[0],
        sample_weight=normalized_weights_split[0],
        batch_size=hps_lr["batch_size"],
        shuffle=False,
        epochs=3
    )
    assert all([history_beta_2.history["loss"][i] != history_unchanged.history["loss"][i] for i in range(3)])
    assert all([history_beta_2.history["loss"][i] != history_beta_1.history["loss"][i] for i in range(3)])

    model_epsilon = tf.keras.models.load_model("tests/model_test_compile.h5", custom_objects=get_default_custom_objects())
    hps_epsilon = default_hps.copy()

    hps_epsilon["Adam_epsilon"] = 0.1
    model_epsilon = builtin_model.compile_model(model_epsilon, hps_lr, metrics=metrics, weighted_metrics=weighted_metrics,
                                                        first_compile=False)
    history_epsilon = model_epsilon.fit(
        x=inputs_split[0],
        y=targets_split[0],
        sample_weight=normalized_weights_split[0],
        batch_size=hps_lr["batch_size"],
        shuffle=False,
        epochs=3
    )
    assert all([history_epsilon.history["loss"][i] != history.history["loss"][i] for i in range(3)])
    assert all([history_epsilon.history["loss"][i] != history_beta_1.history["loss"][i] for i in range(3)])
    assert all([history_epsilon.history["loss"][i] != history_beta_2.history["loss"][i] for i in range(3)])

    os.remove("tests/model_test_compile.h5")


@pytest.mark.skipif(os.environ.get('TEST_QUICK') == '1', reason='Test takes more than 5 seconds to run.')
def test_early_stopper_for_tuning():
    # we need a model for the early stopper, create a dummy model for this purpose
    class DummyModel:
        # dummy inputs and targets
        inputs_train = np.array([1., 2., 3.])
        inputs_val = np.array([4., 5., 6.])
        targets_train = np.array([1.])
        targets_val = np.array([1.])
        normalized_weights_train = np.array([1.])
        normalized_weights_val = np.array([1.])
        def __init__(self):
            # simulated predictions
            self.epoch = 0
            self.sim_predictions_train = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99, 0.995])
            self.sim_predictions_val = np.array([0.1, 0.2, 0.3, 0.4, 0.49, 0.58, 0.66, 0.72, 0.73, 0.71, 0.67, 0.61, 0.5])

            # we need a Keras model for the early stopper to save and load
            self.dummy_model_to_save = get_default_model()
            self.dummy_model_to_save.compile()

            # fields for the early stopper
            self.stop_training = False

        def predict(self, inputs, verbose=0):
            if (inputs == self.inputs_train).all():
                return self.sim_predictions_train[self.epoch]
            else:
                self.epoch += 1
                return self.sim_predictions_val[self.epoch - 1]

        def save(self, path, save_format=None):
            print(f"Dummy model: would save model to {path}.")
            self.dummy_model_to_save.save(path, save_format=save_format)


        def get_weights(self):
            return self.dummy_model_to_save.get_weights()

        def set_weights(self, weights):
            pass

    # create some dummy custom and composite metrics and overtraining conditions
    def difference_loss(targets, predictions, sample_weight=None):
        if sample_weight is None:
            return np.mean(np.abs(targets - predictions), axis=0)
        else:
            return np.mean(np.abs(sample_weight * (targets - predictions)), axis=0)

    custom_metrics = [
        ('difference_loss', difference_loss),
    ]
    composite_metrics = [
        ('train_plus_val_loss', ('train_difference_loss', 'val_difference_loss'), lambda x, y: x + y)
    ]
    overtraining_conditions = [
        ('train_div_val_loss', ('train_difference_loss', 'val_difference_loss'), lambda x, y: np.divide(x, y) < 0.8)
    ]

    # to simulate being in a Tune session, create the necessary multiprocessing objects
    report_event = mp.Event()
    report_queue = mp.Queue()
    report_queue_read_event = mp.Event()
    termination_event = mp.Event()
    in_tune_session = True

    # instantiate the early stopper, start without overtraining conditions to check the normal early stopping
    # functionality; since best epoch (regarding validation 'difference loss') is 9 and patience is 2, we're expecting
    # the termination after epoch 11
    early_stopper = keras_training.EarlyStopperForKerasTuning(
        monitor=('val_difference_loss', 'min'),
        custom_metrics=custom_metrics,
        composite_metrics=composite_metrics,
        overfitting_conditions=[],
        patience_improvement=2,
        patience_overfitting=np.inf,
        inputs_train=DummyModel.inputs_train,
        inputs_val=DummyModel.inputs_val,
        targets_train=DummyModel.targets_train,
        targets_val=DummyModel.targets_val,
        weights_train=DummyModel.normalized_weights_train,
        weights_val=DummyModel.normalized_weights_val,
        restore_best_weights=True,
        verbose=1,
        create_checkpoints=True,
        report_event=report_event,
        report_queue=report_queue,
        report_queue_read_event=report_queue_read_event,
        termination_event=termination_event,
        in_tune_session=in_tune_session
    )
    # instantiate and set the dummy model
    dummy_model = DummyModel()
    early_stopper.model = dummy_model

    # since the training usually runs in a subprocess, we need to do that here too. Within the subprocess, the expected
    # behaviour is verified
    def simulated_training(expected_best_epoch, expected_stopped_epoch):
        # do the simulated training
        i = 0
        while not early_stopper.model.stop_training:
            early_stopper.on_epoch_end(i)
            i += 1
        termination_event.set()
        assert early_stopper.best_epoch + 1 == expected_best_epoch
        assert early_stopper.stopped_epoch + 1 == expected_stopped_epoch
    p = mp.Process(target=simulated_training, args=(9, 11), daemon=True)
    p.start()

    # wait for the reports as done in the training function and check if all expected metrics were reported
    i = 0
    expected_metrics = {"train_difference_loss", "val_difference_loss", "best_train_difference_loss",
                        "best_val_difference_loss", "last_valid_val_difference_loss", "train_plus_val_loss",
                        "best_train_plus_val_loss", "early_stopped"}
    while True:
        report_event.wait(timeout=1)
        if report_event.is_set():
            report_event.clear()
            report = report_queue.get()
            print(f"Early stopper reported (epoch {i+1}): {report}")
            assert set(report.keys()) == expected_metrics
            report_queue_read_event.set()
            i += 1
        elif termination_event.is_set():
            termination_event.clear()
            break

    # exceptions are not caught by pytest if raised in a child process, but we can use the process's exit code
    p.join()
    assert not p.exitcode

    # cleanup
    shutil.rmtree("checkpoint_dir")

    # now use the overfitting condition, but let the overfitting patience be infinity. The first overfitted epoch is
    # epoch 8, because (1-0.7) / (1-0.66) = 0.3 / 0.34 = 0.88 > 0.8 but (1-0.8) / (1-0.72) = 0.2 / 0.28 = 0.71 < 0.8.
    # Since the "best" value is only updated if an epoch is not overfitted, the validation_difference_loss of epoch 7
    # remains the "best" value even though validation_difference_loss improves until epoch 11. As a result, the patience
    # only starts counting once the validation_difference_loss is worse than the value of epoch 7, not worse than the
    # best seen value (epoch 9). This is intended behaviour since if for some reason, a degration of the metric results
    # in an not-overfitted epoch, the difference to the best previously seen not-overfitted epoch is relevant, not the
    # best seen epoch in general.
    # The first epoch with validation_difference_loss worse than epoch 7 is epoch 12, thus we expect termination after
    # epoch 13. Epoch 7 should be returned as the best epoch.
    early_stopper = keras_training.EarlyStopperForKerasTuning(
        monitor=('val_difference_loss', 'min'),
        custom_metrics=custom_metrics,
        composite_metrics=composite_metrics,
        overfitting_conditions=overtraining_conditions,
        patience_improvement=2,
        patience_overfitting=np.inf,
        inputs_train=DummyModel.inputs_train,
        inputs_val=DummyModel.inputs_val,
        targets_train=DummyModel.targets_train,
        targets_val=DummyModel.targets_val,
        weights_train=DummyModel.normalized_weights_train,
        weights_val=DummyModel.normalized_weights_val,
        restore_best_weights=True,
        verbose=1,
        create_checkpoints=True,
        report_event=report_event,
        report_queue=report_queue,
        report_queue_read_event=report_queue_read_event,
        termination_event=termination_event,
        in_tune_session=in_tune_session
    )
    # instantiate and set the dummy model
    dummy_model = DummyModel()
    early_stopper.model = dummy_model

    # start the simulated training
    p = mp.Process(target=simulated_training, args=(7, 13), daemon=True)
    p.start()

    # wait for the reports as done in the training function and check if all expected metrics were reported
    i = 0
    expected_metrics = {"train_difference_loss", "val_difference_loss", "best_train_difference_loss",
                        "best_val_difference_loss", "last_valid_val_difference_loss", "train_plus_val_loss",
                        "best_train_plus_val_loss", "early_stopped"}
    while True:
        report_event.wait(timeout=1)
        if report_event.is_set():
            report_event.clear()
            report = report_queue.get()
            print(f"Early stopper reported (epoch {i + 1}): {report}")
            assert set(report.keys()) == expected_metrics
            report_queue_read_event.set()
            i += 1
        elif termination_event.is_set():
            termination_event.clear()
            break

    # exceptions are not caught by pytest if raised in a child process, but we can use the process's exit code
    p.join()
    assert not p.exitcode

    # cleanup
    shutil.rmtree("checkpoint_dir")

    # Now set the overfitting patience to 2 as well. We now expect the training to terminate after epoch 9 and epoch 7
    # should still be the best epoch.
    early_stopper = keras_training.EarlyStopperForKerasTuning(
        monitor=('val_difference_loss', 'min'),
        custom_metrics=custom_metrics,
        composite_metrics=composite_metrics,
        overfitting_conditions=overtraining_conditions,
        patience_improvement=2,
        patience_overfitting=2,
        inputs_train=DummyModel.inputs_train,
        inputs_val=DummyModel.inputs_val,
        targets_train=DummyModel.targets_train,
        targets_val=DummyModel.targets_val,
        weights_train=DummyModel.normalized_weights_train,
        weights_val=DummyModel.normalized_weights_val,
        restore_best_weights=True,
        verbose=1,
        create_checkpoints=True,
        report_event=report_event,
        report_queue=report_queue,
        report_queue_read_event=report_queue_read_event,
        termination_event=termination_event,
        in_tune_session=in_tune_session
    )
    # instantiate and set the dummy model
    dummy_model = DummyModel()
    early_stopper.model = dummy_model

    # start the simulated training
    p = mp.Process(target=simulated_training, args=(7, 9), daemon=True)
    p.start()

    # wait for the reports as done in the training function and check if all expected metrics were reported
    i = 0
    expected_metrics = {"train_difference_loss", "val_difference_loss", "best_train_difference_loss",
                        "best_val_difference_loss", "last_valid_val_difference_loss", "train_plus_val_loss",
                        "best_train_plus_val_loss", "early_stopped"}
    while True:
        report_event.wait(timeout=1)
        if report_event.is_set():
            report_event.clear()
            report = report_queue.get()
            print(f"Early stopper reported (epoch {i + 1}): {report}")
            assert set(report.keys()) == expected_metrics
            report_queue_read_event.set()
            i += 1
        elif termination_event.is_set():
            termination_event.clear()
            break

    # exceptions are not caught by pytest if raised in a child process, but we can use the process's exit code
    p.join()
    assert not p.exitcode

    # cleanup
    shutil.rmtree("checkpoint_dir")
