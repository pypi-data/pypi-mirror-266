# -*- coding: utf-8 -*-
"""A module that provides functionality to prepare and update a Keras multilayer perceptron."""
import logging
from typing import Union, Optional
import random as python_random
import os
import json

import numpy as np

import tensorflow as tf
from tensorflow.keras import backend as K

import OPTIMA.core.tools
import OPTIMA.builtin.inputs
import OPTIMA.keras.tools
from OPTIMA.core.model import model_config_type


def build_model(
    model_config: model_config_type,
    input_handler: OPTIMA.builtin.inputs.InputHandler,
    inputs_train: np.ndarray,
    targets_train: np.ndarray,
    seed: Optional[int] = None,
) -> tf.keras.Model:
    """Builds a Functional `Keras` model for the hyperparameters provided in the model-config.

    This function is specific to multilayer perceptrons for classification. As such, only the corresponding
    hyperparameters are supported. To use a different type of `Keras` model, a ``build_model``-function needs to be
    defined in the run-config.

    The following hyperparameters are supported:

    - ``'num_layers'``:    number of hidden layers
    - ``'units'``:         number of neurons per hidden layer
    - ``'units_i'``:       number of neurons in hidden layer `i` (has higher priority than 'units')
    - ``'activation'``:    activation function; supported are:
        - ``'relu'``:      Rectified Linear Unit `A(x) = max(0, x)`
        - ``'tanh'``:      Hyperbolic Tangent `A(x) = tanh(x)`
        - ``'sigmoid'``:   Logistic Sigmoid `A(x) = 1 / (1 + e^(-x))`
        - ``'LeakyReLU'``: `A(x) = max(ax, x), 0 <= a <= 1`; here: ``a = 0.1``
        - ``'swish'``:     `A(x) = x / (1 + e^(-ax))`; here: ``a = 1``
        - ``'mish'``:      `A(x) = x * tanh(ln(1 + e^(x)))`
        - ``'selu'``:      `A(x) = scale * (max(0, x) + alpha * (e^(x) - 1) * max(0, -x))`, `scale = 1.05070098`, `alpha = 1.67326324`
        - ``'SPLASH'``: see https://arxiv.org/abs/2006.08947
    - ``'kernel_initializer'`` and ``'bias_initializer'``: initializers of the weights and biases of the hidden layers.
      Supported are all Keras supported initializers, both as a string or as a tuple of type ``tuple[Type, dict]``
      containing the class reference and a dictionary of necessary keyword arguments. Additionally, a value of
      ``'auto'`` can be given to automatically choose suitable initializers. The automatic choices depend on the
      activation function and are as follows (`activation: kernel_initializer, bias_initializer`):
        - ``'relu'``: ``'he_normal'``, ``'zeros'`` (https://arxiv.org/pdf/1805.08266.pdf)
        - ``'tanh'``: ``Orthogonal(gain=2)``, ``RandomNormal(stddev=0.322)`` (https://arxiv.org/abs/1711.04735)
        - ``'sigmoid'``: ``'glorot_uniform'``, ``'zeros'`` (https://proceedings.mlr.press/v9/glorot10a.html)
        - ``'LeakyReLU'``: ``'he_normal'``, ``'zeros'``
        - ``'swish'``: ``VarianceScaling(scale=2.952, distribution='truncated_normal')``, ``RandomNormal(stddev=0.2)``
          (https://arxiv.org/abs/1805.08266)
        - ``'mish'``: ``'he_normal'``, ``'zeros'``
        - ``'selu'``: ``'lecun_normal'``, ``'zeros'`` (https://arxiv.org/abs/1706.02515)
        - ``'SPLASH'``: ``'he_normal'``, ``'zeros'``
    - ``'l1_lambda'`` and ``'l2_lambda'``: strengths of the `L1` and `L2` regularization applied to all hidden layers
    - ``'dropout'``: dropout rate. If the `SELU` activation function is used, Alpha-Dropout is applied instead of regular dropout.

    While technically possible, individual dropout rates and regularizer strengths per layer have not yet been implemented.

    The input variables are normalized using a ``OPTIMA.keras.tools.NonLinearNormalization``-layer that is adapted to
    the training data.

    For all activation functions other than `SELU`, a ``BatchNormalization`` layer is added between the outputs of each
    hidden layer and the corresponding activation layer. The output layer consists of a single neuron with sigmoid
    activation, ``'glorot_uniform'`` kernel initializer and ``'zeros'`` bias initializer.

    The activation function and the number of neurons of the output layer depends on the value of ``output_shape``. If
    ``output_shape[1]`` is ``1``, then a single output neuron with sigmoid activation will be used. If, however,
    ``output_shape[1]`` is larger than ``1``, ``output_shape[1]`` neurons with softmax activation are used instead.

    An example summary of an MLP with two hidden layers, 64 neurons in both hidden layers, `swish` activation and dropout
    of ``0.1`` is given below.

    Parameters
    ----------
    model_config : model_config_type
        Dictionary containing the values for each hyperparameter
    input_handler : OPTIMA.builtin.inputs.InputHandler
        Instance of the ``InputHandler``-class.
    inputs_train : np.ndarray
        The input features for the training dataset. This is used to adapt the normalization layer.
    targets_train : np.ndarray
        The target labels for the training dataset. It is used to infer the number of output neurons.
    seed : Optional[int]
        If provided, the random seed is set globally for numpy.random, random (python built-in) and tensorflow.random to
        ensure reproducibility. (Default value = None)

    Returns
    -------
    tf.keras.Model
        The Functional `Keras` model for the given hyperparameters.

    Examples
    --------
    Example summary of an MLP with two hidden layers, 64 neurons in both hidden layers, `swish` activation and dropout
    of ``0.1``:

    ```python
    Model: "OPTIMA_MLP"
    _________________________________________________________________
     Layer (type)                Output Shape              Param #
    =================================================================
     input_1 (InputLayer)        [(None, 17)]              0

     normalization (NonLinearNor  (None, 17)               35
     malization)

     dense (Dense)               (None, 64)                1152

     batch_normalization (BatchN  (None, 64)               256
     ormalization)

     re_lu (ReLU)                (None, 64)                0

     dropout (Dropout)           (None, 64)                0

     dense_1 (Dense)             (None, 64)                4160

     batch_normalization_1 (Batc  (None, 64)               256
     hNormalization)

     re_lu_1 (ReLU)              (None, 64)                0

     dropout_1 (Dropout)         (None, 64)                0

     dense_2 (Dense)             (None, 64)                4160

     batch_normalization_2 (Batc  (None, 64)               256
     hNormalization)

     re_lu_2 (ReLU)              (None, 64)                0

     dropout_2 (Dropout)         (None, 64)                0

     dense_3 (Dense)             (None, 64)                4160

     batch_normalization_3 (Batc  (None, 64)               256
     hNormalization)

     re_lu_3 (ReLU)              (None, 64)                0

     dropout_3 (Dropout)         (None, 64)                0

     output (Dense)              (None, 3)                 195

    =================================================================
    Total params: 14,886
    Trainable params: 14,339
    Non-trainable params: 547
    _________________________________________________________________
    ```
    """
    # set random seeds for reproducibility; unfortunately, when e.g. initializers are given as strings there is no way
    # to ensure reproducibility other than by setting the global seeds
    if seed is not None:
        max_seeds = OPTIMA.core.tools.get_max_seeds()
        np.random.seed(seed)
        python_random.seed(np.random.randint(*max_seeds))
        tf.keras.utils.set_random_seed(np.random.randint(*max_seeds))
        tf.random.set_seed(np.random.randint(*max_seeds))

    # get activation function from config + set kernel and bias initializer if set to auto; warning: can't instanciate
    # activation layer and kernels here, we need one instance per layer!
    if (
        model_config["activation"] == "relu"
    ):  # auto choices should be close to optimal; https://arxiv.org/pdf/1805.08266.pdf
        activation_layer = (tf.keras.layers.ReLU, {})
        if model_config["kernel_initializer"] == "auto":
            kernel_initializer = (tf.keras.initializers.HeNormal, {})
        else:
            kernel_initializer = model_config["kernel_initializer"]
        if model_config["bias_initializer"] == "auto":
            bias_initializer = (tf.keras.initializers.Zeros, {})
        else:
            bias_initializer = model_config["bias_initializer"]
    elif model_config["activation"] == "tanh":  # auto choices according to https://arxiv.org/pdf/1711.04735.pdf
        activation_layer = (tf.keras.layers.Activation, {"activation": tf.keras.activations.tanh})
        if model_config["kernel_initializer"] == "auto":
            kernel_initializer = (tf.keras.initializers.Orthogonal, {"gain": 2})
        else:
            kernel_initializer = model_config["kernel_initializer"]
        if model_config["bias_initializer"] == "auto":
            bias_initializer = (tf.keras.initializers.RandomNormal, {"stddev": 0.322})
        else:
            bias_initializer = model_config["bias_initializer"]
    elif (
        model_config["activation"] == "sigmoid"
    ):  # auto choices according to https://proceedings.mlr.press/v9/glorot10a.html
        activation_layer = (tf.keras.layers.Activation, {"activation": tf.keras.activations.sigmoid})
        if model_config["kernel_initializer"] == "auto":
            kernel_initializer = (tf.keras.initializers.GlorotUniform, {})
        else:
            kernel_initializer = model_config["kernel_initializer"]
        if model_config["bias_initializer"] == "auto":
            bias_initializer = (tf.keras.initializers.Zeros, {})
        else:
            bias_initializer = model_config["bias_initializer"]
    elif model_config["activation"] == "LeakyReLU":  # auto choices not optimized!
        activation_layer = (tf.keras.layers.LeakyReLU, {"alpha": 0.1})
        if model_config["kernel_initializer"] == "auto":
            kernel_initializer = (tf.keras.initializers.HeNormal, {})
        else:
            kernel_initializer = model_config["kernel_initializer"]
        if model_config["bias_initializer"] == "auto":
            bias_initializer = (tf.keras.initializers.Zeros, {})
        else:
            bias_initializer = model_config["bias_initializer"]
    elif (
        model_config["activation"] == "swish"
    ):  # auto choices according to https://arxiv.org/pdf/1805.08266.pdf, but for not so deep networks I found 'he_uniform' and 'zeros' to work better
        activation_layer = (tf.keras.layers.Activation, {"activation": tf.keras.activations.swish})
        if model_config["kernel_initializer"] == "auto":
            kernel_initializer = (
                tf.keras.initializers.VarianceScaling,
                {"scale": 2.952, "distribution": "truncated_normal"},
            )
        else:
            kernel_initializer = model_config["kernel_initializer"]
        if model_config["bias_initializer"] == "auto":
            bias_initializer = (tf.keras.initializers.RandomNormal, {"stddev": 0.2})
        else:
            bias_initializer = model_config["bias_initializer"]
    elif model_config["activation"] == "mish":  # auto choices not optimized!
        activation_layer = (OPTIMA.keras.tools.Mish, {})
        if model_config["kernel_initializer"] == "auto":
            kernel_initializer = (tf.keras.initializers.HeNormal, {})
        else:
            kernel_initializer = model_config["kernel_initializer"]
        if model_config["bias_initializer"] == "auto":
            bias_initializer = (tf.keras.initializers.Zeros, {})
        else:
            bias_initializer = model_config["bias_initializer"]
    elif model_config["activation"] == "selu":  # weights_initializer should be fine, bias not optimized!
        activation_layer = (tf.keras.layers.Activation, {"activation": tf.keras.activations.selu})
        if model_config["kernel_initializer"] == "auto":
            kernel_initializer = (tf.keras.initializers.LecunNormal, {})
        else:
            kernel_initializer = model_config["kernel_initializer"]
        if model_config["bias_initializer"] == "auto":
            bias_initializer = (tf.keras.initializers.Zeros, {})
        else:
            bias_initializer = model_config["bias_initializer"]
    elif model_config["activation"] == "SPLASH":  # auto choices not optimized!
        activation_layer = (OPTIMA.keras.tools.SPLASHLayer, {"b": [0, 1, 2, 2.5]})
        if model_config["kernel_initializer"] == "auto":
            kernel_initializer = (tf.keras.initializers.HeNormal, {})
        else:
            kernel_initializer = model_config["kernel_initializer"]
        if model_config["bias_initializer"] == "auto":
            bias_initializer = (tf.keras.initializers.Zeros, {})
        else:
            bias_initializer = model_config["bias_initializer"]

    # get and adapt the normalization layer
    norm_layer = OPTIMA.keras.tools.NonLinearNormalization(
        input_handler.get_vars(), input_handler.get_nonlinear_scaling(), name="normalization"
    )
    norm_layer.adapt(inputs_train)

    inputs = tf.keras.Input(shape=inputs_train.shape[1:])
    x = norm_layer(inputs)
    for i in range(1, model_config["num_layers"] + 1):
        if ("units_" + str(i)) in model_config.keys():
            units_i = model_config["units_" + str(i)]
        else:
            units_i = model_config["units"]
        kernel_initializer_layer = (
            kernel_initializer
            if isinstance(kernel_initializer, str)
            else kernel_initializer[0](**kernel_initializer[1])
        )
        bias_initializer_layer = (
            bias_initializer if isinstance(bias_initializer, str) else bias_initializer[0](**bias_initializer[1])
        )
        x = tf.keras.layers.Dense(
            units=units_i,
            kernel_initializer=kernel_initializer_layer,
            bias_initializer=bias_initializer_layer,
            kernel_regularizer=tf.keras.regularizers.L1L2(l1=model_config["l1_lambda"], l2=model_config["l2_lambda"]),
            bias_regularizer=tf.keras.regularizers.L1L2(l1=model_config["l1_lambda"], l2=model_config["l2_lambda"]),
        )(x)
        if not model_config["activation"] == "selu":
            x = tf.keras.layers.BatchNormalization(axis=1)(x)
        x = activation_layer[0](**activation_layer[1])(x)
        if model_config["dropout"] > 0:
            if not model_config["activation"] == "selu":
                x = tf.keras.layers.Dropout(model_config["dropout"])(x)
            else:
                x = tf.keras.layers.AlphaDropout(model_config["dropout"])(x)
    if targets_train.shape[1] == 1:
        outputs = tf.keras.layers.Dense(
            1, kernel_initializer=tf.keras.initializers.GlorotUniform(), activation="sigmoid", name="output"
        )(x)
    else:
        outputs = tf.keras.layers.Dense(
            targets_train.shape[1],
            kernel_initializer=tf.keras.initializers.GlorotUniform(),
            activation="softmax",
            name="output",
        )(x)

    return tf.keras.Model(inputs=inputs, outputs=outputs, name="OPTIMA_MLP")


def update_model(
    model: Union[tf.keras.Model, tf.keras.models.Sequential],
    model_config: model_config_type,
    input_handler: Optional[OPTIMA.builtin.inputs.InputHandler] = None,
    inputs_train: Optional[np.ndarray] = None,
    targets_train: Optional[np.ndarray] = None,
) -> Union[tf.keras.Model, tf.keras.models.Sequential]:
    """Updates all updatable hyperparameters of a given pretrained `Keras` model to the values provided in the model-config.

    This function is specific to multilayer perceptrons for classification produced by the built-in ``build`` function.
    As such, only the corresponding model and hyperparameters are supported. To use a different type of `Keras` model,
    an ``update_model``-function needs to be defined in the run-config.

    With this function, the dropout rate as well as the strength of the L1 and L2 regularizers can be updated. Currently,
    changing them individually per layer has not yet been implemented.

    Note: the model needs to be compiled for the changes to take effect.

    Parameters
    ----------
    model : Union[tf.keras.Model, tf.keras.models.Sequential]
        `Keras` model whose hyperparameters should be updated.
    model_config : model_config_type
        Model-config containing the updated hyperparameters.
    input_handler : Optional[OPTIMA.builtin.inputs.InputHandler]
        Instance of the ``InputHandler``-class. While not needed for the built-in MLP, other models may need to know the
        inputs they are provided with, thus an ``update_model``-function in the run-config needs to be provided with the
        ``input_handler``. (Default value = None)
    inputs_train : Optional[np.ndarray]
        The input features for the training dataset. While not needed for the built-in MLP, other models may need to
        know the training inputs, thus an ``update_model``-function in the run-config needs to be provided with the
        ``inputs_train``. (Default value = None)
    targets_train : Optional[np.ndarray]
        The target labels for the training dataset. While not needed for the built-in MLP, other models may need to
        know the target labels, thus an ``update_model``-function in the run-config needs to be provided with the
        ``targets_train``. (Default value = None)

    Returns
    -------
    Union[tf.keras.Model, tf.keras.models.Sequential]
        `Keras` model with updated hyperparameters (but same training state, i.e. same weights and biases and same optimizer
        state)
    """
    for layer in model.layers:
        if isinstance(layer, tf.keras.layers.Dense) and layer.name != "output":
            # regularizers are stored in a list of "callable losses"; unfortunately there is no intended way to remove/modify them.
            # we therefore have to remove all previous losses (which currently only contain the regularizers; this may change
            # in the future and would then break this workaround)
            layer._clear_losses()  # clear eager losses (is this necessary?)
            layer._callable_losses = []  # clear callable losses to remove existing regularizers

            # update the regularizer attributes of the layer (which is needed for saving and restoring) and add the new losses
            for attribute in ["kernel_regularizer", "bias_regularizer"]:
                regularizer = tf.keras.regularizers.L1L2(l1=model_config["l1_lambda"], l2=model_config["l2_lambda"])
                setattr(layer, attribute, regularizer)

                # Add the regularization loss term,
                # https://github.com/tensorflow/tensorflow/blob/v2.2.2/tensorflow/python/keras/engine/base_layer.py#L578-L585
                variable = getattr(layer, attribute.split("_")[0])
                name_in_scope = variable.name[: variable.name.find(":")]
                layer._handle_weight_regularization(name_in_scope, variable, regularizer)

        elif isinstance(layer, tf.keras.layers.Dropout):
            # changing the rate attribute is sufficient to change the dropout rate
            layer.rate = model_config["dropout"]

    return model


def compile_model(
    model: Union[tf.keras.models.Sequential, tf.keras.Model],
    model_config: model_config_type,
    metrics: Optional[list] = None,
    weighted_metrics: Optional[list] = None,
    input_handler: Optional[OPTIMA.builtin.inputs.InputHandler] = None,
    inputs_train: Optional[np.ndarray] = None,
    targets_train: Optional[np.ndarray] = None,
    first_compile: bool = True,
) -> Union[tf.keras.models.Sequential, tf.keras.Model]:
    """Compiles a provided `Keras` model and updates the parameters of the optimizer if necessary.

    This allows to change the loss function and the hyperparameters of the optimizer without losing the training state of
    the provided model if desired.

    Currently, only the `Adam` optimizer is supported. Its tunable hyperparameters are the parameters ``alpha``,
    `beta_1`, `beta_2` and `epsilon` in the Adam update rule (see https://arxiv.org/abs/1412.6980v9) and are set via

    - ``'learning_rate'``: `alpha`
    - ``'Adam_beta_1'``: `beta_1`
    - ``'one_minus_Adam_beta_2'``: `1 - beta_2`
    - ``'Adam_epsilon'``: `epsilon`

    Supported loss functions, set using the hyperparameter ``'loss_function'``, are binary crossentropy loss
    (``'BinaryCrossentropy'``), categorical crossentropy loss (``'CategoricalCrossentropy'``), and Kullback–Leibler
    divergence loss (``'KLDivergence'``). For all available loss functions, the loss values can be weighted using class
    weights, controlled via hyperparameters of type  ``'loss_weight_class_N'`` with ``N`` corresponding to the N-th class.
    There must be either no loss class weights or as many weights defined as there are classes. This is not verified.

    Additionally, ``model_config['loss_function']`` can also contain a reference to a class that should be used for the
    loss function. Its constructor is provided with the dictionary containing all hyperparameters to allow
    hyperparameter-specific configuration.

    This function is specific to classification. For different tasks, a ``compile_model``-function needs to be defined
    in the run-config.

    :return:

    Parameters
    ----------
    model : Union[tf.keras.models.Sequential, tf.keras.Model]
        The `Keras` model to be compiled.
    model_config : model_config_type
        The model-config containing the values of the ``Adam`` optimizer's hyperparameters, the loss function and the value
        of the loss signal weight.
    metrics : Optional[list]
        List of `Keras` metrics to be given to the ``compile`` function. (Default value = None)
    weighted_metrics : Optional[list]
        List of weighted `Keras` metrics to be given to the ``compile`` function. (Default value = None)
    input_handler : Optional[OPTIMA.builtin.inputs.InputHandler]
        Instance of the ``InputHandler``-class. While not needed for the built-in MLP, other models may need to know the
        inputs they are provided with, thus a ``compile_model``-function in the run-config needs to be provided with the
        ``input_handler``. (Default value = None)
    inputs_train : Optional[np.ndarray]
        The input features for the training dataset. While not needed for the built-in MLP, other models may need to
        know the training inputs, thus a ``compile_model``-function in the run-config needs to be provided with the
        ``inputs_train``. (Default value = None)
    targets_train : Optional[np.ndarray]
        The target labels for the training dataset. While not needed for the built-in MLP, other models may need to
        know the target labels, thus a ``compile_model``-function in the run-config needs to be provided with the
        ``targets_train``. (Default value = None)
    first_compile : bool
        If ``True``, a new instance of the ``Adam`` optimizer is created. If ``False``, the parameters of the optimizer
        bound to the model are updated. (Default value = True)

    Returns
    -------
    Union[tf.keras.models.Sequential, tf.keras.Model]
        The compiled `Keras` model.
    """
    if metrics is None:
        metrics = []
    if weighted_metrics is None:
        weighted_metrics = []

    if first_compile:
        optimizer = tf.keras.optimizers.Adam(
            learning_rate=model_config["learning_rate"],
            beta_1=model_config["Adam_beta_1"],
            beta_2=1 - model_config["one_minus_Adam_beta_2"],
            epsilon=model_config["Adam_epsilon"],
        )
    else:
        # if it is a recompile, we would like to preserve the optimizer state (e.g. the running momentum) and only update the parameters
        optimizer = model.optimizer
        K.set_value(optimizer.lr, model_config["learning_rate"])
        optimizer.beta_1 = model_config["Adam_beta_1"]
        optimizer.beta_2 = 1 - model_config["one_minus_Adam_beta_2"]
        optimizer.epsilon = model_config["Adam_epsilon"]  # optimizer.epsilon is float, not a tensor

    # build the dict of class weights by selecting all keys of type "loss_weight_class_#"
    class_weights = {}
    for param, val in model_config.items():
        if "loss_weight_class" in param:
            class_weights[param[12:]] = val

    # get the loss function
    if model_config["loss_function"] == "BinaryCrossentropy":
        loss_function = OPTIMA.keras.tools.WeightedBinaryCrossentropy(class_weights=class_weights)
    elif model_config["loss_function"] == "CategoricalCrossentropy":
        loss_function = OPTIMA.keras.tools.WeightedCategoricalCrossentropy(class_weights=class_weights)
    elif model_config["loss_function"] == "KLDivergence":
        loss_function = OPTIMA.keras.tools.WeightedKLDivergence(class_weights=class_weights)
    else:
        loss_function = model_config["loss_function"](model_config)

    model.compile(optimizer=optimizer, loss=loss_function, metrics=metrics, weighted_metrics=weighted_metrics)

    return model


def export_builtin_keras_to_lwtnn(
    model: tf.keras.Model,
    output_shape: tuple,
    input_handler: OPTIMA.builtin.inputs.InputHandler,
    lwtnn_inputs_with_scalings: dict,
    output_dir: str,
) -> None:
    """Exports the Keras model generated with the built-in ``build``-function to the lightweight trained neural network format.

    For LWTNN, three inputs are necessary to generate the model file:

    - The model architecture, which is generated by calling ``model.to_json()``.
    - The model weights, which are exported by calling ``model.save_weights(...)``.
    - The input variables file containing the input variables with their linear scaling and the output nodes. The non-linear
      scaling of the inputs is encoded in the variable name and is expected to be correctly given in
      ``lwtnn_inputs_with_scalings``. The linear scaling is directly extracted from the model's ``Normalization``-layer.

    All three outputs are saved to the provided ``output_dir``.

    Parameters
    ----------
    model : tf.keras.Model
        The model to export to LWTNN.
    output_shape : tuple
        The shape of the output layer.
    input_handler : OPTIMA.builtin.inputs.InputHandler
        A reference to the input handler.
    lwtnn_inputs_with_scalings : dict
        The dictionary containing the input variable names with non-linear scaling.
    output_dir : str
        Path to the directory the output files should be saved to.
    """
    # output variables with scaling
    # first get the model's normalization layer
    scale, offset = None, None
    for layer in model.layers:
        if isinstance(layer, OPTIMA.keras.tools.NonLinearNormalization):
            scale = 1 / np.sqrt(
                layer.variance.numpy().flatten()
            )  # in LWTNN, the inputs are multiplied by the scale, i.e. we need to divide by the standard deviation
            offset = -layer.mean.numpy().flatten()

    if scale is None or offset is None:
        logging.error("Could not find the Normalization layer in the provided model, skipping the export to LWTNN...")
        return
    else:
        # we found the normalization layer, so we can do the export
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    # built the basic structure of the variables part of the lwtnn model
    vars_dict = {
        "input_sequences": [],
        "inputs": [{"name": "node_0", "variables": []}],
        "outputs": [{"labels": [f"out_{i}" for i in range(output_shape[0])], "name": "MyLWTNNOutput"}],
    }

    # add the input variables with scaling
    for i, var_with_scaling in enumerate(
        {var: lwtnn_inputs_with_scalings[var] for var in input_handler.get_vars()}.values()
    ):
        var_dict = {"name": var_with_scaling, "offset": float(offset[i]), "scale": float(scale[i])}
        vars_dict["inputs"][0]["variables"].append(var_dict)

    # save model architecture
    arch = model.to_json()
    with open(os.path.join(output_dir, "architecture.json"), "w") as arch_file:
        arch_file.write(arch)

    # now the model weights
    model.save_weights(os.path.join(output_dir, "weights.h5"))

    with open(os.path.join(output_dir, "variables.json"), "w") as inputs_file:
        json.dump(vars_dict, inputs_file, indent=4)
