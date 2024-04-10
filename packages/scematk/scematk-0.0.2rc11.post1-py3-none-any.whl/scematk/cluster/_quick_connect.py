from .profiles._get_profile import get_profile
from dask_jobqueue import HTCondorCluster, LSFCluster, MoabCluster, OARCluster, PBSCluster, SGECluster, SLURMCluster

def quick_connect(profile: str, minimum: int, maximum: int, min_n_wait: int = None, timeout: int = 300):
    assert isinstance(profile, str), "profile must be a string"
    assert isinstance(minimum, int), "minimum must be an integer"
    assert isinstance(maximum, int), "maximum must be an integer"
    if min_n_wait is None:
        min_n_wait = minimum
    assert isinstance(min_n_wait, int), "min_n_wait must be an integer"
    assert min_n_wait <= minimum, "min_n_wait must be less than or equal to minimum"
    assert isinstance(timeout, int), "timeout must be an integer"
    profile_dict = get_profile(profile)
    cluster_type = profile_dict.pop('cluster_type')
    if cluster_type == 'HTCondor':
        cluster = HTCondorCluster(**profile_dict)
    elif cluster_type == 'LSF':
        cluster = LSFCluster(**profile_dict)
    elif cluster_type == 'Moab':
        cluster = MoabCluster(**profile_dict)
    elif cluster_type == 'OAR':
        cluster = OARCluster(**profile_dict)
    elif cluster_type == 'PBSCluster':
        cluster = PBSCluster(**profile_dict)
    elif cluster_type == 'SGE':
        cluster = SGECluster(**profile_dict)
    elif cluster_type == 'SLURM':
        cluster = SLURMCluster(**profile_dict)
    else:
        raise ValueError(f"Unsupported cluster type: {cluster_type}")
    try:
        cluster.adapt(minimum=minimum, maximum=maximum)
    except Exception as e:
        cluster.close()
        raise e
    try:
        cluster.wait_for_workers(min_n_wait, timeout=timeout)
    except TimeoutError:
        cluster.close()
        raise TimeoutError(f"Timeout: {min_n_wait} workers did not start within {timeout} seconds")
    except Exception as e:
        cluster.close()
        raise e
    return cluster