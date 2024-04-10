import re

from ..util import defn

from .base import Base

SCRIPT_TEMPLATE = """#!/usr/bin/env bash

#$ -j y
#$ -o {{script_log_path}}
#$ -S /bin/bash
#$ -l h_vmem={{job.ram}}
#$ -pe threaded {{job.cpu}}

set -euo pipefail

source "{{cast_path}}/settings/credentials.sh"
cd "{{engine_run_path}}"

set -x
./engine run --single-job {{job.fw_id}}

"""

DEFAULT_RAM = "4G"
DEFAULT_CPU_COUNT = "4-8"


class Sge(Base):
    """The SGE Scheduler."""

    def __init__(self, config, log):
        """Initializes a new instance of the SGE Scheduler.

        Args:
            config (util.config.Config): The configuration settings.
            log (util.log.Log): The log.
        """
        super().__init__(config, log)
        self.default_ram = DEFAULT_RAM
        self.default_cpu_count = DEFAULT_CPU_COUNT

    def set_config_defaults(self):
        """Set the default configuration settings for the SGE Scheduler."""
        c = self.config.cast

        if c.command is None:
            c.command = ["qsub", "{{script_path}}"]

        if c.command_script_stdin is None:
            c.command_script_stdin = False

        if c.script is None:
            c.script = SCRIPT_TEMPLATE

        if c.script_executable is None:
            c.script_executable = True

    def determine_job_settings(self, job):
        """Sets the job settings for the SGE Scheduler.

        Args:
            job (flywheel.JobEntry): The job to determine the settings for.

        Returns:
            defn.JobSettings: The job settings.
        """
        s_debug, s_write = self.determine_singularity_settings(job)

        ram, cpu = self.determine_ram_and_cpu_settings(job=job)

        return defn.JobSettings(
            fw_id=str(job.id),
            singularity_debug=s_debug,
            singularity_writable=s_write,
            ram=ram,
            cpu=cpu,
        )

    def format_scheduler_ram_and_cpu_settings(
        self, scheduler_ram: str, scheduler_cpu: str
    ) -> (str, str):
        """Formats the scheduler ram and cpu settings for the SGE Scheduler.

        Args:
            scheduler_ram (str): The scheduler ram setting.
            scheduler_cpu (str): The scheduler cpu setting.

        Returns:
            tuple: The formatted scheduler ram and cpu settings.
        """
        if not scheduler_ram:
            scheduler_ram = self.default_ram
        if not scheduler_cpu:
            scheduler_cpu = self.default_cpu_count

        # Force alphanum, with dashes for cpu range
        ram = re.sub(r"\W+", "", str(scheduler_ram))
        cpu = re.sub(r"[^a-zA-Z0-9\-]+", "", str(scheduler_cpu))

        return ram, cpu
