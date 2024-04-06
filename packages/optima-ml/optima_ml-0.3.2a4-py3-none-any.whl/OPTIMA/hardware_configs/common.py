from typing import Optional, Union

import os
import subprocess
from abc import ABC, abstractmethod


class Cluster(ABC):
    type = None

    cpus_per_node = None
    gpus_per_node = None
    mem_per_cpu = None
    threads_per_cpu_core = None  # number of threads per cpu core (SMT)
    SMT_included_in_reservation = None  # if requesting N cores, do we get N logical (SMT_included_in_reservation=True) or N physical cores (SMT_included_in_reservation=False)

    # str; path to pickle file containing a list of type [[job_id, head_node_name, instance_num], [...]] marking which
    # node already runs a Ray head node and which instance_num is used for it; if it does not exist, it will be created
    # by helpers/manage_ray_nodes.py
    # Importantly, this file needs to be writable from the worker nodes!
    ray_headnodes_path = None
    ray_temp_path = "/tmp/ray"  # path where Ray's temporary session files can be saved to; this should preferably be a local directory on each worker node.

    def submit_job(self, job: "ClusterJob", job_file_path: str, dry_run: bool = False) -> None:
        """Writes the job file for the provided job and submits it to the batch system."""
        if os.path.dirname(job_file_path) != "" and not os.path.exists(os.path.dirname(job_file_path)):
            os.makedirs(os.path.dirname(job_file_path))
        with open(job_file_path, "w") as f:
            f.write(self._write_job_config(job) + "\n")
            f.write(job.payload)

        if not dry_run:
            self._submit(job_file_path)

    @abstractmethod
    def get_job_nodes_list(self) -> list:
        """Returns a list of nodes for the current job."""
        raise NotImplementedError

    @abstractmethod
    def get_job_nodes_list_bash(self) -> str:
        """Returns a string containing a bash command to fetch the list of node names for the current job."""
        raise NotImplementedError

    @abstractmethod
    def get_node_ip_bash(self, node: str) -> str:
        """Returns a string containing a bash command to fetch the ip address of the provided node."""
        raise NotImplementedError

    @abstractmethod
    def get_job_id(self) -> str:
        """Returns a string containing the id of the current job."""
        raise NotImplementedError

    @abstractmethod
    def get_job_id_bash(self) -> str:
        """Returns a string containing a bash command to fetch the id of the current job."""
        raise NotImplementedError

    @abstractmethod
    def check_job_running(self, job_id) -> bool:
        """Checks if a job for a given job_id is still running."""
        raise NotImplementedError

    @abstractmethod
    def get_cpus_per_nodes(self, include_SMT: Optional[bool] = False) -> dict[str, int]:
        """Returns a dict of type {'node_name': num_cpus, ...} containing the number of cpus reserved on each node in the job."""
        raise NotImplementedError

    @abstractmethod
    def get_ports(self) -> dict[str, tuple[int, int]]:
        """
        Returns a dict of port numbers that can be used for the communication between the Ray nodes.

        See https://docs.ray.io/en/releases-2.5.1/ray-core/configure.html#ports-configurations for explanations of the
        available ports.

        The keys must be:

        - `'port'`
        - `'node_manager_port'`
        - object_manager_port
        - ray_client_server_port
        - redis_shard_ports
        - min_worker_port
        - max_worker_port

        In order to allow multiple parallel Ray clusters, the corresponding ports must be different for each job. Thus,
        instead of only a single port number, each value must be a tuple of two integers. The first value is the port
        to be used for the first job, and the second number if the offset that is added for each additional job. For example,
        a value of `(6700, 10)` would mean that the first job uses port 6700, the second job port 6710, etc.
        """
        raise NotImplementedError

    def start_ray_node(
            self,
            node: str,
            head_ip: str,
            num_cpus: Union[int, str],
            num_gpus: Union[int, str],
            head: bool = False,
            port: Optional[Union[int, str]] = None,
            node_manager_port: Optional[Union[int, str]] = None,
            object_manager_port: Optional[Union[int, str]] = None,
            ray_client_server_port: Optional[Union[int, str]] = None,
            redis_shard_ports: Optional[Union[int, str]] = None,
            min_worker_port: Optional[Union[int, str]] = None,
            max_worker_port: Optional[Union[int, str]] = None,
    ) -> str:
        """Returns a string containing a bash command to start a ray node on the provided node."""
        if head:
            cmd = f" \\\n\tray start --head \\\n"
            cmd += f"\t\t--node-ip-address=\"{head_ip}\" \\\n"
            cmd += f"\t\t--port={port} \\\n"
            cmd += f"\t\t--node-manager-port={node_manager_port} \\\n"
            cmd += f"\t\t--object-manager-port={object_manager_port} \\\n"
            cmd += f"\t\t--ray-client-server-port={ray_client_server_port} \\\n"
            cmd += f"\t\t--redis-shard-ports={redis_shard_ports} \\\n"
            cmd += f"\t\t--min-worker-port={min_worker_port} \\\n"
            cmd += f"\t\t--max-worker-port={max_worker_port} \\\n"
            cmd += f"\t\t--num-cpus {num_cpus} \\\n"
            cmd += f"\t\t--num-gpus {num_gpus} \\\n"
            cmd += f"\t\t--temp-dir {self.ray_temp_path} \\\n"
            cmd += f"\t\t--include-dashboard false \\\n"
            cmd += f"\t\t--block --disable-usage-stats &"
        else:
            cmd = f" \\\n\tray start \\\n"
            cmd += f"\t\t--address {head_ip} \\\n"
            cmd += f"\t\t--num-cpus {num_cpus} \\\n"
            cmd += f"\t\t--num-gpus {num_gpus} \\\n"
            cmd += f"\t\t--block --disable-usage-stats &"

        cmd = self._execute_single_cmd(cmd, num_cpus, node)
        return cmd

    @abstractmethod
    def _write_job_config(self, job: "ClusterJob") -> str:
        """Helper function that returns the header of the job file defining the job config, i.e. number of cpus etc."""
        raise NotImplementedError

    @abstractmethod
    def _submit(self, job_file_path: str) -> None:
        """Helper function that submits a job to the batch system."""
        raise NotImplementedError

    @abstractmethod
    def _execute_single_cmd(self, cmd: str, cpus: Optional[int] = None, node: Optional[str] = None) -> str:
        """Helper function that returns a bash command that executes a single command on a specific node of the cluster."""
        raise NotImplementedError


class ClusterJob(ABC):
    def __init__(
            self,
            name: Optional[str] = None,
            cpus: Optional[int] = None,
            gpus: Optional[int] = None,
            nodes: Optional[int] = None,
            tasks: Optional[int] = None,
            tasks_per_node: Optional[int] = None,
            gpus_per_node: Optional[int] = None,
            cpus_per_task: Optional[int] = None,
            mem_per_cpu: Optional[Union[int, float]] = None,
            use_SMT: Optional[bool] = None,
            runtime: Optional[Union[int, float]] = None,
            log_path_out: Optional[str] = None,
            log_path_error: Optional[str] = None,
            payload: Optional[str] = None,
    ):
        self.name = name
        self.cpus = cpus
        self.gpus = gpus
        self.nodes = nodes
        self.tasks = tasks
        self.tasks_per_node = tasks_per_node
        self.gpus_per_node = gpus_per_node
        self.cpus_per_task = cpus_per_task
        self.mem_per_cpu = mem_per_cpu
        self.use_SMT = use_SMT
        self.runtime = runtime
        self.log_path_out = log_path_out
        self.log_path_error = log_path_error
        self.payload = payload

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def cpus(self):
        return self._cpus

    @cpus.setter
    def cpus(self, value):
        self._cpus = value

    @property
    def gpus(self):
        return self._gpus

    @gpus.setter
    def gpus(self, value):
        self._gpus = value

    @property
    def nodes(self):
        return self._nodes

    @nodes.setter
    def nodes(self, value):
        self._nodes = value

    @property
    def tasks(self):
        return self._tasks

    @tasks.setter
    def tasks(self, value):
        self._tasks = value

    @property
    def tasks_per_node(self):
        return self._tasks_per_node

    @tasks_per_node.setter
    def tasks_per_node(self, value):
        self._tasks_per_node = value

    @property
    def gpus_per_node(self):
        return self._gpus_per_node

    @gpus_per_node.setter
    def gpus_per_node(self, value):
        self._gpus_per_node = value

    @property
    def cpus_per_task(self):
        return self._cpus_per_task

    @cpus_per_task.setter
    def cpus_per_task(self, value):
        self._cpus_per_task = value

    @property
    def mem_per_cpu(self):
        return self._mem_per_cpu

    @mem_per_cpu.setter
    def mem_per_cpu(self, value):
        self._mem_per_cpu = value

    @property
    def use_SMT(self):
        return self._use_SMT

    @use_SMT.setter
    def use_SMT(self, value):
        self._use_SMT = value

    @property
    def runtime(self):
        return self._runtime

    @runtime.setter
    def runtime(self, value):
        self._runtime = value

    @property
    def log_path_out(self):
        return self._log_path_out

    @log_path_out.setter
    def log_path_out(self, value):
        self._log_path_out = value

    @property
    def log_path_error(self):
        return self._log_path_error

    @log_path_error.setter
    def log_path_error(self, value):
        self._log_path_error = value

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, value):
        self._payload = value


class SLURMCluster(Cluster):
    type = "SLURM"

    def get_job_nodes_list(self) -> list:
        # get the list of nodes
        nodes = os.environ["SLURM_JOB_NODELIST"]

        # expand the possible list of nodes that may be present here, e. g. taurusi[7041-7042,7045-7046]
        if "[" in nodes:  # assuming sensible node names
            nodes_range = nodes.split("[")[1].split("]")[0]
            nodes_list_int = self._rangeexpand(nodes_range)
            nodes_list = [nodes.split("[")[0] + str(node_num) for node_num in nodes_list_int]
        else:
            nodes_list = [nodes]

        return nodes_list

    def get_job_nodes_list_bash(self) -> str:
        return "$SLURM_JOB_NODELIST"

    def get_node_ip_bash(self, node: str) -> str:
        return f"$(srun --nodes=1 --ntasks=1 -w \"{node}\" hostname --ip-address)"

    def get_job_id(self) -> str:
        return os.environ["SLURM_JOB_ID"]

    def get_job_id_bash(self) -> str:
        return "$SLURM_JOB_ID"

    def check_job_running(self, job_id) -> bool:
        # check if this job is still running by executing "squeue -o '$i' --job job_id" and see if error
        # is thrown (invalid job id -> job is not running) or the job_id is returned
        try:
            subprocess.check_output(["squeue", "-o", "'%i'", "--job", job_id], stderr=subprocess.DEVNULL).decode("utf-8")
            job_running = True
        except subprocess.CalledProcessError:
            job_running = False
        return job_running

    def get_cpus_per_nodes(self, include_SMT: Optional[bool] = False) -> dict[str, int]:
        # get the necessary information
        job_id = os.environ["SLURM_JOB_ID"]
        p = subprocess.check_output(["scontrol", "show", "job", "-d", job_id]).decode("utf-8")

        resources = {}
        for line in p.split("\n"):
            # get list of cpus per node
            if "Nodes=" in line and not "NumNodes" in line:
                # first get ranges for nodes and cpus
                nodes, cpus, _, _ = line.split()
                nodes = nodes.split("=")[1]
                cpus = cpus.split("=")[1]

                # expand the possible list of nodes that may be present here, e. g. taurusi[7041-7042,7045-7046]
                if "[" in nodes:  # assuming sensible node names
                    nodes_range = nodes.split("[")[1].split("]")[0]
                    nodes_list_int = self._rangeexpand(nodes_range)
                    nodes_list = [nodes.split("[")[0] + str(node_num) for node_num in nodes_list_int]
                else:
                    nodes_list = [nodes]

                # now expand the range of cpus
                cpus_list = self._rangeexpand(cpus)

                for node in nodes_list:
                    resources[node] = cpus_list

        # convert list of cpus to number of cpus in each node
        num_cpus_per_node = {}
        for node, cpus_list in resources.items():
            num_cpus_per_node[node] = int(round(len(cpus_list) / (self.threads_per_cpu_core if not include_SMT else 1)))

        return num_cpus_per_node

    def _write_job_config(self, job: "SLURMClusterJob") -> str:
        runtime_hours = int(job.runtime)
        runtime_minutes = int(60 * (job.runtime - runtime_hours))
        runtime_seconds = int(3600 * (job.runtime - runtime_hours - 1 / 60 * runtime_minutes))

        config = f"#SBATCH --job-name={job.name}\n"
        config += f"#SBATCH --output={job.log_path_out}\n"
        config += f"#SBATCH --error={job.log_path_error}\n"
        config += f"#SBATCH --account={job.account}\n" if job.account is not None else ""
        config += f"#SBATCH --partition={job.partition}\n" if job.partition is not None else ""
        config += f"#SBATCH --time={f'{runtime_hours:02d}:{runtime_minutes:02d}:{runtime_seconds:02d}'}\n"
        config += f"#SBATCH --nodes={job.nodes}\n" if job.nodes is not None else ""
        config += f"#SBATCH --ntasks={job.tasks}\n" if job.tasks is not None else ""
        config += f"#SBATCH --tasks-per-node={job.tasks_per_node}\n" if job.tasks_per_node is not None else ""
        config += f"#SBATCH --cpus-per-task={job.cpus_per_task * (self.threads_per_cpu_core if (self.SMT_included_in_reservation and job.use_SMT) else 1)}\n" if job.cpus_per_task is not None else ""
        if job.gpus_per_node is not None:
            config += f"#SBATCH --gres=gpu:{job.gpus_per_node}" if (job.gpus_per_node > 0) else ""
        config += f"#SBATCH --mem-per-cpu={int(job.mem_per_cpu)}\n" if job.mem_per_cpu is not None else ""
        config += f"#SBATCH --exclude={','.join(job.excludes_list)}\n" if job.excludes_list not in [None, []] else ""
        config += "#SBATCH --hint=nomultithread\n" if not job.use_SMT else ""
        return config

    def _submit(self, job_file_path: str) -> None:
        job_proc = ["sbatch", job_file_path]
        print("SubmitString: " + " ".join(job_proc))
        jid = subprocess.check_output(job_proc, stderr=subprocess.STDOUT).decode("utf-8")
        print("Return: {}".format(jid))

    def _execute_single_cmd(self, cmd: str, cpus: Optional[int] = None, node: Optional[str] = None, disable_cpu_binding: Optional[bool] = False) -> str:
        return f"srun --nodes=1 --ntasks=1 {f'--cpus-per-task {cpus} ' if cpus is not None else ''}" \
               f"{f'-w {node} ' if node is not None else ''}{'--cpu-bind=no' if disable_cpu_binding else ''}{cmd}"

    def _rangeexpand(self, txt):
        """Helper function to expand ranges like "1-3,4,5,7-9,10" to a list of integers containing all values."""
        lst = []
        for r in txt.split(','):
            if '-' in r[1:]:
                r0, r1 = r[1:].split('-', 1)
                lst += range(int(r[0] + r0), int(r1) + 1)
            else:
                lst.append(int(r))
        return lst


class SLURMClusterJob(ClusterJob):
    def __init__(
            self,
            *args,
            partition: Optional[str] = None,
            account: Optional[str] = None,
            excludes_list: Optional[str] = None,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.partition = partition
        self.account = account
        self.excludes_list = excludes_list

    @property
    def partition(self):
        return self._partition

    @partition.setter
    def partition(self, value):
        self._partition = value

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    @property
    def excludes_list(self):
        return self._excludes_list

    @excludes_list.setter
    def excludes_list(self, value):
        self._excludes_list = value
