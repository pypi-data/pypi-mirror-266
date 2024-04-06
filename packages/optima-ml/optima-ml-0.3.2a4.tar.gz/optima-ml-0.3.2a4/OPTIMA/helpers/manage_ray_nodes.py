#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helper module to manage the ray nodes on a cluster."""
import os
import pickle
import argparse
import sys
import time
import logging

from OPTIMA.hardware_configs.helpers import get_cluster


def get_and_verify_running_head_nodes(cluster, update_ray_nodes_file=True):
    """_summary_.

    Parameters
    ----------
    cluster : _type_
        _description_
    update_ray_nodes_file : _type_
        _description_ (Default value = True)

    Returns
    -------
    _type_
        _description_
    """
    # get the list of machines that is currently running ray head nodes
    if not os.path.exists(cluster.ray_headnodes_path):
        with open(cluster.ray_headnodes_path, "wb") as file:
            pickle.dump([], file)
        os.chmod(cluster.ray_headnodes_path, 0o664)
        return []
    else:
        with open(cluster.ray_headnodes_path, "rb") as file:
            running_head_nodes = pickle.load(file)

    # get all head nodes; check if the corresponding job is still running
    verified_running_head_nodes = []
    logging.info("Verifying running ray head nodes...")
    for job_id, head_node, instance_num in running_head_nodes:
        logging.info(f"Checking if job {job_id} is still running...")
        job_running = cluster.check_job_running(job_id)

        # update the list for all jobs that are still running
        if job_running:
            logging.info(f"Job {job_id} is still running.")
            verified_running_head_nodes.append([job_id, head_node, instance_num])
        else:
            logging.info(
                f"Job {job_id} has been terminated." + " Removing the entry from the ray head nodes file."
                if update_ray_nodes_file
                else ""
            )

    if update_ray_nodes_file:
        with open(cluster.ray_headnodes_path, "wb") as file:
            pickle.dump(verified_running_head_nodes, file)

    return verified_running_head_nodes


def sort_nodes(running_head_nodes, cluster):
    """Return a sorted list of nodes for this job, starting with free nodes (i.e. no ray  head nodes), followed by occupied nodes.

    This function will fetch all nodes for this job, check on which of them a ray head node is already running and return a sorted list
    + a boolean if any of the available nodes is still free

    Parameters
    ----------
    running_head_nodes : _type_
        _description_
    cluster : _type_
        _description_
    """
    nodes_list = cluster.get_job_nodes_list()

    # get the list of running head nodes
    running_head_nodes_list = []
    for _, head_node, _ in running_head_nodes:
        running_head_nodes_list.append(head_node)

    # go through all nodes of this job and check if they are in running_head_nodes_list
    available_nodes = []
    occupied_nodes = []
    for node in nodes_list:
        if node in running_head_nodes_list:
            occupied_nodes.append(node)
        else:
            available_nodes.append(node)

    return available_nodes + occupied_nodes, len(available_nodes) > 0


def main():
    """_summary_.

    Returns
    -------
    _type_
        _description_
    """
    # TODO: add config!
    parser = argparse.ArgumentParser(
        description="Helper script that contains useful function to manage ray nodes",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--cluster",
        help="Specify which cluster the job should be executed on. This must be one of the "
        "possible values given in get_cluster() in hardware_config.common.",
    )
    parser.add_argument(
        "--sorted_nodes_path",
        default="temp_sorted_nodes.txt",
        help="Path to the file where the sorted list of nodes for this job should be saved.",
    )
    parser.add_argument(
        "--sorted_cpus_per_node_path",
        default="temp_sorted_cpus_per_node.txt",
        help="Path to the file where the sorted list of cpus per node for this job should be saved.",
    )
    parser.add_argument(
        "--instance_num_path",
        default="temp_instance_num.txt",
        help="Path to the file where the instance_num that is to be used for this job should be saved. This is needed "
        "to ensure different Ray clusters use different ports for the communication.",
    )
    args = parser.parse_args(sys.argv[1:])

    # logging config
    DFormat = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=DFormat, level=logging.INFO)

    # get the cluster for this job
    cluster = get_cluster(args.cluster)

    # in order to prevent multiple jobs from accessing running_headnodes.pickle at the same time, create a queue to
    # schedule the accesses based on the job id
    # wrap in try...finally block to make sure the queue file is deleted in the end
    try:
        job_id = cluster.get_job_id()
        node_folder = os.path.dirname(cluster.ray_headnodes_path)
        queue_file_path = os.path.join(
            node_folder, job_id
        )  # temporary file to tell other jobs that this job wants to access the running_headnodes.pickle file
        open(queue_file_path, "w").close()  # create temporary file

        # get all files in the working dir, excluding the running_headnodes.pickle file --> should only be temporary files created
        # by waiting jobs, file names are the corresponding job ids --> sort the ids and only continue, if this jobs id is the lowest
        # one; if not, check again in a few seconds
        can_start = False
        while not can_start:
            # get all files and remove the .pickle file (if present)
            file_list = os.listdir(node_folder)
            if os.path.basename(cluster.ray_headnodes_path) in file_list:
                file_list.remove(os.path.basename(cluster.ray_headnodes_path))

            # convert to int and sort
            file_list = [int(file) for file in file_list]
            file_list.sort()

            # check if jobs associated to queue files are still running (files may remain if job crashes or is canceled here)
            for job_id in file_list:
                if not cluster.check_job_running(str(job_id)):
                    logging.info(f"Job {job_id} has been terminated, but entry is still present in queue. Removing...")
                    try:
                        file_list.remove(job_id)
                        os.remove(os.path.join(node_folder, str(job_id)))
                    except FileNotFoundError:
                        pass

            # start if this job id is the first entry in the sorted list
            queue_spot = file_list.index(job_id) + 1
            if queue_spot == 1:
                logging.info("Number 1 in queue, starting...")
                can_start = True
            else:
                logging.info(f"Number {queue_spot} in queue, waiting...")
                time.sleep(15)

        running_head_nodes = get_and_verify_running_head_nodes(cluster)
        sorted_nodes, node_available = sort_nodes(running_head_nodes, cluster)

        if node_available:
            # get the smallest instance num that is still free
            instance_nums_taken = [running_head_node[2] for running_head_node in running_head_nodes]
            next_free_instance_num = next(i for i, e in enumerate(sorted(instance_nums_taken) + [None], 1) if i != e)
            logging.info(f"Using instance num {next_free_instance_num}.")

            # update list of running head nodes
            running_head_nodes.append([str(job_id), sorted_nodes[0], next_free_instance_num])
            with open(cluster.ray_headnodes_path, "wb") as file:
                pickle.dump(running_head_nodes, file)

            # save sorted nodes list to file
            with open(args.sorted_nodes_path, "w") as file:
                file.write(" ".join(sorted_nodes))

            # also dump the number of cpus per node (in the same order as sorted_nodes)
            num_cpus_per_node = cluster.get_cpus_per_nodes()
            sorted_num_cpus = [str(num_cpus_per_node[node]) for node in sorted_nodes]
            with open(args.sorted_cpus_per_node_path, "w") as file:
                file.write(" ".join(sorted_num_cpus))

            # finally save the instance_num that is to be used
            with open(args.instance_num_path, "w") as file:
                file.write(str(next_free_instance_num))
        else:
            # exit code 129 to tell optimization script that no free node was found
            sys.exit(129)
    finally:
        # remove the queue file
        os.remove(queue_file_path)


if __name__ == "__main__":
    main()
