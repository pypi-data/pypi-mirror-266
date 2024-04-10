import re

from ..util import defn
from .base import Base

SCRIPT_TEMPLATE = """#!/bin/bash

#SBATCH --job-name=fw-{{job.fw_id}}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={{job.cpu}}
#SBATCH --mem-per-cpu={{job.ram}}
#SBATCH --output {{script_log_path}}

set -euo pipefail

source "{{cast_path}}/settings/credentials.sh"
cd "{{engine_run_path}}"

set -x
srun ./engine run --single-job {{job.fw_id}}

"""

DEFAULT_RAM = "4G"
DEFAULT_CPU_COUNT = "1"
DEFAULT_GPU_COUNT = "1"


class Slurm(Base):
    """The Slurm Scheduler."""

    def __init__(self, config, log):
        """Initializes a new instance of the LSF Scheduler.

        Args:
            config (util.config.Config): The configuration settings.
            log (util.log.Log): The log.
        """
        super().__init__(config, log)
        self.default_ram = DEFAULT_RAM
        self.default_cpu_count = DEFAULT_CPU_COUNT
        self.default_gpu_count = DEFAULT_GPU_COUNT

    def set_config_defaults(self):
        """Set the default configuration settings for the Slurm Scheduler."""
        c = self.config.cast

        if c.command is None:
            c.command = ["sbatch", "{{script_path}}"]

        if c.command_script_stdin is None:
            c.command_script_stdin = False

        if c.script is None:
            c.script = SCRIPT_TEMPLATE

        if c.script_executable is None:
            c.script_executable = True

    def determine_job_settings(self, job):
        """Determines the job settings for the Slurm Scheduler.

        Args:
            job (flywheel.JobEntry): The job to determine the settings for.

        Returns:
            defn.JobSettings: The job settings.
        """
        s_debug, s_write = self.determine_singularity_settings(job)

        ram, cpu = self.determine_ram_and_cpu_settings(job=job)

        priority = self.determine_job_priority(job)

        # This setting can be modified to account for multiple GPUs per node
        # For now, we will assume that a job will only request one GPU
        if "gpu" in job.tags:
            gpu = "1"
        else:
            gpu = None

        return defn.JobSettings(
            fw_id=str(job.id),
            singularity_debug=s_debug,
            singularity_writable=s_write,
            ram=ram,
            cpu=cpu,
            gpu=gpu,
            priority=priority,
        )

    def format_scheduler_ram_and_cpu_settings(
        self, scheduler_ram: str, scheduler_cpu: str
    ) -> (str, str):
        """Formats the scheduler ram and cpu settings for the Slurm Scheduler.

        Args:
            scheduler_ram (str): The scheduler ram setting.
            scheduler_cpu (str): The scheduler cpu setting.

        Returns:
            tuple: The formatted scheduler ram and cpu settings.
        """
        if not scheduler_ram:
            scheduler_ram = "4G"
        if not scheduler_cpu:
            scheduler_cpu = "1"
        # Force string and alphanum
        ram = re.sub(r"\W+", "", str(scheduler_ram))
        cpu = re.sub(r"\W+", "", str(scheduler_cpu))
        return ram, cpu
