import os
import pip
from subprocess import check_output, getoutput
from os.path import dirname
import fnmatch


def get_nvidia_driver_version():
    cmd = 'dpkg -l | grep nvidia-cuda-toolkit | tr -s " " | cut -d " " -f 3'
    return getoutput(cmd)

def get_os(sep=" "):
    cmd1 = "lsb_release -is"
    cmd2 = "lsb_release -rs"
    return sep.join([getoutput(cmd) for cmd in [cmd1, cmd2]])

def get_machine_name():
    cmd = "hostname"
    return getoutput(cmd)

def get_machine_type():
    cmd = "uname -m"
    return getoutput(cmd)


def get_site_packages():
    return dirname(dirname(pip.__file__))


def is_conda_activated():
    return bool(int(os.environ.get("CONDA_SHLVL", "0")))


def get_env_name(verbose=False):
    def verbose_print(msg):
        if verbose:
            print(msg)

    hostname = get_machine_name()
    slurm_partition = os.environ.get("SLURM_JOB_PARTITION", None)

    if slurm_partition is not None:
        verbose_print("Detected slurm partition %s" % slurm_partition)
        env = slurm_partitions_mappings.get(slurm_partition, None)
        if env is not None:
            verbose_print("Using environment %s" % env)
            return env
        else:
            verbose_print("No environment found for this partition")

    verbose_print("Trying individual nodes rules")
    for node_wildcard, env in nodes_mappings.items():
        if fnmatch.filter([hostname], node_wildcard):
            verbose_print("Match with %s -> %s" % (node_wildcard, env))
            return env

    verbose_print("Could not find any environment for %s" % hostname)
    return None





