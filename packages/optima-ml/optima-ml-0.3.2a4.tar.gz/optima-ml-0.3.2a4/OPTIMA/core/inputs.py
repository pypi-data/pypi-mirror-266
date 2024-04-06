# -*- coding: utf-8 -*-
"""A module that provides functionality to handle the training inputs."""
from types import ModuleType
from typing import Optional, Union

import itertools
import os
from functools import partial

import numpy as np

import ray

import OPTIMA.builtin.inputs


train_val_splitting_type = tuple[Union[ray.ObjectRef, list[ray.ObjectRef]], Union[ray.ObjectRef, list[ray.ObjectRef]]]
train_val_test_splitting_type = tuple[
    Union[ray.ObjectRef, list[ray.ObjectRef]],
    Union[ray.ObjectRef, list[ray.ObjectRef]],
    Union[ray.ObjectRef, list[ray.ObjectRef]],
]


def _event_nums_splitting_cond_kfold(
    event_nums: np.ndarray,
    run_config: ModuleType,
    split: str = "val",
    use_testing_set: bool = True,
    fixed_testing_set: bool = True,
) -> list[np.ndarray]:
    """Does the k-fold event splitting based on the array of event numbers.

    The following cases are distinguished:

        - ``use_testing_set`` is ``False``: only a training/validation split is to be done, thus the only allowed
          value of ``split`` is ``'val'``. The returned array is calculated using the condition:
          ``(event_nums - i + run_config.eventNums_splitting_offset_val) % run_config.eventNums_splitting_N == 0``,
          where ``i`` is varied between ``0`` and ``run_config.eventNums_splitting_N - 1``. This results in
          ``run_config.eventNums_splitting_N`` different folds.
        - ``use_testing_set`` is ``True``:

            - ``fixed_testing_set`` is ``True``: the same testing dataset is to be used for all folds. The conditions are:

                - ``split == 'test'``: ``(event_nums + run_config.eventNums_splitting_offset_test) % run_config.eventNums_splitting_N == 0``
                - ``split == 'val'``: ``(event_nums - i + run_config.eventNums_splitting_offset_val) % run_config.eventNums_splitting_N == 0``,
                  where ``i`` is varied between ``0`` and ``run_config.eventNums_splitting_N - 1``. The iteration
                  ``i == (run_config.eventNums_splitting_offset_val - run_config.eventNums_splitting_offset_test) % run_config.eventNums_splitting_N``
                  is skipped to ensure that the validation and testing datasets are always different.
              This results in ``run_config.eventNums_splitting_N - 1`` different folds. Each event is either always
              part of the testing dataset or exactly once part of the validation dataset and
              ``run_config.eventNums_splitting_N - 2`` times part of the training dataset.
            - if ``fixed_testing_set`` is ``False``: the subset used as the testing dataset is shifted in the same
              way as the validation dataset, resulting in a different testing dataset for every fold. The conditions are

                - ``split == 'test'``: ``(event_nums - i + run_config.eventNums_splitting_offset_test) % run_config.eventNums_splitting_N == 0``
                -`` split == 'val'``: ``(event_nums - i + run_config.eventNums_splitting_offset_val) % run_config.eventNums_splitting_N == 0``
          In both cases, ``i`` is varied between ``0`` and ``run_config.eventNums_splitting_N - 1``, resulting in
          ``run_config.eventNums_splitting_N`` different folds. Each event is exactly once part of the testing dataset,
          exactly once part of the validation dataset and ``run_config.eventNums_splitting_N - 2`` times part of the
          training dataset.

    The return value is a list of boolean arrays of the same shape as ``event_nums``. Each list entry corresponds to a
    fold.

    Parameters
    ----------
    event_nums : np.ndarray
        1D array of integers giving numbers to each event.
    run_config : ModuleType
        Reference to the imported run-config file.
    split : str
        Specifies if this is the training / validation or the training+validation / testing split. Possible values
        are ``'val'`` or ``'test'``. (Default value = 'val')
    use_testing_set : bool
        Specifies if a training / validation or a training / validation / testing split is to be done. (Default value = True)
    fixed_testing_set : bool
        Specifies if the same testing dataset should be used for all folds or if it should be varied like the
        validation dataset. (Default value = True)

    Returns
    -------
    list[np.ndarray]
        List of boolean arrays, ``True`` where ``event_nums`` fulfills a condition.
    """
    condition_list = []

    if use_testing_set and fixed_testing_set:
        if split == "val":
            for i in range(run_config.eventNums_splitting_N):
                # skip if validation set == test set, i.e. (EventNumber - i + val) % N == (EventNumber + test) % N
                #  <==> (-i + val) % N == test % N
                if (
                    use_testing_set
                    and (run_config.eventNums_splitting_offset_val - i) % run_config.eventNums_splitting_N
                    == run_config.eventNums_splitting_offset_test % run_config.eventNums_splitting_N
                ):
                    continue
                condition_list.append(
                    ((event_nums - i) + run_config.eventNums_splitting_offset_val) % run_config.eventNums_splitting_N
                    == 0
                )
        elif split == "test":
            condition_list = [
                (event_nums + run_config.eventNums_splitting_offset_test) % run_config.eventNums_splitting_N == 0
            ] * (run_config.eventNums_splitting_N - 1)
        else:
            raise NotImplementedError
    else:
        if split == "val":
            for i in range(run_config.eventNums_splitting_N):
                condition_list.append(
                    ((event_nums - i) + run_config.eventNums_splitting_offset_val) % run_config.eventNums_splitting_N
                    == 0
                )
        elif split == "test":
            assert use_testing_set, "Split 'test' can only be used when use_testing_set is True."
            for i in range(run_config.eventNums_splitting_N):
                condition_list.append(
                    ((event_nums - i) + run_config.eventNums_splitting_offset_test) % run_config.eventNums_splitting_N
                    == 0
                )
        else:
            raise NotImplementedError

    return condition_list


def get_experiment_inputs(
    run_config: ModuleType,
    input_handler: OPTIMA.builtin.inputs.InputHandler,
    output_dir: Optional[str] = None,
    inputs_for_crossvalidation: bool = False,
    disable_printing: bool = False,
) -> Union[
    tuple[
        train_val_test_splitting_type,
        train_val_test_splitting_type,
        train_val_test_splitting_type,
        train_val_test_splitting_type,
    ],
    tuple[
        train_val_splitting_type,
        train_val_splitting_type,
        train_val_splitting_type,
        train_val_splitting_type,
    ],
]:
    """Prepares the input data used for the training during the optimization and crossvalidation and copies them to Ray's object store.

    This function depends on three functions that handle the loading and preprocessing (``get_inputs``), the splitting of
    the dataset (``get_training_data``) and the plotting of the input variables (``plot_input_data``). If they are not
    provided in the run-config, the defaults defined in ``OPTIMA.builtin.inputs`` are used. The expected behaviour of these
    three functions is described in the corresponding documentations.

    The input data is loaded by calling ``get_inputs`` and providing the ``run_config``, the desired number of events
    and the input variables to include in the dataset. If the list of input variables is not specified in the `run-config`,
    ``None`` will be provided to ``get_inputs`` and it should use all available input variables. ``get_inputs`` is
    expected to return an array of input features, an array of corresponding target labels, a 1D-array of event weights,
    a 1D-array of normalized event weights and a 1D-array of event numbers. For all arrays, axis 0 is expected to separate
    different events.

    Once loaded, the inputs, targets, weights, normalized weights and event numbers are given to ``get_target_data`` to
    be split into training, validation and (if requested) testing sets. The method of splitting and the sizes of the
    respective dataset is controlled via the ``splitting_cond`` parameter of
    ``get_target_data``. Its value is controlled by various options discussed below. Depending on the value of
    ``inputs_for_crossvalidation``, which controls if a simple splitting or a k-fold splitting is to be done and is given to
    ``get_target_data`` as ``do_kfold``, ``get_target_data`` is expected to return tuples of arrays (if
    ``inputs_for_crossvalidation`` is ``False``) or tuples of lists of arrays (if ``inputs_for_crossvalidation`` is
    ``True``). Each tuple entry is expected to correspond to a different type of dataset (training/validation/testing),
    thus is expected to have length ``2`` if no testing dataset is requested and ``3`` otherwise. If
    ``inputs_for_crossvalidation`` is ``True``, each list entry is expected to correspond to a different fold, and
    subsequently all lists are expected to be of the same length.

    If ``run_config.produce_inputs_plots`` is ``True`` and ``inputs_for_crossvalidation`` is ``False``, the
    ``plot_input_data``-function is called and the path to a subdirectory ``'inputs'`` in the provided ``output_dir``
    is given as the directory to save the plots into.

    Finally, the numpy arrays returned by ``get_target_data`` are copied to Ray's object store and the object references
    are returned.

    The behaviour of this function is controlled by various options that are expected to be present in the run-config:

    - ``max_num_events``: controls the number of events to load from the dataset and will be provided as ``nevts`` to
      ``get_inputs``.
    - ``use_testing_dataset``: if ``True``, the dataset will be split into training, validation and testing sets. If
      ``False``, only a training/validation split will be done.
    - ``use_eventNums_splitting``: `bool` to choose if the dataset should be split randomly or based on the event numbers
        - ``False``: the options ``run_config.validation_fraction`` and (if ``run_config.use_testing_dataset`` is ``True``)
          ``run_config.test_fraction`` are provided as ``splitting_cond`` to ``get_training_data``.
        - ``True``: depending on ``inputs_for_crossvalidation``, a simple splitting or a k-fold splitting based on the
          array of event numbers is performed.
            - if ``inputs_for_crossvalidation`` is ``False``: a callable evaluating the condition
              `(EventNumber + C_val) % N = 0` and (if ``use_testing_dataset`` is ``True``) a callable evaluating
              `(EventNumber + C_test) % N = 0` is/are provided as ``splitting_cond`` to ``get_training_data``. `C_val`
              and `C_test` are given by the options ``run_config.eventNums_splitting_offset_val`` and
              ``run_config.eventNums_splitting_offset_test`` and `N` is given by ``run_config.eventNums_splitting_N``.
            - ``inputs_for_crossvalidation`` is ``True``: the callable(s) provided as ``splitting_cond`` to
              ``get_training_data`` return(s) a list of boolean arrays when given an array of event numbers. Each list
              entry corresponds to a fold. The boolean arrays are calculated according to:
                - if ``run_config.use_testing_dataset`` is ``True``:
                    - if ``run_config.fixed_testing_dataset`` is ``True``: a fixed testing dataset is used for all folds
                      while the remaining dataset is used for k-fold splitting to create `k = N-1` different training/
                      validation splits.
                        - testing dataset: `(EventNumber + C_test) % N = 0`
                        - validation dataset: `(EventNumber - i + C_val) % N = 0`, with
                          `0 <= i <= N` and `(-i + C_val) % N != C_test`
                    - ``run_config.fixed_testing_dataset`` is ``False``: the subset of the data used for testing is
                      shifted in the same way as the validation dataset, resulting in `k = N` different training/
                      validation/testing splits.
                        - testing dataset: `(EventNumber - i + C_test) % N = 0`
                        - valdiation dataset: `(EventNumber - i + C_val) % N = 0`
                - ``run_config.use_testing_dataset`` is ``False``: `k = N` different training/validation splits are returned.
                  Validation dataset: `(EventNumber - i + C_val) % N = 0`
          The size of the validation dataset and (if ``run_config.use_testing_dataset`` is ``True``) the testing dataset
          are thus controlled via ``run_config.eventNums_splitting_N`` and the validation and testing set are always of the
          same size.
    - ``produce_inputs_plots``: controls if ``plot_input_data`` is called.

    Parameters
    ----------
    run_config : ModuleType
        Reference to the imported run-config file.
    input_handler : OPTIMA.builtin.inputs.InputHandler
        Instance of the ``InputHandler``-class.
    output_dir : Optional[str]
        Directory to save the output plots to. (Default value = None)
    inputs_for_crossvalidation : bool
        If True, k-fold splitting will be performed according to the options given in the run-config. Otherwise, simple
        splitting is done. (Default value = False)
    disable_printing : bool
        If True, no messages will be printed. (Default value = False)

    Returns
    -------
    Union[
        tuple[
        train_val_test_splitting_type,
        train_val_test_splitting_type,
        train_val_test_splitting_type,
        train_val_test_splitting_type,
        ],
        tuple[
        train_val_splitting_type,
        train_val_splitting_type,
        train_val_splitting_type,
        train_val_splitting_type,
        ],
    ]
        The Ray object references to the split inputs, targets, weights and normalized weights are returned.
    """
    # define splitting conditions
    if not run_config.use_eventNums_splitting:
        if run_config.use_testing_dataset:
            splitting_cond_trainVal_test = run_config.test_fraction
            splitting_cond_train_val = run_config.validation_fraction
            splitting_cond = (splitting_cond_trainVal_test, splitting_cond_train_val)
        else:
            splitting_cond = run_config.validation_fraction
    elif run_config.use_eventNums_splitting and not inputs_for_crossvalidation:
        if run_config.use_testing_dataset:
            splitting_cond_trainVal_test = (
                lambda x: (x + run_config.eventNums_splitting_offset_test) % run_config.eventNums_splitting_N == 0
            )
            splitting_cond_train_val = (
                lambda x: (x + run_config.eventNums_splitting_offset_val) % run_config.eventNums_splitting_N == 0
            )
            splitting_cond = (splitting_cond_trainVal_test, splitting_cond_train_val)
        else:
            splitting_cond = (
                lambda x: (x + run_config.eventNums_splitting_offset_val) % run_config.eventNums_splitting_N == 0
            )
    elif run_config.use_eventNums_splitting and inputs_for_crossvalidation:
        if run_config.use_testing_dataset:
            splitting_cond_trainVal_test = partial(
                _event_nums_splitting_cond_kfold,
                run_config=run_config,
                split="test",
                use_testing_set=True,
                fixed_testing_set=run_config.fixed_testing_dataset,
            )
            splitting_cond_train_val = partial(
                _event_nums_splitting_cond_kfold,
                run_config=run_config,
                split="val",
                use_testing_set=True,
                fixed_testing_set=run_config.fixed_testing_dataset,
            )
            splitting_cond = (splitting_cond_trainVal_test, splitting_cond_train_val)
        else:
            splitting_cond = partial(
                _event_nums_splitting_cond_kfold, run_config=run_config, split="val", use_testing_set=False
            )

    # load the input data and split it
    if hasattr(run_config, "get_inputs"):
        get_inputs = run_config.get_inputs
    else:
        get_inputs = OPTIMA.builtin.inputs.get_inputs
    inputs, targets, weights, normalized_weights, event_nums = get_inputs(
        run_config,
        run_config.max_num_events,
        input_handler.get_vars(as_indices=input_handler.as_indices),
        disable_printing=disable_printing,
    )

    # if no input variables were specified in the run_config, we can use the indices of the inputs instead. For that,
    # we need to provide all possible indices once to the input handler.
    if input_handler.get_vars() is None:
        index_slices = [
            list(range(i)) for i in inputs[0].shape
        ]  # get the shape of an input and get indices for each dimension
        indices_list = list(itertools.product(*index_slices))  # calculate the cross product over the lists of indices
        input_handler.set_vars(indices_list, as_indices=True)

    if hasattr(run_config, "get_training_data"):
        get_training_data = run_config.get_training_data
    else:
        get_training_data = OPTIMA.builtin.inputs.get_training_data
    (
        inputs_split,
        targets_split,
        weights_split,
        normalized_weights_split,
    ) = get_training_data(
        inputs,
        targets,
        weights,
        normalized_weights,
        splitting_cond,
        event_nums=event_nums,
        do_kfold=inputs_for_crossvalidation,
        fixed_test_dataset=run_config.fixed_testing_dataset,
        disable_printing=disable_printing,
    )

    if run_config.produce_inputs_plots and not inputs_for_crossvalidation:
        if not disable_printing:
            print("Plotting the input variables...")
        if hasattr(run_config, "plot_input_data"):
            plot_input_data = run_config.plot_input_data
        else:
            plot_input_data = OPTIMA.builtin.inputs.plot_input_data
        plot_input_data(
            run_config,
            inputs,
            targets,
            input_handler.get_vars(),
            outdir=os.path.join(output_dir, "inputs"),
            weights=weights,
        )

    # copy the data to the object store
    inputs_split = [[ray.put(arr) for arr in e] if isinstance(e, list) else ray.put(e) for e in inputs_split]
    targets_split = [[ray.put(arr) for arr in e] if isinstance(e, list) else ray.put(e) for e in targets_split]
    weights_split = [[ray.put(arr) for arr in e] if isinstance(e, list) else ray.put(e) for e in weights_split]
    normalized_weights_split = [
        [ray.put(arr) for arr in e] if isinstance(e, list) else ray.put(e) for e in normalized_weights_split
    ]

    return inputs_split, targets_split, weights_split, normalized_weights_split
