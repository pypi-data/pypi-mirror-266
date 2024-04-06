from .common import Cluster, ClusterJob, SLURMClusterJob
from . import Dresden_Taurus

def get_cluster(name: str) -> Cluster:
    if name in ["romeo", "Romeo"]:
        return Dresden_Taurus.Romeo()
    if name in ["barnard", "Barnard"]:
        return Dresden_Taurus.Barnard()
    else:
        raise ValueError(f"Cluster {name} is not known!")


def get_suitable_job(cluster: Cluster) -> ClusterJob:
    if cluster.type == "SLURM":
        return SLURMClusterJob()
    else:
        return ClusterJob()
