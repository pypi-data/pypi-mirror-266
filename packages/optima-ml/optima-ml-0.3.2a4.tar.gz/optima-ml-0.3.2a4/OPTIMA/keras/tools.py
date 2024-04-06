# -*- coding: utf-8 -*-
"""Toolbox of useful classes and functions specific to Keras models."""
from typing import Union, Optional, Callable, Any

import numpy as np

import tensorflow as tf
from tensorflow.keras import backend as K


@tf.keras.saving.register_keras_serializable(package="OPTIMA.core.keras.tools", name="NonLinearNormalization")
class NonLinearNormalization(tf.keras.layers.Normalization):
    r"""Extension of Keras's ``Normalization``-layer to allow manually defined non-linear transformations.

    Besides the usual linear transformation (scale and offset), this layer also allows applying a square-root or a log10
    transformation before the linear transformation. The inputs are consequently scaled according to

    $$
    \tilde{y} = a_1 \cdot f(a_2 \cdot y + b_2) + b_1,
    $$

    where \(f\) is either \(\sqrt{\bullet}\), \(\log_{10}(\bullet)\) or the identity, \(a_2\) and \(b_2\) are scaling
    and offset applied before the non-linear transformation and need to be provided, and \(a_1\) and \(b_1\) are the
    scaling and offset applied after the non-linear transformation and are calculated automatically to achieve a mean
    of zero and variance of one for the training dataset. \(f\), \(a_2\) and \(b_2\) can be different for each input
    variable.
    """

    def __init__(self, vars_in_use: list[str], scaling_dict: dict, *args: list[Any], **kwargs: dict[Any]) -> None:
        r"""Constructor of NonLinearNormalization.

        Parameters
        ----------
        vars_in_use : list[str]
            The list of variable names that is currently used.
        scaling_dict : dict
            The dictionary containing the non-linear scalings of the input variables. Each value is expected to be a tuple
            of type (transform_type, (scale, offset)) where transform_type can be "sqrt", "log10" or "linear" and scale and
            offset are floats that allow a linear scaling of the inputs before applying the non-linear transformation.
        *args : list[Any]
            Positional arguments for the ``Normalization`` layer.
        **kwargs : dict[Any]
            Keyword arguments for the ``Normalization`` layer.
        """
        super().__init__(*args, **kwargs)

        self.scaling_dict = scaling_dict
        self.vars_in_use = vars_in_use

        self.non_linear_ops = []
        self.non_linear_mask = []
        for i, var in enumerate(vars_in_use):
            scaling = scaling_dict.get(var)
            if scaling is not None and scaling[0] == "sqrt":
                self.non_linear_ops.append((tf.math.sqrt, scaling[1][0], scaling[1][1]))
            elif scaling is not None and scaling[0] == "log10":
                self.non_linear_ops.append(
                    (
                        lambda x: tf.math.log(x) / tf.math.log(tf.constant(10.0, dtype=x.dtype)),
                        scaling[1][0],
                        scaling[1][1],
                    )
                )
            elif scaling is not None and scaling[0] == "linear":
                self.non_linear_ops.append((tf.identity, scaling[1][0], scaling[1][1]))
            elif scaling is None:
                self.non_linear_ops.append((tf.identity, 1.0, 0.0))
            else:
                raise ValueError(f"Unknown scaling type {scaling}.")

            self.non_linear_mask.append(tf.one_hot(i, len(vars_in_use)))

    def non_linear_transform(self, inputs: np.ndarray) -> np.ndarray:
        r"""Applies the non-linear transformation to the inputs.

        This only performs the transformations specified in the provided scaling dictionary.

        Parameters
        ----------
        inputs : np.ndarray
            Numpy array of inputs to be scaled.

        Returns
        -------
        np.ndarray
            The numpy array containing the scaled inputs.
        """
        # TODO: make this more efficient by transforming all columns of the same op together and generalize the mask to multiple
        # TODO: columns
        # apply the nonlinear transformation to each column
        for i in range(inputs.shape[1]):
            # get the transformation, scale and offset
            transform, scale, offset = self.non_linear_ops[i]

            # column-wise assignment to tensors is not supported, we thus need to correct the columns one by one while
            # keeping the others unchanged --> generate zero-padded vector of the transformed inputs minus the original
            # inputs of each column which is added to the inputs tensor
            inputs_i_transformed = transform(scale * inputs[:, i] + offset) - inputs[:, i]
            inputs += tf.pad(tf.reshape(inputs_i_transformed, (-1, 1)), [[0, 0], [i, inputs.shape[1] - i - 1]])
        return inputs

    def adapt(self, data: np.ndarray, batch_size: Any = None, steps: Any = None) -> None:
        r"""_summary_.

        Parameters
        ----------
        data : np.ndarray
            The numpy array of input features that are used to adapt the normalization layer by first applying the
            non-linear transformations and then determining the mean and variance.
        batch_size : Any
            Argument of the ``tf.keras.layers.Normalization.adapt`` function. (Default value = None)
        steps : Any
            Argument of the ``tf.keras.layers.Normalization.adapt`` function. (Default value = None)
        """
        scaled_data = self.non_linear_transform(data)
        super().adapt(scaled_data, batch_size=batch_size, steps=steps)

    def call(self, data: np.ndarray) -> np.ndarray:
        r"""Transforms the provided input features by first applying a non-linear and a subsequent linear transformation.

        The non-linear transformation is performed by calling ``non_linear_transform`` and providing ``data``. The linear
        transformation is done by calling the super-function. Note that to use this function, the layer needs to be adapted
        first by calling the ``adapt``-function.

        Parameters
        ----------
        data : np.ndarray
            The numpy array of input features to transform.

        Returns
        -------
        np.ndarray
            The transformed input features.
        """
        scaled_data = self.non_linear_transform(data)
        return super().call(scaled_data)

    def get_config(self) -> dict:
        r"""Builds and returns the config for serialization.

        Returns
        -------
        dict
            A dictionary containing the config for serialization.
        """
        config = super().get_config()
        config.update({"vars_in_use": self.vars_in_use, "scaling_dict": self.scaling_dict})
        return config


@tf.keras.saving.register_keras_serializable(package="OPTIMA.core.keras.tools", name="SPLASHLayer")
class SPLASHLayer(tf.keras.layers.Layer):
    r"""_summary_.

    Returns
    -------
    _type_
        _description_
    """

    def __init__(self, b, a_plus_init=None, a_minus_init=None, **kwargs):
        r"""_summary_.

        Parameters
        ----------
        b : _type_
            _description_
        a_plus_init : _type_
            _description_ (Default value = [])
        a_minus_init : _type_
            _description_ (Default value = [])
        **kwargs : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        super(SPLASHLayer, self).__init__()

        if a_minus_init is None:
            a_minus_init = []
        if a_plus_init is None:
            a_plus_init = []

        self.b_input = b
        self.a_plus_init_input = a_plus_init
        self.a_minus_init_input = a_minus_init

        # set shapes and initial values
        self.b = K.constant(b, name="b")
        if a_plus_init != []:
            self.a_plus_init = K.constant(a_plus_init, name="a_plus_init")
        else:
            a_plus_init = 4 * [0.0]
            a_plus_init[0] = 1.0
            self.a_plus_init = K.constant(a_plus_init, name="a_plus_init")
        if a_minus_init != []:
            self.a_minus_init = K.constant(a_minus_init, name="a_minus_init")
        else:
            a_minus_init = 4 * [0.0]
            self.a_minus_init = K.constant(a_minus_init, name="a_minus_init")

    def build(self, input_shape):
        r"""_summary_.

        Parameters
        ----------
        input_shape : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        self.a_plus = tf.Variable(name="a_plus", initial_value=self.a_plus_init, trainable=True)
        self.a_minus = tf.Variable(name="a_minus", initial_value=self.a_minus_init, trainable=True)
        super(SPLASHLayer, self).build(input_shape)

    def call(self, x):
        r"""_summary_.

        Parameters
        ----------
        x : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        # input x is 2D-tensor: 1st dim. for batch size, second actual input values, e. g. [-2, -1, 0, 1, 2]
        # activation function is h(x) = sum_{i=1}^len(b)(a_plus_i * max(0, x - b_i)) + sum_{i=1}^len(b)(a_minus_i * max(0, -x - b_i))
        # to avoid summation with loops, first we add a dimension to x: K.expand_dims(x) -> returns [[-2], [-1], [0], [1], [2]]
        # substraction of b: K.expand_dims(x) - b -> gives [[-2-b_0, -2-b_1, -2-b_2, ...],
        #                                                         [-1-b_0, -1-b_1, -1-b_2, ...], ...]
        # max(0, x-b_i) can be done elementwise with K.maximum(0., K.expand_dims(x) - b) -> gives tensor of same shape as K.expand_dims(x) - b,
        # but all negative entries are replaced with 0.; pay attention to use float 0!
        # mulpilication with a_minus_i can be done as matrix multiplication: a_plus * K.maximum(0., K.expand_dims(x) - b) -> still
        # same shape as K.expand_dims(x) - b
        # summation is done with K.sum(..., axis=1)
        return K.sum(self.a_plus * K.relu(K.expand_dims(x) - self.b), axis=2) + K.sum(
            self.a_minus * K.relu(K.expand_dims(-x) - self.b), axis=2
        )
        # return K.relu(x)

    def compute_output_shape(self, input_shape):
        r"""_summary_.

        Parameters
        ----------
        input_shape : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        return input_shape

    def get_config(self):
        r"""_summary_.

        Returns
        -------
        _type_
            _description_
        """
        config = super().get_config()
        config.update(
            {
                "b": self.b_input,
                "a_plus_init": self.a_plus_init_input,
                "a_minus_init": self.a_minus_init_input,
            }
        )
        return config


@tf.keras.saving.register_keras_serializable(package="OPTIMA.core.keras.tools", name="Mish")
class Mish(tf.keras.layers.Layer):
    r"""Mish Activation Function.

    .. math::
       mish(x) = x * tanh(softplus(x)) = x * tanh(ln(1 + e^{x}))
    """

    def __init__(self, **kwargs):
        r"""_summary_.

        Parameters
        ----------
        **kwargs : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        super(Mish, self).__init__(**kwargs)
        self.supports_masking = True

    def call(self, inputs):
        r"""_summary_.

        Parameters
        ----------
        inputs : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        return inputs * K.tanh(K.softplus(inputs))

    def compute_output_shape(self, input_shape):
        r"""_summary_.

        Parameters
        ----------
        input_shape : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        return input_shape


@tf.keras.saving.register_keras_serializable(package="OPTIMA.core.keras.tools", name="CReLU")
class CReLU(tf.keras.layers.Layer):
    r"""_summary_.

    Returns
    -------
    _type_
        _description_
    """

    def __init__(self, axis=-1, **kwargs):
        r"""_summary_.

        Parameters
        ----------
        axis : _type_
            _description_ (Default value = -1)
        **kwargs : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        self.axis = axis
        super(CReLU, self).__init__(**kwargs)

    def build(self, input_shape):
        r"""_summary_.

        Parameters
        ----------
        input_shape : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        super(CReLU, self).build(input_shape)

    def call(self, x):
        r"""_summary_.

        Parameters
        ----------
        x : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        x = tf.nn.crelu(x, axis=self.axis)
        return x

    def compute_output_shape(self, input_shape):
        r"""_summary_.

        Parameters
        ----------
        input_shape : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        output_shape = list(input_shape)
        output_shape[-1] = output_shape[-1] * 2
        output_shape = tuple(output_shape)
        return output_shape

    def get_config(self, input_shape):
        r"""_summary_.

        Parameters
        ----------
        input_shape : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        config = {
            "axis": self.axis,
        }
        base_config = super(CReLU, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))


@tf.keras.saving.register_keras_serializable(package="OPTIMA.core.keras.tools", name="SignificanceMetric")
class SignificanceMetric(tf.keras.metrics.Metric):
    r"""_summary_.

    Returns
    -------
    _type_
        _description_
    """

    def __init__(
        self,
        exp_sig,
        exp_bkg,
        num_cuts,
        min_sig_events=1.0,
        min_bkg_events=1.0,
        max_significance=10.0,
        name=None,
        bin_optimize=False,
        min_events_per_bin=10,
        dtype=None,
        **kwargs,
    ):
        r"""_summary_.

        Parameters
        ----------
        exp_sig : _type_
            _description_
        exp_bkg : _type_
            _description_
        num_cuts : _type_
            _description_
        min_sig_events : _type_
            _description_ (Default value = 1.0)
        min_bkg_events : _type_
            _description_ (Default value = 1.0)
        max_significance : _type_
            _description_ (Default value = 10.0)
        name : _type_
            _description_ (Default value = None)
        bin_optimize : _type_
            _description_ (Default value = False)
        min_events_per_bin : _type_
            _description_ (Default value = 10)
        dtype : _type_
            _description_ (Default value = None)
        **kwargs : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        super(SignificanceMetric, self).__init__(name, dtype, **kwargs)

        # parameter necessary for reloading
        self.exp_sig = exp_sig
        self.exp_bkg = exp_bkg
        self.num_cuts = num_cuts

        # if after a cut, less than min_sig_events signal events are left, the number of signal events is set to 0
        self.min_sig_events = min_sig_events
        # if after a cut, less than min_bkg_events background events are left, the number of background events is set to min_bkg_events
        self.min_bkg_events = min_bkg_events

        self.max_significance = max_significance

        # bin optimize histogram before significance calculation; warning: only applies to significance returned from calc_significance()
        self.bin_optimize = bin_optimize
        self.min_events_per_bin = min_events_per_bin

        # convert parameters to tensors
        self.exp_sig_tensor = K.constant(exp_sig)
        self.exp_bkg_tensor = K.constant(exp_bkg)
        self.min_sig_events_tensor = K.constant(min_sig_events)
        self.min_bkg_events_tensor = K.constant(min_bkg_events)
        self.max_significance_tensor = K.constant(max_significance)
        self.zero = K.constant(0.0)

        self.cuts = np.linspace(0, 1, self.num_cuts, endpoint=False)
        self.cuts_tensor = K.constant(self.cuts)  # tensor containing the cuts
        self.sum_weights_after_cut_sig = K.variable(
            np.zeros(self.num_cuts)
        )  # tensor containing the sum over the signal weights after each cut
        self.sum_weights_after_cut_bkg = K.variable(
            np.zeros(self.num_cuts)
        )  # tensor containing the sum over the background weights after each cut
        self.total_sum_weights_sig = K.variable(0.0)  # total signal weight
        self.total_sum_weights_bkg = K.variable(1.0)  # total background weight

        self.significance = self.add_weight(name="SoB_significance", initializer="zeros")

    def calc_significance(self, y_true, y_pred, sample_weight=None):
        r"""_summary_.

        Parameters
        ----------
        y_true : _type_
            _description_
        y_pred : _type_
            _description_
        sample_weight : _type_
            _description_ (Default value = None)

        Returns
        -------
        _type_
            _description_
        """
        # reshape the input
        y_true = np.reshape(y_true, y_true.shape[0])
        y_pred = np.reshape(y_pred, y_pred.shape[0])

        # first get the DNN predictions for signal and background
        pred_sig = y_pred * y_true
        pred_bkg = y_pred * (1 - y_true)

        # sum up the signal and background weights and add them to the total weights
        total_sum_weights_sig = np.sum(sample_weight * y_true)
        total_sum_weights_bkg = np.sum(sample_weight * (1 - y_true))

        # get the sum over the signal and background weights for events with y_pred > cut, for each cut, and add it to
        # the sum of weights after cuts
        sum_weights_after_cut_sig = np.sum(
            np.expand_dims(sample_weight, axis=1)
            * np.maximum(0.0, np.sign(np.expand_dims(pred_sig, axis=1) - self.cuts)),
            axis=0,
        )
        sum_weights_after_cut_bkg = np.sum(
            np.expand_dims(sample_weight, axis=1)
            * np.maximum(0.0, np.sign(np.expand_dims(pred_bkg, axis=1) - self.cuts)),
            axis=0,
        )

        # get the expected number of events with y_pred > cut by scaling the sum of weights after cuts with the expected number of events
        N_sig_after_cut = self.exp_sig / (total_sum_weights_sig + 1e-10) * sum_weights_after_cut_sig
        N_bkg_after_cut = self.exp_bkg / (total_sum_weights_bkg + 1e-10) * sum_weights_after_cut_bkg

        # perform binning optimization or apply the minimum number of events limits; WARNING: binning optimization does
        # not do what was intended!!! TODO: don't forget!
        if self.bin_optimize:
            # go backwards through s and b arrays to create new list for each with potentially fewer bins, so that s+b
            # in each bin is at least min_events_per_bin
            s_bins = [
                0.0,
            ]
            b_bins = [
                0.0,
            ]
            for i in range(N_sig_after_cut.shape[0] - 1, -1, -1):
                if s_bins[-1] + b_bins[-1] > self.min_events_per_bin:
                    s_bins.append(N_sig_after_cut[i])
                    b_bins.append(N_bkg_after_cut[i])
                else:
                    s_bins[-1] += N_sig_after_cut[i]
                    b_bins[-1] += N_bkg_after_cut[i]
            s_bins.reverse()
            b_bins.reverse()
            N_sig_after_cut = np.array(s_bins)
            N_bkg_after_cut = np.array(b_bins)
        else:
            N_sig_after_cut = (
                np.maximum(0.0, np.sign(N_sig_after_cut - self.min_sig_events)) * N_sig_after_cut
            )  # factor is 1 if N_sig_after_cut > self.min_sig_events and 0 if N_sig_after_cut <= self.min_sig_events
            N_bkg_after_cut = np.maximum(self.min_bkg_events, N_bkg_after_cut)

        # calculate the significance for each cut
        significance_after_cut = N_sig_after_cut / np.sqrt(N_bkg_after_cut + 1e-10)

        return np.max(significance_after_cut)

    def update_state(self, y_true, y_pred, sample_weight=None):
        r"""_summary_.

        Parameters
        ----------
        y_true : _type_
            _description_
        y_pred : _type_
            _description_
        sample_weight : _type_
            _description_ (Default value = None)

        Returns
        -------
        _type_
            _description_
        """
        # first get the DNN predictions for signal and background
        pred_sig = y_pred * y_true
        pred_bkg = y_pred * (1 - y_true)

        # sum up the signal and background weights and add them to the total weights
        self.total_sum_weights_sig.assign_add(K.sum(sample_weight * y_true))
        self.total_sum_weights_bkg.assign_add(K.sum(sample_weight * (1 - y_true)))

        # get the sum over the signal and background weights for events with y_pred > cut, for each cut, and add it to
        # the sum of weights after cuts
        self.sum_weights_after_cut_sig.assign_add(
            K.sum(
                K.expand_dims(sample_weight) * K.maximum(self.zero, K.sign(K.expand_dims(pred_sig) - self.cuts_tensor)),
                axis=(0, 1),
            )
        )
        self.sum_weights_after_cut_bkg.assign_add(
            K.sum(
                K.expand_dims(sample_weight) * K.maximum(self.zero, K.sign(K.expand_dims(pred_bkg) - self.cuts_tensor)),
                axis=(0, 1),
            )
        )

        # get the expected number of events with y_pred > cut by scaling the sum of weights after cuts with the expected
        # number of events and apply the minimum number of events limits
        N_sig_after_cut = (
            self.exp_sig_tensor / (self.total_sum_weights_sig + K.epsilon()) * self.sum_weights_after_cut_sig
        )
        N_sig_after_cut = (
            K.maximum(self.zero, K.sign(N_sig_after_cut - self.min_sig_events_tensor)) * N_sig_after_cut
        )  # factor is 1 if N_sig_after_cut > self.min_sig_events and 0 if N_sig_after_cut <= self.min_sig_events
        N_bkg_after_cut = K.maximum(
            self.min_bkg_events_tensor,
            self.exp_bkg_tensor / (self.total_sum_weights_bkg + K.epsilon()) * self.sum_weights_after_cut_bkg,
        )

        # calculate the significance for each cut
        significance_after_cut = N_sig_after_cut / K.sqrt(N_bkg_after_cut + K.epsilon())

        # best significance is the maximum of significance_after_cut
        self.significance.assign(K.minimum(K.max(significance_after_cut), self.max_significance_tensor))

    def result(self):
        r"""_summary_.

        Returns
        -------
        _type_
            _description_
        """
        return self.significance

    def reset_state(self):
        r"""_summary_.

        Returns
        -------
        _type_
            _description_
        """
        self.cuts_tensor = K.constant(np.linspace(0, 1, self.num_cuts, endpoint=False))  # tensor containing the cuts
        self.sum_weights_after_cut_sig = K.variable(
            np.zeros(self.num_cuts)
        )  # tensor containing the sum over the signal weights after each cut
        self.sum_weights_after_cut_bkg = K.variable(
            np.zeros(self.num_cuts)
        )  # tensor containing the sum over the background weights after each cut
        self.total_sum_weights_sig = K.variable(0.0)  # total signal weight
        self.total_sum_weights_bkg = K.variable(1.0)  # total background weight

        self.significance.assign(0.0)

    def get_config(self):
        r"""_summary_.

        Returns
        -------
        _type_
            _description_
        """
        config = super().get_config()
        config.update(
            {
                "exp_sig": self.exp_sig,
                "exp_bkg": self.exp_bkg,
                "num_cuts": self.num_cuts,
                "min_sig_events": self.min_sig_events,
                "min_bkg_events": self.min_bkg_events,
                "max_significance": self.max_significance,
                "bin_optimize": self.bin_optimize,
                "min_events_per_bin": self.min_events_per_bin,
            }
        )
        return config


@tf.keras.saving.register_keras_serializable(package="OPTIMA.core.keras.tools", name="WeightedBinaryCrossentropy")
class WeightedBinaryCrossentropy(tf.keras.losses.BinaryCrossentropy):
    r"""_summary_.

    Returns
    -------
    _type_
        _description_
    """

    def __init__(self, *args, class_weights=None, only_numpy=False, **kwargs):
        r"""_summary_.

        Parameters
        ----------
        *args : _type_
            _description_
        class_weights : _type_
            _description_ (Default value = None)
        only_numpy : _type_
            _description_ (Default value = False)
        **kwargs : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        super(WeightedBinaryCrossentropy, self).__init__(*args, **kwargs)

        # get the class weights
        self.class_weights = class_weights
        if class_weights is None or class_weights == {}:
            self.signal_weight = 1.0
        else:
            self.signal_weight = class_weights.get("class_0")
            if self.signal_weight is None:
                self.signal_weight = 1.0
            if len(class_weights.keys()) > 1:
                print("Warning: more than 1 class weight was received, ignoring all but 'class_0'.")

        if not only_numpy:
            self.signal_weight_tensor = K.constant(self.signal_weight)

    def __call__(self, y_true, y_pred, sample_weight=None):
        r"""Intended to be used with Tensorflow.

        Parameters
        ----------
        y_true : _type_
            _description_
        y_pred : _type_
            _description_
        sample_weight : _type_
            _description_ (Default value = None)
        """
        # increase sample weights for signal samples by self.signal_weight
        if sample_weight is not None:
            y_true_reshaped = tf.reshape(y_true, tf.shape(sample_weight))
            sample_weight = (y_true_reshaped * self.signal_weight_tensor + (1 - y_true_reshaped)) * sample_weight
        else:
            sample_weight = y_true * self.signal_weight_tensor + (1 - y_true)

        return super(WeightedBinaryCrossentropy, self).__call__(y_true, y_pred, sample_weight=sample_weight)

    def calc_loss(self, y_true, y_pred, sample_weight=None):
        r"""Assumes inputs are numpy arrays.

        Parameters
        ----------
        y_true : _type_
            _description_
        y_pred : _type_
            _description_
        sample_weight : _type_
            _description_ (Default value = None)
        """
        # increase sample weights for signal samples by self.signal_weight
        y_pred = np.clip(y_pred, 1e-7, 1 - 1e-7)
        loss = -(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
        weighted_loss = ((y_true * self.signal_weight + (1 - y_true)) * loss).reshape(sample_weight.shape)

        if sample_weight is not None:
            return np.mean(sample_weight * weighted_loss, axis=0)
        else:
            return np.mean(weighted_loss, axis=0)

    def get_config(self):
        r"""_summary_.

        Returns
        -------
        _type_
            _description_
        """
        config = super(WeightedBinaryCrossentropy, self).get_config()
        config.update({"class_weights": self.class_weights})
        return config


@tf.keras.saving.register_keras_serializable(package="OPTIMA.core.keras.tools", name="WeightedCategoricalCrossentropy")
class WeightedCategoricalCrossentropy(tf.keras.losses.CategoricalCrossentropy):
    r"""_summary_.

    Returns
    -------
    _type_
        _description_
    """

    def __init__(self, *args, class_weights=None, only_numpy=False, **kwargs):
        r"""_summary_.

        Parameters
        ----------
        *args : _type_
            _description_
        class_weights : _type_
            _description_ (Default value = None)
        only_numpy : _type_
            _description_ (Default value = False)
        **kwargs : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        super(WeightedCategoricalCrossentropy, self).__init__(*args, **kwargs)

        # get the class weights
        self.class_weights_dict = class_weights
        if class_weights is None or class_weights == {}:
            self.class_weights = None
        else:
            assert (
                len(class_weights) >= 2
            ), f"At least two class weights need to be provided, only got {len(class_weights)}"
            class_indices = [int(key.split("_")[1]) for key in class_weights.keys()]
            class_indices.sort()
            self.class_weights = np.array([class_weights[f"class_{i}"] for i in class_indices])

        if not only_numpy and self.class_weights is not None:
            self.class_weights_tensor = K.constant(self.class_weights)

    def __call__(self, y_true, y_pred, sample_weight=None):
        r"""Intended to be used with Tensorflow.

        Parameters
        ----------
        y_true : _type_
            _description_
        y_pred : _type_
            _description_
        sample_weight : _type_
            _description_ (Default value = None)
        """
        if self.class_weights is not None:
            if sample_weight is not None:
                # multiply sample weight with class weight of the true class
                sample_weight = tf.reduce_sum(
                    tf.repeat(tf.reshape(sample_weight, (-1, 1)), repeats=y_true.shape[1], axis=1)
                    * self.class_weights_tensor
                    * y_true,
                    axis=1,
                )
            else:
                # can use the class weights of the true class directly as sample weights
                sample_weight = tf.reduce_sum(self.class_weights_tensor * y_true, axis=1)

        return super(WeightedCategoricalCrossentropy, self).__call__(y_true, y_pred, sample_weight=sample_weight)

    def calc_loss(self, y_true, y_pred, sample_weight=None):
        r"""Assumes inputs are numpy arrays.

        Parameters
        ----------
        y_true : _type_
            _description_
        y_pred : _type_
            _description_
        sample_weight : _type_
            _description_ (Default value = None)
        """
        # increase sample weights for signal samples by self.signal_weight
        y_pred = np.clip(y_pred, 1e-7, 1 - 1e-7)

        if self.class_weights is not None:
            weighted_loss = -np.sum(y_true * self.class_weights * np.log(y_pred), axis=1)
        else:
            weighted_loss = -np.sum(y_true * np.log(y_pred), axis=1)

        if sample_weight is not None:
            return np.mean(sample_weight * weighted_loss, axis=0)
        else:
            return np.mean(weighted_loss, axis=0)

    def get_config(self):
        r"""_summary_.

        Returns
        -------
        _type_
            _description_
        """
        config = super(WeightedCategoricalCrossentropy, self).get_config()
        config.update({"class_weights": self.class_weights_dict})
        return config


@tf.keras.saving.register_keras_serializable(package="OPTIMA.core.keras.tools", name="WeightedKLDivergence")
class WeightedKLDivergence(tf.keras.losses.KLDivergence):
    r"""_summary_.

    Returns
    -------
    _type_
        _description_
    """

    def __init__(self, *args, class_weights=None, only_numpy=False, **kwargs):
        r"""_summary_.

        Parameters
        ----------
        *args : _type_
            _description_
        class_weights : _type_
            _description_ (Default value = None)
        only_numpy : _type_
            _description_ (Default value = False)
        **kwargs : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        super(WeightedKLDivergence, self).__init__(*args, **kwargs)

        # get the class weights
        self.class_weights_dict = class_weights
        if class_weights is None or class_weights == {}:
            self.class_weights = None
        else:
            assert (
                len(class_weights) >= 2
            ), f"At least two class weights need to be provided, only got {len(class_weights)}"
            class_indices = [int(key.split("_")[1]) for key in class_weights.keys()]
            class_indices.sort()
            self.class_weights = np.array([class_weights[f"class_{i}"] for i in class_indices])

        if not only_numpy and self.class_weights is not None:
            self.class_weights_tensor = K.constant(self.class_weights)

    def __call__(self, y_true, y_pred, sample_weight=None):
        r"""Intended to be used with Tensorflow.

        Parameters
        ----------
        y_true : _type_
            _description_
        y_pred : _type_
            _description_
        sample_weight : _type_
            _description_ (Default value = None)
        """
        if self.class_weights is not None:
            if sample_weight is not None:
                # multiply sample weight with class weight of the true class
                batch_size = y_true.shape[0]
                sample_weight = tf.reduce_sum(
                    tf.repeat(tf.reshape(sample_weight, (batch_size, 1)), repeats=y_true.shape[1], axis=1)
                    * self.class_weights_tensor
                    * y_true,
                    axis=1,
                )
            else:
                # can use the class weights of the true class directly as sample weights
                sample_weight = tf.reduce_sum(self.class_weights_tensor * y_true, axis=1)
        return super(WeightedKLDivergence, self).__call__(y_true, y_pred, sample_weight=sample_weight)

    def calc_loss(self, y_true, y_pred, sample_weight=None):
        r"""Assumes inputs are numpy arrays.

        Parameters
        ----------
        y_true : _type_
            _description_
        y_pred : _type_
            _description_
        sample_weight : _type_
            _description_ (Default value = None)
        """
        # increase sample weights for signal samples by self.signal_weight
        y_pred = np.clip(y_pred, 1e-7, 1.0)
        weighted_loss = np.sum(y_true * self.class_weights * np.log(np.clip(y_true, 1e-7, 1.0) / y_pred), axis=1)

        if sample_weight is not None:
            return np.mean(sample_weight * weighted_loss, axis=0)
        else:
            return np.mean(weighted_loss, axis=0)

    def get_config(self):
        r"""_summary_.

        Returns
        -------
        _type_
            _description_
        """
        config = super(WeightedKLDivergence, self).get_config()
        config.update({"class_weights": self.class_weights_dict})
        return config


class SignalStrengthUncertaintyLoss(tf.keras.losses.Loss):
    r"""A differentiable approximation of the uncertainty of the signal strength parameter for uncertainty aware training.

    For each value in the neural network predictions in a batch, the bin assignment to a 1D output histogram is
    determined. To allow differentiation, a custom gradient is applied corresponding to the gradient of an approximated
    histogram where each bin is replaced with a Gaussian of the same height and a standard deviation of half the bin
    width. This bin assignment together with the target labels, the sample weights and the nominal fit parameters (signal
    strength and nuisance parameters) is given to a callable provided to the constructor which is expected to return the
    expected negative log-likelihood. This allows a flexible definition of the likelihood function including an
    arbitrary number of nuisance parameters and variations. From this, an approximated uncertainty of the signal strength
    is determined via the Fisher information. See https://doi.org/10.1007/s41781-020-00049-5 for more information.
    """

    def __init__(
        self,
        likelihood_function: Callable,
        nominal_fit_params: list[float],
        N_bins: int = 40,
        hist_limits: Union[tuple[float], str] = (0.0, 1.0),
        **kwargs: Any,
    ) -> None:
        r"""Constructor of ``SignalStrengthUncertaintyLoss``.

        Parameters
        ----------
        likelihood_function : Callable
            Callable that is expected to take a tensor of target labels, a tensor containing a one-hot-encoded vector
            for each value in the neural network prediction corresponding to the bin the value corresponds to, a tensor
            of nominal fit parameters as well as a tensor of sample weights. It is expected to return the (differentiable!)
            expected negative log-likelihood.
        nominal_fit_params : list[float]
            A list specifying the nominal values of the signal strength and all nuisance parameters. A tensor-version of
            this input will be given to ``likelihood_function`` to be able to calculate the gradient of the likelihood
            with respect to the fit parameters. The first entry in the list is expected to correspond to the signal
            strength.
        N_bins : int
            The number of bins in the 1D output histogram. (Default value = 40)
        hist_limits : Union[tuple[float], str]
            Either the range of the histogram (when a tuple is provided) or enables adaptive histogram range (if
            ``'adaptive'`` is given. (Default value = (0.0, 1.0))
        **kwargs : Any
            Additional keyword arguments for the parent Loss class.
        """
        super().__init__(**kwargs)

        # status parameters for reloading
        self.N_bins_float = N_bins
        self.hist_limits = hist_limits
        self.nominal_fit_params = nominal_fit_params

        # function to calculate the expected negative log-likelihood
        self.likelihood_function = likelihood_function

        # tensor of signal strength and nuisance parameters
        self.fit_params = tf.convert_to_tensor(nominal_fit_params)

        # histogram parameters
        self.N_bins = tf.constant(N_bins)
        if hist_limits != "adaptive":
            # make unit histogram bins for one the fly scaling
            self.hist_min = tf.constant(hist_limits[0], dtype=tf.float32)
            self.hist_max = tf.constant(hist_limits[1], dtype=tf.float32)
            bin_edges = tf.linspace(
                hist_limits[0], hist_limits[1] - (hist_limits[1] - hist_limits[0]) / N_bins, N_bins
            )  # we need to exclude the right edge of the final bin
            self.bin_centers = bin_edges + (hist_limits[1] - hist_limits[0]) / (2 * N_bins)
        else:
            bin_edges = tf.linspace(
                0.0, 1.0 - 1.0 / N_bins, N_bins
            )  # we need to exclude the right edge of the final bin
            self.bin_centers = bin_edges + 1.0 / (2 * N_bins)

    def gaussian_gradients_for_bins(
        self,
        v: Union[tf.Tensor, tf.TensorSpec],
        max_x: Union[tf.Tensor, tf.TensorSpec],
        min_x: Union[tf.Tensor, tf.TensorSpec],
        x_shifted: Union[tf.Tensor, tf.TensorSpec],
    ) -> Union[tf.Tensor, tf.TensorSpec]:
        r"""Returns the JVP of the custom gradient corresponding to the approximated histogram.

        The approximation of the histogram returned by ``bin_with_gaussian_gradients`` is obtained by replacing each bin
        with a Gaussian of the same height and a standard deviation of half the bin width. The product of the Jacobian
        of this approximated histogram with respect to the inputs and an upstream vector ``v``, giving the
        Jacobian-Vector-product, is returned.

        Since the histogram to be approximated is a one-hot vector of ``self.N_bins`` bins for each entry in the input
        tensor ``x`` corresponding to the bin this value should be sorted into, i.e. a tensor with an additional dimension
        compared to ``x``, approximated histogram is given by the functional form (with \(\vec{b}\) the bin centers,
        \(w\) the bin width, \(N\) the number of bins, \(x_\mathrm{max}\) the rightmost bin edge and \(x_\mathrm{min}\)
        the leftmost bin edge):

        $$
        \begin{align}
        h(x)_{ijk} &= \exp \left( -\frac{(x_{ij} - b_k)^{2}}{2(w/2)^2)} \right) \\
        &= \exp \left( -2 \left( \frac{x_{ij} - b_k}{w} \right)^{2} \right) \\
        &= \exp \left( -2N^{2} \left( \frac{x_{ij} - b_k}{x_{\mathrm{max}} - x_{\mathrm{min}}} \right)^2 \right)
        \end{align}
        $$

        We now need the gradient of this approximation with respect to \(x\). Instead of directly returning the Jacobian,
        Tensorflow expects us to return the `Vector-Jacobian-product`: for function \(f: \mathbb{R}^n \rightarrow \mathbb{R}^m\),
        the Jacobian of \(f\) evaluated at \(x\) in \(\mathbb{R}^n\), \(J(x)\), can be thought of as a linear map
        \(J(x): \mathbb{R}^n \rightarrow \mathbb{R}^m\) and is usually represented as a matrix \(J(x)\) in
        \(\mathbb{R}^{m \times n}\). The `Vector-Jacobian-product` is \(\mathrm{VJP}(x, v) = v^T \cdot J(x)\) with \(x\) in
        \(\mathbb{R}^n\) and \(v\) in \(\mathbb{R}^m\), i.e. the Jacobian \(J(x)\) is multiplied with an arbitrary tensor
        of the same shape as the output of \(f\). For more details, see
        https://jax.readthedocs.io/en/latest/notebooks/autodiff_cookbook.html

        Since here, it is:

        $$
        h: \mathbb{R}^{n_\mathrm{batch} \times n_\mathrm{outputs}} \rightarrow
            \mathbb{R}^{n_\mathrm{batch} \times n_\mathrm{outputs} \times N},
        $$

        the Jacobian is also

        $$
        J(x): \mathbb{R}^{n_\mathrm{batch} \times n_\mathrm{outputs}} \rightarrow
            \mathbb{R}^{n_\mathrm{batch} \times n_\mathrm{outputs} \times N},
        $$

        and thus is represented as a tensor in \(\mathbb{R}^{n_\mathrm{batch} \times n_\mathrm{outputs} \times N
        \times n_\mathrm{batch} \times n_\mathrm{outputs}}\). This makes sense when remembering that for every
        entry in \(h(x)\), the partial derivatives with respect to every component in \(x\) need to be calculated. However,
        since each entry in \(h(x)\) only depends on a single component in \(x\) ( \(h(x)_{ijk}\) is determined by \(x_{ij}\)),
        we don't need to calculate the 4th and 5th dimension of \(J(x)\) since all but one entry will be zero anyway,
        i.e.

        $$
        \begin{align}
        &\hspace{0.1cm} J(x)_{ijklm} \neq 0 \,\,\, \text{only for} \,\,\, i = l \,\,\, \text{and} \,\,\, j = m \\
        &\Rightarrow J(x)_{ijklm} =: \tilde{J}(x)_{ijk} \delta_{il} \delta_{jm}
        \end{align}
        $$

        Instead, we only calculate

        $$
        \tilde{J}(x)_{ijk} = \frac{\mathrm{d} h(x)_{ijk}}{\mathrm{d} x_{ij}},
        $$

        resulting in an \( (n_\mathrm{batch} \times n_\mathrm{outputs} \times N) \) matrix, i.e. the same shape as \(h(x)\):

        $$
        \begin{align}
        \left(\frac{\partial h(x)}{\partial x} \right)_{ijk} &= \frac{\mathrm{d}}{\mathrm{d} x_{ij}} \left[
        \exp \left( -2 N^2 \left( \frac{x_{ij} - b_k}{x_\mathrm{max} - x_\mathrm{min}} \right)^2 \right) \right] \\
        &= h(x)_{ijk} \cdot \frac{\mathrm{d}}{\mathrm{d} x_{ij}} \left[ -2 N^2 \frac{(x_{ij} - b_k)^2}{(x_\mathrm{max}
        - x_\mathrm{min})^2} \right] \\
        &= -\frac{4 N^2}{(x_\mathrm{max} - x_\mathrm{min})^2} \cdot (x_{ij} - b_k) \cdot h(x)_{ijk}
        \end{align}
        $$

        Finally, we need to handle the multiplication with the tensor \(v\) in \(\mathbb{R}^{n_\mathrm{batch} \times
        n_\mathrm{outputs} \times N}\). From looking at the shapes of \(J(x)\) ( \( (n_\mathrm{batch} \times
        n_\mathrm{outputs} \times N \times n_\mathrm{batch} \times n_\mathrm{outputs}) \) ) and of \(v\)
        ( \( (n_\mathrm{batch} \times n_\mathrm{outputs} \times N) \) ) we can deduct that the output should be a matrix
        of shape \( (n_\mathrm{batch} \times n_\mathrm{outputs}) \). In component notation we see that:

        $$
        \mathrm{VJP}(x, v)_{lm} = \left( v^T \cdot J(x) \right)_{lm} = \sum_{ijk} v_{ijk} \, J(x)_{ijklm}
        $$

        but as we have seen before, \(J(x)_{ijklm}\) is only different from zero for \(i = l\) and \(j = m\). Thus,
        \(\mathrm{VJP}(x, v)_{lm}\) simplifies to:

        $$
        \begin{align}
        \mathrm{VJP}(x, v)_{lm} &= \sum_{k} v_{lmk} \, J(x)_{lmklm} \\
        &= \sum_k v_{lmk} \, \tilde{J}(x)_{lmk} \\
        &= \sum_k v_{lmk} \, \frac{\mathrm{d} h(x)_{lmk}}{\mathrm{d} x_{lm}},
        \end{align}
        $$

        the second part of which we have already calculated.

        Parameters
        ----------
        v : Union[tf.Tensor, tf.TensorSpec]
            The upstream vector for the Jacobian-Vector-product.
        max_x : Union[tf.Tensor, tf.TensorSpec]
            The right edge of the rightmost bin.
        min_x : Union[tf.Tensor, tf.TensorSpec]
            The left edge of the leftmost bin.
        x_shifted : Union[tf.Tensor, tf.TensorSpec]
            The input values shifted by the bin centers. Compared to the original input tensor, this must contain an
            additional axis (axis 0) of the same length as the number of bins. Each entry in dimension 0 corresponds to
            the input tensor shifted by the corresponding bin center.

        Returns
        -------
        Union[tf.Tensor, tf.TensorSpec]
            The Jacobian-Vector-product for the Jacobian of the approximated histogram with respect to the inputs
            and the provided upstream vector `v`.
        """
        # get the gaussian approximation of the histogram: exp(-2*(num_bins * (x - bin_centers) / (hist_max - hist_min))^2)
        gauss_approx = tf.exp(-2 * tf.square(tf.cast(self.N_bins, tf.float32) / (max_x - min_x) * x_shifted))

        # now get the derivative of gauss_approx with respect to x
        grad = (
            -4 * tf.cast(tf.square(self.N_bins), dtype=tf.float32) / tf.square(max_x - min_x) * x_shifted
        ) * gauss_approx

        # finally, multiply with v to get the JVP
        return tf.reduce_sum(v * grad, axis=2)

    @tf.custom_gradient
    def bin_with_gaussian_gradients(
        self, x: Union[tf.Tensor, tf.TensorSpec]
    ) -> tuple[Union[tf.Tensor, tf.TensorSpec], Callable]:
        r"""Returns a one-hot-encoded vector for each value in the input tensor corresponding to the bin the value corresponds to.

        This is done by repeating the input ``self.N_bins`` times along a new dimension, shifting by the bin centers,
        and finding the entry that is closest to zero. This effectively finds the bin center that is closest to the input
        value and thus corresponds to the bin this value is added to. This is then one-hot encoded.

        Depending on the value of ``self.hist_limits``, the range of the histogram is either fixed (if fixed values were
        provided) or determined from the input tensor (if ``self.hist_limits`` is ``'adaptive'``).

        The input tensor is expected to be of shape ``(n_batch, n_outputs)``, the shape of the return value will subsequently
        be ``(n_batch, n_outputs, n_bins)``.

        To allow differentiation, a custom gradient is returned corresponding to the gradient of an approximated histogram
        where each bin is replaced with a Gaussian of the same height and a standard deviation of half the bin width.

        Example
        -------
        For an input tensor ``[[0.1], [0.5], [0.9]]`` and a histogram with 5 bins between ``0`` and ``1``, the return
        value will be the tensor ``[[[1, 0, 0, 0, 0,]], [[0, 0, 1, 0, 0,]], [[0, 0, 0, 0, 1]]]``.

        Parameters
        ----------
        x : Union[tf.Tensor, tf.TensorSpec]
            The input tensor whose values should be assigned to bins of a histogram.

        Returns
        -------
        tuple[Union[tf.Tensor, tf.TensorSpec], Callable]
            A tensor with one additional dimension compared to ``x`` containing a one-hot-encoded vector denoting the
            histogram bin each value of the input tensor ``x`` belongs to.
        """
        # adaptively set the histogram ranges is desired
        if self.hist_limits == "adaptive":
            max_x = tf.math.reduce_max(x)
            min_x = tf.math.reduce_min(x)
            bin_centers = (max_x - min_x) * self.bin_centers + min_x
        else:
            max_x = self.hist_max
            min_x = self.hist_min
            bin_centers = self.bin_centers

        # repeat the bin centers to get the correct shape for the substraction from the input values
        if x.shape[0] is not None:
            bin_centers_repeated = tf.repeat(
                tf.repeat(tf.expand_dims(tf.expand_dims(bin_centers, axis=0), axis=0), x.shape[1], axis=1),
                x.shape[0],
                axis=0,
            )
        else:
            bin_centers_repeated = tf.repeat(
                tf.expand_dims(tf.expand_dims(bin_centers, axis=0), axis=0), x.shape[1], axis=1
            )

        # substract the bin centers from the input values
        x_shifted = tf.repeat(tf.expand_dims(x, axis=-1), self.N_bins, axis=-1) - bin_centers_repeated

        def grad(v: Union[tf.Tensor, tf.TensorSpec]) -> Union[tf.Tensor, tf.TensorSpec]:
            r"""Returns the JVP of the custom gradient calculated by _gaussian_gradients_for_bins.

            Parameters
            ----------
            v : Union[tf.Tensor, tf.TensorSpec]
                The upstream vector for the Jacobian-Vector-product.

            Returns
            -------
            Union[tf.Tensor, tf.TensorSpec]
                The Jacobian-Vector-product for the Jacobian of the approximated histogram with respect to the inputs
                and the provided upstream vector `v`.
            """
            return self.gaussian_gradients_for_bins(v, max_x, min_x, x_shifted)

        # find the index corresponding to the lowest absolute value, i.e. to the bin center closest to the input value
        indices_min_dist = tf.argmin(tf.abs(x_shifted), axis=2)

        # get a one-hot encoded vector of the found index for each input value
        bin_counts = tf.one_hot(indices_min_dist, self.N_bins)
        return bin_counts, grad

    def __call__(self, y_true: tf.Tensor, y_pred: tf.Tensor, sample_weight: Optional[tf.Tensor] = None) -> tf.Tensor:
        r"""Calculate a differentiable approximation of the uncertainty of the signal strength for the current batch.

        This function calls ``bin_with_gaussian_gradients()`` to determine which bin of the 1D output histogram each
        value of the neural network's predictions correspond to (in an approximately differentiable manner) an gives the
        return value together with the target labels, the nominal fit parameter values and the sample weights to the
        provided ``likelihood_function``. The uncertainty of the signal strength corresponds to the 00 element of the
        inverse of the Fisher information of the returned expected negative log-likelihood, which takes into account
        all nuisance parameters used to calculate the likelihood.

        Parameters
        ----------
        y_true : tf.Tensor
            The tensor of target labels.
        y_pred : tf.Tensor
            The tensor of neural network predictions.
        sample_weight : Optional[tf.Tensor]
            The tensor of sample weights. (Default value = None)

        Returns
        -------
        tf.Tensor
            A differentiable approximation of the uncertainty of the signal strength for the current batch.
        """
        with tf.GradientTape() as tape_1:
            with tf.GradientTape() as tape_2:
                tape_1.watch(self.fit_params)
                tape_2.watch(self.fit_params)

                hist_pred = self.bin_with_gaussian_gradients(y_pred)
                neg_log_likelihood = self.likelihood_function(
                    y_true, hist_pred, self.fit_params, sample_weight=sample_weight
                )

            g = tape_2.gradient(neg_log_likelihood, self.fit_params)
        unc_mu = tf.linalg.inv(tape_1.jacobian(g, self.fit_params))[0, 0]
        return unc_mu

    def get_config(self):
        r"""_summary_.

        Returns
        -------
        _type_
            _description_
        """
        config = super().get_config()
        config.update(
            {
                "likelihood_function": self.likelihood_function,
                "nominal_fit_params": self.nominal_fit_params,
                "N_bins": self.N_bins_float,
                "hist_limits": self.hist_limits,
            }
        )
        return config

    @classmethod
    def from_config(cls, config):
        r"""_summary_.

        Parameters
        ----------
        config : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        return cls(**config)
