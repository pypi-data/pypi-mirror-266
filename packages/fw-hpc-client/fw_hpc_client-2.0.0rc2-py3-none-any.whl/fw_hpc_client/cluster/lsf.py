import re

from ..util import defn

from .base import Base

SCRIPT_TEMPLATE = """#!/bin/bash

#BSUB -P flywheel
#BSUB -J fw-{{job.fw_id}}
#BSUB -n {{job.cpu}}
#BSUB -R {{job.ram}}
#BSUB -oo {{script_log_path}}
#BSUB -eo {{script_log_path}}

set -euo pipefail

source "{{cast_path}}/settings/credentials.sh"
cd "{{engine_run_path}}"

set -x
./engine run --single-job {{job.fw_id}}

"""

DEFAULT_RAM = "rusage[mem=4000]"
DEFAULT_CPU_COUNT = "1"


class Lsf(Base):
    """The LSF Scheduler."""

    def __init__(self, config, log):
        """Initializes a new instance of the LSF Scheduler.

        Args:
            config (util.config.Config): The configuration settings.
            log (util.log.Log): The log.
        """
        super().__init__(config, log)
        self.default_ram = DEFAULT_RAM
        self.default_cpu_count = DEFAULT_CPU_COUNT

    def set_config_defaults(self):
        """Set the default configuration settings for the LSF Scheduler."""
        c = self.config.cast

        if c.command is None:
            c.command = [
                "bsub",
                "-P",
                "flywheel",
                "-J",
                "fw-{{job.fw_id}}",
                "-oo",
                "{{script_log_path}}",
                "-eo",
                "{{script_log_path}}",
            ]

        # Unlike qsub, bsub does not like being passed the file as a param.
        # It will superficially appear to work, but actually drop some of its parameters.
        if c.command_script_stdin is None:
            c.command_script_stdin = True

        if c.script is None:
            c.script = SCRIPT_TEMPLATE

        if c.script_executable is None:
            c.script_executable = False

    def determine_job_settings(self, job):
        """Determines the job settings for the LSF Scheduler.

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
        """Formats the scheduler RAM and CPU settings for the LSF Scheduler.

        Args:
            scheduler_ram (str): The scheduler RAM setting.
            scheduler_cpu (str): The scheduler CPU setting.

        Returns:
            tuple: The formatted scheduler RAM and CPU settings.
        """
        if not scheduler_ram:
            scheduler_ram = self.default_ram
        if not scheduler_cpu:
            scheduler_cpu = self.default_cpu_count

        # Force alphanum, with some extra chars for ram syntax
        ram = re.sub(r"[^a-zA-Z0-9\[\]\=]+", "", str(scheduler_ram))
        cpu = re.sub(r"\W+", "", str(scheduler_cpu))

        return ram, cpu
