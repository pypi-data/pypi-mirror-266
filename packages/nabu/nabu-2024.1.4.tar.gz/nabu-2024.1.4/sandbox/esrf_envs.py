from .sysutils import *

esrf_environments = {
    "ubuntu20.04_cuda10_ppc64le": {
        "needs_conda": False,
        "base_dir": "/scisoft/tomotools_env/nabu/ubuntu20.04/cuda10.1.243-3/ppc64le"
    },
    "ubuntu20.04_cuda10": {
        "needs_conda": False,
        "base_dir": "/scisoft/tomotools_env/nabu/ubuntu20.04/cuda10.1.243-3/x86_64"
    },
    "deb8_cuda75": {
        "needs_conda": True,
        "base_dir": "/scisoft/tomotools_env/nabu/debian8.11/cuda7.5.18-4~bpo8+1",
    },

}


# Rules for SLURM partitions
slurm_partitions_mappings = {
    "p9gpu": "ubuntu20.04_cuda10_ppc64le",
    "id16a": "ubuntu20.04_cuda10_ppc64le",
}

# Rules for individual nodes
nodes_mappings = {
    "p9-??": "ubuntu20.04_cuda10_ppc64le",
    "gpid16a-180?": "ubuntu20.04_cuda10",
    "gpu2-14??": "deb8_cuda75", # OAR
    "gptomo-nice-0405": "deb8_cuda75",
    "gpid11-nice": "deb8_cuda75",
}

if __name__ == "__main__":
    print(get_env_name(verbose=True))
