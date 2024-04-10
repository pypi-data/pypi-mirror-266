from ..util import frame

from .base import Base
from .lsf import Lsf
from .sge import Sge
from .slurm import Slurm


def run_cast(start, config, log):
    """Look up a cluster implementation, and run a single cast sweep.

    Args:
        start (datetime): Date and time of the start of the cast.
        config (defn.Config): Cast configuration, paths, and environment variables.
        log (module): Logging module.
    """

    if config.cast.cluster == "base":
        Base(config, log).handle_all(start)

    elif config.cast.cluster == "lsf":
        Lsf(config, log).handle_all(start)

    elif config.cast.cluster == "sge":
        Sge(config, log).handle_all(start)

    elif config.cast.cluster == "slurm":
        Slurm(config, log).handle_all(start)

    else:
        frame.fatal("No such cluster type: " + config.cast.cluster)


def from_scheduler(config, log, scheduler_type: str):
    """Acts as a factory method for instantiating a scheduler object.

    Args:
        (defn.Config): Cast configuration, paths, and environment variables.
        log (module): Logging module.
        scheduler_type (str): The type of scheduler to instantiate.

    Returns:
        Base: The type of scheduler that is instantiated.
    """

    if scheduler_type == "base":
        return Base(config, log)

    elif scheduler_type == "lsf":
        return Lsf(config, log)

    elif scheduler_type == "sge":
        return Sge(config, log)

    elif scheduler_type == "slurm":
        return Slurm(config, log)

    else:
        frame.fatal("No such cluster/scheduler type: " + config.cast.cluster)
