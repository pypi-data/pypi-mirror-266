# -*- coding: utf-8 -*-
"""_summary_."""
from types import ModuleType

import sys
import logging

try:
    import root_numpy as rn
except ModuleNotFoundError:
    logging.info("This script requires root_numpy!")
    sys.exit(1)

import numpy as np
import pandas as pd
import os
import imp
import argparse
import logging


def get_logging() -> logging.Logger:
    """Setup the logging configuration.

    Returns
    -------
    logging.Logger
        configured logger
    """
    log_level = logging.DEBUG
    log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")

    # Logging configuration
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(log_format)

    # Create logger
    log_level = logging.INFO
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Add logger handler
    if not logger.handlers:
        logger.addHandler(console_handler)
    return logger


def extract_features_and_targets(config: ModuleType) -> pd.DataFrame:
    """Extract the features and the targets of the given data.

    Parameters
    ----------
    config : ModuleType
        imported config file

    Returns
    -------
    pd.DataFrame
        event features and targets
    """
    # the trees of the processes
    process_trees = config.process_trees
    if isinstance(process_trees, str):
        process_trees = [process_trees]

    # get the list of trees
    tree_names_list = rn.list_trees(config.root_file_path)

    # extract the available features from the first tree
    feature_names = rn.list_branches(config.root_file_path, tree_names_list[0])

    # rename weight column ('Weight' -> 'weight')
    try:
        feature_names[feature_names.index("Weight")] = "weight"
    except ValueError:
        pass

    # contains the names of the branches of the extracted trees
    features = []

    # targets dataframe
    targets = []

    # count the trees for summary
    target_sum = np.zeros(len(process_trees))
    skipped_trees = 0

    # iterate over all trees, convert them to numpy structured arrays and append them to trees_list
    for tree_name in tree_names_list:
        logging.info(f"Now at {tree_name}")

        # set target
        target = np.array([1.0 if process in tree_name else 0 for process in process_trees])
        target_sum += target

        # skip not classified trees for multiclass classifier
        if len(process_trees) > 1 and sum(target) == 0:
            logging.warning(f"No classification found for {tree_name} in {process_trees}. Skipping tree")
            skipped_trees += 1
            continue

        # check if the tree is in more than one classification
        if sum(target) > 1:
            raise RuntimeError(f"{tree_name} was classified in multiple categories {process_trees[target == 1.]}")

        # extract tree
        tree = rn.root2array(
            config.root_file_path, tree_name
        )  # returns structured array, column names are extracted from branch names

        # append features
        features.append(tree)

        # append targets
        targets.append(np.array([target] * len(tree)))

    # merge all trees
    features_merged = np.concatenate(features)
    targets_merged = np.concatenate(targets)

    # create dataframes
    features_df = pd.DataFrame(features_merged, columns=feature_names)
    targets_df = pd.DataFrame(targets_merged, columns=process_trees, dtype=np.float32)

    # concatenate into one dataframe
    events = pd.concat([features_df, targets_df], axis=1, keys=["features", "targets"])

    # give summary
    logging.info(f"{skipped_trees} trees were skipped")
    for i, process in enumerate(process_trees):
        logging.info(f"{int(target_sum[i])} trees belong to the {process} classification")
    return events


def main():
    """Extract the NTuple content."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        default=os.path.join(os.path.dirname(__file__), "config.py"),
        help="Path to config file for transformation",
    )
    args = parser.parse_args()
    logger = get_logging()

    logger.info(f"Import config {args.config}")
    # import config file
    config = imp.load_source("config", args.config)

    logging.info("Extracting trees")

    events = extract_features_and_targets(config)

    # create output dir if not exists
    output_directory = os.path.dirname(config.inputs_file)
    if not os.path.exists(output_directory):
        logging.info(f"Create output directory {output_directory}")
        os.system("mkdir -p " + output_directory)

    logging.info(f"Save features and targets to {config.inputs_file}")
    # save events to pickle
    events.to_pickle(config.inputs_file)


if __name__ == "__main__":
    main()
