from typing import Optional

from .common import SLURMCluster, SLURMClusterJob


class Romeo(SLURMCluster):
    cpus_per_node = 128
    gpus_per_node = 0
    mem_per_cpu = 1972
    threads_per_cpu_core = 2
    SMT_included_in_reservation = False
    ray_headnodes_path = "/projects/materie-09/s7701085/running_ray_headnodes/running_ray_headnodes.pickle"
    ray_temp_path = "/tmp/ray"  # default

    def get_ports(self) -> dict[str, tuple[int, int]]:
        port_config = {
            "port": (6379, 1),
            "node_manager_port": (6700, 100),
            "object_manager_port": (6701, 100),
            "ray_client_server_port": (10001, 1000),
            "redis_shard_ports": (6702, 100),
            "min_worker_port": (10002, 1000),
            "max_worker_port": (10999, 1000),
        }
        return port_config

    def submit_job(self, job: "SLURMClusterJob", job_file_path: str, dry_run: bool = False) -> None:
        job.partition = "romeo"
        job.account = "materie-09"
        job.use_SMT = False
        super().submit_job(job, job_file_path, dry_run)

    def _execute_single_cmd(self, cmd: str, cpus: Optional[int] = None, node: Optional[str] = None) -> str:
        return super()._execute_single_cmd(cmd=cmd, cpus=cpus, node=node, disable_cpu_binding=True)

    def _write_job_config(self, job: "SLURMClusterJob") -> str:
        config = "#!/usr/bin/env bash\n\n"
        config += super()._write_job_config(job)
        return config


class Barnard(SLURMCluster):
    cpus_per_node = 104
    gpus_per_node = 0
    mem_per_cpu = 4800
    threads_per_cpu_core = 2
    SMT_included_in_reservation = False
    ray_headnodes_path = "/projects/materie-09/OPTIMA/running_ray_headnodes/running_ray_headnodes.pickle"
    ray_temp_path = "/dev/shm/ray"

    def get_ports(self) -> dict[str, tuple[int, int]]:
        port_config = {
            "port": (6379, 1),
            "node_manager_port": (6700, 100),
            "object_manager_port": (6701, 100),
            "ray_client_server_port": (10001, 1000),
            "redis_shard_ports": (6702, 100),
            "min_worker_port": (10002, 1000),
            "max_worker_port": (10999, 1000),
        }
        return port_config

    def submit_job(self, job: "SLURMClusterJob", job_file_path: str, dry_run: bool = False) -> None:
        job.account = "materie-09"
        job.use_SMT = False
        super().submit_job(job, job_file_path, dry_run)

    def _execute_single_cmd(self, cmd: str, cpus: Optional[int] = None, node: Optional[str] = None) -> str:
        return super()._execute_single_cmd(cmd=cmd, cpus=cpus, node=node, disable_cpu_binding=True)

    def _write_job_config(self, job: "SLURMClusterJob") -> str:
        config = "#!/usr/bin/env bash\n\n"
        config += super()._write_job_config(job)
        return config

