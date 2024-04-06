import numpy as np

# the following arguments need to be provided in the run-config
__requires__ = [
    "perform_variable_opt",            # bool; whether to perform the initial hyperparameter optimization step with Optuna and subsequent input variable optimization
    "perform_main_hyperopt",           # bool; whether to perform the main hyperparameter optimization step with Optuna
    "perform_PBT_hyperopt",            # bool; whether to perform hyperparameter fine-tuning step with PBT
]

# the following arguments need to be provided in the run-config when not running in local-mode, i.e. when running the optimization on a cluster
__requires_cluster__ = [
    "path_to_setup_file",              # str; path to sourceable file that sets up the anaconda environment
]

# the following arguments are required by at least one built-in function, i.e. they need to be provided in the run-config if the corresponding built-in functionality is used
__requires_builtin__ = [
    (("get_inputs",), "inputs_file"),  # str; path to file containing the input data; needed for built-in get_inputs() function
]

# hyperparameter search space. The range of hyperparameters can be specified by:
#   - giving a fixed value --> no optimization
#   - giving a list --> only specified values will be tried
#   - giving a tuple (keyword, a, b, step), where keyword can be 'uniform' or 'log' (in which case the values will be
#     drawn from a uniform/logarithmic distribution between a and b) or 'normal' (in which case the values will be drawn
#     from a gaussian distribution with mean a and standard deviation b). step is optional and if given, the distribution
#     will be discretized with step size step. For 'uniform' and 'log', the datatype of a will decide the datatype of the
#     drawn value
# For the built-in MLP: tunable hyperparameters are: "num_layers", "units", "units_i" where i is the ith layer (WARNING:
# when specifying units for each layer, make sure to give at least as many entries as the maximum possible number of layers
# and set "optimize_units_per_layer" to True!), "activation", "kernel_initializer", "bias_initializer",
# "dropout", "batch_size", "learning_rate", "Adam_beta_1", "one_minus_Adam_beta_2", "Adam_epsilon" and "loss_weight_class_i"
# (with i between 0 and the number of classes - 1; WARNING: you need to specify either no or as many loss_weight_class
# entries as there are classes). For all hyperparameters (besides loss_weight_class_i) that are not specified here,
# default values given in OPTIMA.builtin.search_space.get_hp_defaults() will be used.
search_space = {
    "num_layers": ('uniform', 3, 6, 1),
    "units": ('log', 16, 128, 1),
    "activation": 'swish',
    "kernel_initializer": 'auto',
    "bias_initializer": 'auto',
    "l1_lambda": 0.,  # ('log', 1e-18, 1e-1),
    "l2_lambda": 0.,  # ('log', 1e-18, 1e-1),
    "dropout": ('uniform', 0.0, 0.2),
    "batch_size": ('uniform', 64., 512.),
    "learning_rate": ('log', 1e-5, 1e-2),
    "Adam_beta_1": ('uniform', 1e-4, 0.99),
    "one_minus_Adam_beta_2": ('log', 1e-5, 0.9999),
    "Adam_epsilon": ('log', 1e-10, 1.0),
    "loss_function": 'BinaryCrossentropy',
    # "loss_weight_class_0": 1.0,
    # "loss_weight_class_1": 1.0,
    # "loss_weight_class_2": 1.0,
}
optimize_units_per_layer = False  # for built-in MLP; should each layer be of the same size or should the size of each layer be optimized individually?

# output folder
output_name = "OPTIMA_defaults"  # suffix appended to output folder name (which by default also contains the algorithm used and the validation offset as C# when using event numbers for splitting)
output_path = "DNN_storage"  # this is where the output folder for the optimization will be created
use_exact_name = False  # omit the automatically created part of the output folder name?
produce_inputs_plots = True  # produce plots of the input variable before and after scaling

# train / val / test splitting
use_testing_dataset = True  # should the dataset be split into training / validation or training / validation / testing? (crossvalidation will also be performed with the same number of splits)
fixed_testing_dataset = True  # should the same testing dataset be used for all folds during crossvalidation or shuffled like the validation dataset? Only used if explicit_testing_dataset == True
use_eventNums_splitting = False  # should inputs be split randomly into training, validation (and test) or should the event numbers be used?
eventNums_splitting_offset_val = 0  # for training / validation split: split according to (event_number + offset_val) % N == 0
eventNums_splitting_offset_test = 1  # for trainVal / test split: split according to (event_number + offset_test) % N == 0; only used if use_testing_dataset == True
eventNums_splitting_N = 5  # controls the size of the training dataset
validation_fraction = 0.2  # only used when not specifying a custom splitting condition; fraction of events used for validation
test_fraction = 0.2  # only used when not specifying a custom splitting condition and requesting explicit testing dataset; fraction of events used for testing
max_num_events = np.inf  # limit the maximum number of events to use; can be np.inf to use all available input data
max_event_weight = np.inf  # maximum event weight (compared to average weight) before duplicating

# general settings for the optimization
model_type = 'Keras'  # the library used to build the model, possible values: 'Keras' and 'Lightning'
monitor_name = 'val_loss'  # metric that is used for the optimization, early stopping and the evaluation
monitor_op = 'min'  # operator corresponding to the metric to monitor
optimize_on_best_value = False  # should the highest value of the metric to monitor be used as target for the optimization (that may be an outlier) or the current value (that may have gotten worse due to overtraining)?
restore_on_best_checkpoint = False  # if True, any reloads will use the best model so far (based on metic value) instead of the last one
max_epochs = 200  # maximum number of epoch before terminating the training; this can be something very large because the Early Stopping and ASHA will take care of the termination
early_stopping_patience = 6  # number of consecutive epochs without improvement (of the metric to monitor) before terminating the training
overtraining_patience = 6  # number of consecutive epochs with overtraining detected (at least one overtraining condition is fulfilled) before terminating the training; only used when OT conditions are defined
random_seed = 42  # random seed to make optimization deterministic (within the limits of parallelization); set to None to disable

# settings for the evaluation and crossvalidation
fit_min_R_squared = 0.9  # min. R-squared of the fit; if less, the fit is rejected (and consequently the trial is ignored for the evaluation)
check_overtraining_with_fit = True  # for the evaluation using the fit, use the value of the fit function to decide if a checkpoint is overtrained or not; only used when OT conditions are defined
use_early_stopping_for_crossvalidation = False  # whether to use early stopping or a fixed number of epochs determined from the optimization for the trainings during crossvalidation; this also applies any training done during the variable optimization
use_OT_conditions_for_crossvalidation = False  # whether to use OT conditions for early stopping like during the optimization; this also applies any training done during the variable optimization
reuse_seed_for_crossvalidation = False  # if True, will provide the same seed to the trainable as during the optimization; if False, a new random seed will be drawn
fixed_seed_for_crossvalidation = False  # if True, will use the same seed for all folds; if False, a new seed is generated for each fold (only used if reuse_seed_for_crossvalidation is False)
evaluation_class_labels = ["Signal", "Background"]  # labels for each category: needs to contain as one entry per class; for binary classification (0 or 1), the first entry corresponds to the "1" label; for one-hot encoded targets, the order corresponds to the target labels (only used by the default 'evaluate'-function)

# settings for the hyperparameter optimization with Optuna; this affects both the main and the pre-optimization steps
num_samples_variableOpt = 1  # how many hyperparameter combinations to try during the initial hyperparameter optimization step with Optuna before doing the subsequent input variable optimization
num_samples_main = 1  # how many hyperparameter combinations to try for the main hyperparameter optimization step with Optuna
use_TPESampler = True  # use Optuna's Tree-structured Parzen Estimator algorithm or random sampling?
use_multivariate_TPE = False  # use the multivariate or independent version of the TPESampler
use_ASHAScheduler = True  # use Asynchronous HyperBand scheduler (ASHA) to prune trials or not?
ASHA_grace_period = 15  # grace period before ASHA starts terminating trails
ASHA_max_t = max_epochs  # end point of the reduction
ASHA_reduction_factor = 2  # which fraction of trails to terminate each time

# settings for the hyperparameter optimization with Population Based Training
num_samples_PBT = 4  # how large should the population be for PBT?
use_fit_results_for_PBT = True  # PBT cannot optimize all hyperparameters. If optuna was used as first step of the optimization, should PBT use the results from the fit or the highest metric value?
perturbation_interval = 6  # number of epochs to train between perturbations
burn_in_period = 6  # number of epochs to wait before first perturbation

# settings for the input variable selection
var_metric = 'loss'  # which metric should be used to check the DNN performance during variable optimization? possible values are 'loss' (which will use BinaryCrossentropy loss) and all native_metrics, weighted_native_metrics and custom_metrics.
var_metric_op = 'min'  # operator corresponding to the metric to monitor during variable optimization
variable_optimization_mode = 'hybrid'  # which algorithm to use to evaluate variable importance. Options are 'retrain' (for retraining new models with different input variables), 'shuffle' (for shuffling dropped input variable with fixed models), 'hybrid' (combines 'shuffle' and 'retrain') and 'custom' (for providing an own method)
acceptance_criterion = "improvement"  # criterion to decide if an iteration should be accepted. Possible values are: "threshold" (always accept unless relative worsening is larger than max_rel_change), "improvement" (accept if improvement compared to the best seen value), and "degradation" (accept unless more than 1 sigma worse than best seen value)
max_rel_change = 0.5  # threshold for how much the metric value is allowed to increase/decrease before stopping the variable optimization (relative difference!); positive values correspond to worse metric values; only used if acceptance_criterion is "threshold"
var_opt_patience = 3  # early-stopping like patience to stop the variable optimization once a certain number of iterations in a row were not accepted
choose_best_var_set = True  # if True: return the set of variables of the best iteration; if False: return the last accepted iteration
hybrid_revert_to_best_before_switch = True  # only used if variable_optimization_mode == 'hybrid'. If True: revert to the best iteration before switching to retrain phase; if False: revert to last accepted iteration
num_repeats = 5  # how often should each variable set be evaluated per iteration
num_repeats_hybrid_retrain = 1  # how often should each variable set be evaluated per iteration in the second phase of hybrid mode (retrain); not used if variable_optimization_mode != 'hybrid'
reevaluate_candidate_to_drop = True  # if True: instead of using the metric value after variable drop directly, an additional evaluation set is performed for the best variable set in each iteration to get an unbiased performance estimate
retrain_for_reevaluation = True  # if True: instead of using the original evaluation method used for each variable set, the re-evaluation for the baseline uses the retrain method
num_repeats_for_reevaluation = 2  # the number of times the re-evaluation of the best variable set should be done
use_median_for_averages = False  # if True: use the median and MAD to calculate averages and uncertainties across the k folds, otherwise use mean and standard deviation
use_fit_results_for_varOpt = True  # whether to use the hyperparameters from the best fit or highest metric value of the initial hyperoptimization step

# a list of references to a callback class (specific for the used ML framework, i.e. a subclass of keras.callbacks.Callback for Keras or lightning.pytorch.callbacks.Callback for Lightning) in the form (ClassName, {"kwarg1": kwarg1, ...}. They are only used during the model training.
callbacks = [
    # (tf.keras.callbacks.ReduceLROnPlateau, {"patience": 10, "factor": 0.2})
]

# list of references to a metric class (native to the used ML framework) in the form (name, (ClassName, {"kwarg1": kwarg1, ...})). Their values are calculated without applying event weights.
native_metrics = [
    # ('binary_accuracy', (tf.keras.metrics.BinaryAccuracy, {"threshold": 0.75}))
    # ('lightning_accuracy', (torchmetrics.classification.BinaryAccuracy, {"threshold": 0.5})),,
]

# list of references to a metric class (native to the used ML framework) in the form (name, (ClassName, {"kwarg1": kwarg1, ...})). Their values are calculated using the event weights.
weighted_native_metrics = [
    # ('weighted_binary_accuracy', (tf.keras.metrics.BinaryAccuracy, {"threshold": 0.75}))
]

# here custom metrics can be defined. These are functions that take as inputs the target and predicted labels and optionally sample weights,
# and return a number or boolean - they are calculated at the end of each epoch on both the training and validation datasets and can be used
# directly for the optimization and for Early Stopping and can be combined using "composite metrics" (see below).
# The syntax is [(name, callable), ...].
custom_metrics = [
    # ('bce_loss', OPTIMA.keras.tools.WeightedBinaryCrossentropy(class_weights={"class_0": 1.0}, only_numpy=True).calc_loss),
    # ('SoverSqrtB', OPTIMA.builtin.figures_of_merit.build_FoM(name='SoverSqrtB', exp_sig=20.002, exp_bkg=394.450, min_events_per_bin=10.)),
]

# here metrics that take as inputs the values of already existing metrics can be defined. They are evaluated after the custom_metrics
# and can therefore use them as inputs. They can be used for the optimization, for Early Stopping and to compare the performance of
# the DNN on training and validation data (to detect overtraining). The syntax is [(name, (metric_name1, metric_name2, ...), callable), ...]
# where callable needs to take the same number of positional arguments as the number of provided metric names and needs to return
# a number or a boolean.
composite_metrics = [
    # ('red_val_bce_loss', ('train_bce_loss', 'val_bce_loss'), lambda train_bce_loss, val_bce_loss: val_bce_loss + (val_bce_loss - train_bce_loss)),
]

# overtraining conditions are special composite metrics that should return 'True' when overtraining is present and 'False' otherwise.
# They are evaluated after the custom_metrics and the composite_metrics and can therefore use them as inputs. They are not added to
# the epoch's log and are not reported to ray. The syntax is the same as for composite metrics.
overtraining_conditions = [
    # ('bce_loss train / val', ('train_bce_loss', 'val_bce_loss'), lambda train_loss, val_loss: np.divide(train_loss, val_loss) < 0.99)
]

# examples for additional optional (and recommended) arguments
"""python
input_vars = ['jet1_pt', 'jet1_phi_recalibrated', 'jet1_eta']  # which input variables to give to the DNN. If not provided, will use all available input variables. When using variable optimization, these are the input variables for the initial optimization phase. For the remaining optimization, the optimized set of input variables will be used.
input_scaling = {
        "jet1_pt": ("log10", (1., 0.)),
        "jet1_eta": ("linear", (1., 0.)),
        "jet1_phi": ("linear", (1., 0.)),
}  # input scaling for each input variable
"""