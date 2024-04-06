import os
from typing import Union, Literal, Optional
from types import ModuleType

import numpy as np
import matplotlib.pylab as plt

# parameters of gaussians
mu_1 = np.array([-1, 0.5])
mu_2 = np.array([-1, -0.5])
mu_3 = np.array([1, 0])
covar_1 = np.array([[1, 0.], [0., 1.]])
covar_2 = np.array([[1, 0.], [0., 1.]])
covar_3 = np.array([[1, 0.], [0., 1.]])

def get_inputs(run_config: ModuleType, nevts: int, input_vars_list: list[str], *args, **kwargs):
    # get random state for reproducibility
    rng = np.random.RandomState(seed=random_seed)

    # procedurally draw events from three overlapping 2D Gaussians
    events_class_1_2d = rng.multivariate_normal(mu_1, covar_1, size=nevts // 3)
    events_class_2_2d = rng.multivariate_normal(mu_2, covar_2, size=nevts // 3)
    events_class_3_2d = rng.multivariate_normal(mu_3, covar_3, size=nevts // 3)

    # display drawn events
    fig, ax = plt.subplots(layout="constrained")
    ax.scatter(x=events_class_1_2d[:, 0], y=events_class_1_2d[:, 1], s=1, label="class 1")
    ax.scatter(x=events_class_2_2d[:, 0], y=events_class_2_2d[:, 1], s=1, label="class 2")
    ax.scatter(x=events_class_3_2d[:, 0], y=events_class_3_2d[:, 1], s=1, label="class 3")
    ax.set_aspect('equal')
    ax.set_xlim((-4, 4))
    ax.set_ylim((-4, 4))
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()
    os.makedirs(os.path.join(output_path, output_name, "inputs"), exist_ok=True)
    fig.savefig(os.path.join(output_path, output_name, "inputs", "scatter_2d.pdf"))
    plt.close(fig)

    # for each point, add a third random and fourth value, drawn from the same gaussian for all classes. This is an
    # intentionally useless variable for the classification and should be removed by the input variable selection.
    input_shape = (nevts // 3, 4)
    inputs_class_1 = np.empty(input_shape)
    inputs_class_2 = np.empty(input_shape)
    inputs_class_3 = np.empty(input_shape)
    inputs_class_1[:, [0, 1]] = events_class_1_2d
    inputs_class_1[:, 2] = rng.normal(0, 1, size=nevts // 3)
    inputs_class_1[:, 3] = rng.normal(0, 1, size=nevts // 3)
    inputs_class_2[:, [0, 1]] = events_class_2_2d
    inputs_class_2[:, 2] = rng.normal(0, 1, size=nevts // 3)
    inputs_class_2[:, 3] = rng.normal(0, 1, size=nevts // 3)
    inputs_class_3[:, [0, 1]] = events_class_3_2d
    inputs_class_3[:, 2] = rng.normal(0, 1, size=nevts // 3)
    inputs_class_3[:, 3] = rng.normal(0, 1, size=nevts // 3)

    # build the target labels
    targets_class_1 = np.empty((nevts // 3, 3))
    targets_class_2 = np.empty((nevts // 3, 3))
    targets_class_3 = np.empty((nevts // 3, 3))
    targets_class_1[:] = [1., 0., 0.]
    targets_class_2[:] = [0., 1., 0.]
    targets_class_3[:] = [0., 0., 1.]

    # combine and shuffle
    inputs = np.concatenate([inputs_class_1, inputs_class_2, inputs_class_3])
    targets = np.concatenate([targets_class_1, targets_class_2, targets_class_3])
    p = rng.permutation(len(inputs))
    inputs = inputs[p]
    targets = targets[p]

    # create event numbers and event weights
    weights = np.ones(len(inputs))
    normalized_weights = np.ones(len(inputs))
    event_nums = np.arange(len(inputs))

    # choose input variables
    var_indices_dict = {
        "x": 0,
        "x_copy": 0,
        "y": 1,
        "y_copy": 1,
        "random_1": 2,
        "random_2": 3,
    }
    var_indices = [var_indices_dict[var] for var in input_vars_list]
    inputs = inputs[:, var_indices]

    return inputs, targets, weights, normalized_weights, event_nums

perform_variable_opt = True
num_samples_variableOpt = 4
perform_main_hyperopt = True
num_samples_main = 4
perform_PBT_hyperopt = False

output_name = "testrun"
output_path = "OPTIMA_verification"
use_exact_name = True

use_testing_dataset = False
max_num_events = 2000
validation_fraction = 0.2
evaluation_class_labels = ["Class 1", "Class 2", "Class 3"]
input_vars = ['x', 'y', 'x_copy', 'random_1']

early_stopping_patience = 2
use_early_stopping_for_crossvalidation = True  # when dropping 2 of 4 variables, we are expecting the optimal number of epochs to be different
random_seed = 125

variable_optimization_mode = 'hybrid'
acceptance_criterion = "degradation"
hybrid_revert_to_best_before_switch = False
choose_best_var_set = False
var_opt_patience = 1
num_repeats_for_reevaluation = 4
use_fit_results_for_varOpt = False

search_space = {
    "num_layers": 3,
    "units": [4, 8],
    "activation": 'mish',
    "kernel_initializer": 'auto',
    "bias_initializer": 'auto',
    "l1_lambda": 0.,
    "l2_lambda": 0.,
    "dropout": 0.,
    "batch_size": 128,
    "learning_rate": 1e-3,
    "Adam_beta_1": 0.6,
    "one_minus_Adam_beta_2": 1e-3,
    "Adam_epsilon": 1e-8,
    "loss_function": 'CategoricalCrossentropy',
}

# TODO: lightning?