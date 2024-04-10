import inspect
import os
import subprocess
import sys
from abc import abstractmethod

import flywheel

from ..util import defn, frame

from .common import Common

SCRIPT_TEMPLATE = (
    inspect.cleandoc(
        """#!/bin/bash

echo "This is an example script. Hello world!!"
echo
echo "The FW job ID is {{job.fw_id}}"
echo
{%- if job.cpu -%}echo "Job CPU is set to {{job.cpu}}"{%- endif %}
{%- if job.ram -%}echo "Job RAM is set to {{job.ram}}"{%- endif %}

echo
echo "This file will be written to"
echo "{{script_path}}"

echo "The log will be written to"
echo "{{script_log_path}}"

"""
    )
    + "\n\n"
)

# These are valid tag prefixes for the scheduler settings in lower case
# Tagging a job with one of these--followed by the setting--will set the job's
# scheduler settings to the value of the tag.
VALID_CPU_TAGS = ["cpu=", "cpus=", "scheduler_cpu="]
VALID_RAM_TAGS = ["ram=", "scheduler_ram=", "ram-gb="]
VALID_TAGS = {
    "scheduler_cpu": VALID_CPU_TAGS,
    "scheduler_ram": VALID_RAM_TAGS,
}


class Base(Common):
    """
    BaseCluster defines methods that you may need to override.
    """

    def set_config_defaults(self):
        """
        Use this function to set cluster defaults.
        These will be used when the corresponding YAML value is not present.
        """

        c = self.config.cast

        if c.command is None:
            c.command = ["echo", "{{script_path}}"]

        if c.command_script_stdin is None:
            c.command_script_stdin = False

        if c.script is None:
            c.script = SCRIPT_TEMPLATE

        if c.script_executable is None:
            c.script_executable = False

    def determine_job_settings(self, job):
        """Parse job settings out of a FW job object.

        You will need to override this for cluster-specific config naming. This
        is also your opportunity to apply defaults for users who forget to
        specify the relevant options in their gear's manifest.

        Important: Security-sensitive.
        These values will be passed to command and script templating.

        Args:
            job (flywheel.JobListEntry): The job to cast.

        Returns:
            defn.JobSettings: The settings for this job.
        """

        # These value names are not cluster-specific.
        # Use this function call when overriding.
        s_debug, s_write = self.determine_singularity_settings(job)

        # For this Base impl, no extra settings are defined.
        # Your cluster type might support these; override this function and add them.

        return defn.JobSettings(
            fw_id=str(job.id),
            singularity_debug=s_debug,
            singularity_writable=s_write,
            ram=None,
            cpu=None,
        )

    def determine_script_patch(self, job):
        """Determine where the HPC script file will be placed.

        You probably do not need to change this.

        Args:
            job (flywheel.JobListEntry): The job to cast.

        Returns:
            str: The path to the generated script file.
        """

        return self.config.paths.scripts_path / f"job-{job.id}.sh"

    def determine_log_patch(self, job):
        """Determine where the HPC log file will be placed.

        You probably do not need to change this.

        Args:
            job (flywheel.JobListEntry): The job to cast.

        Returns:
            str: The path to the generated log file.
        """

        return self.config.paths.hpc_logs_path / f"job-{job.id}.txt"

    def execute(self, command, script_path):
        """Execute the scheduler command.

        Args:
            command (list): A list of strings that form the command to execute.
            script_path (Pathlike): The path to the generated script file.
        """
        # Prevent out-of-order log entries
        sys.stdout.flush()
        sys.stderr.flush()

        # Execute
        if not self.config.cast.command_script_stdin:
            subprocess.run(command, check=True)
        else:
            # Some commands, such as bsub, prefer to be fed via stdin
            with open(script_path, "r") as handle:
                subprocess.run(command, stdin=handle, check=True)

    def handle_each(self, job, values):
        """Handle a single job.

        Override if the general pattern of "generate script, run command" does not work for your cluster type.

        Args:
            job (flywheel.JobListEntry): The job to cast.
            values (defn.ScriptTemplate): The templating values for the script.

        Exceptions:
            FileNotFoundError: If the script file is not found.
        """

        _, command = self.run_templating(job, values)

        self.log.info("Casting job to HPC...")
        t = frame.timer()

        try:
            self.execute(command, values.script_path)

        except (FileNotFoundError, subprocess.SubprocessError) as e:
            self.log.critical("Error executing command. Exec error follows:")
            frame.fatal(e)

        ms = str(frame.elapsed_ms(t))
        self.log.debug("Casted job in " + ms + " ms.")

    def handle_all(self, start):
        """Main handler loop.

        Args:
            start (datetime): The start time of the casting process.
        """

        # Note: some functions are defined in BaseCluster:
        #
        #   determine_job_settings
        #   determine_script_patch
        #   handle_each
        #   set_config_defaults
        #
        # As such, using a Common class directly is invalid.

        # Load any cluster-specific settings
        self.set_config_defaults()
        self.confirm_config_defaults_loaded()

        # Load candidate jobs into memory
        self.log.debug("Looking for jobs to cast...")
        t = frame.timer()
        jobs = self.get_jobs()
        ms = str(frame.elapsed_ms(t))
        count = str(len(jobs))
        self.log.debug("Found " + count + " jobs in " + ms + " ms.")

        # Track results
        jobs_launched = 0
        jobs_skipped = 0
        jobs_rejected = 0

        # Invoke cluster-specific logic
        for job in jobs:
            # Cast uses the existence of a script file
            # to determine if a job should be cast.
            script_path = self.determine_script_patch(job)

            if os.path.exists(script_path):
                jobs_skipped += 1
                continue

            if not self.check_whitelist(job):
                jobs_rejected += 1
                continue

            # Collect information
            script_log_path = self.determine_log_patch(job)
            job_settings = self.determine_job_settings(job)

            # Prepare templating values
            values = defn.ScriptTemplate(
                job=job_settings,
                script_path=script_path,
                script_log_path=script_log_path,
                cast_path=self.config.paths.cast_path,
                engine_run_path=self.config.paths.engine_run_path,
            )

            # Job is fit to cast
            self.handle_each(job, values)
            jobs_launched += 1

        # Finish
        self.report_results(start, jobs_launched, jobs_skipped, jobs_rejected)

    def determine_ram_and_cpu_settings(self, job: flywheel.JobListEntry) -> (str, str):
        """Get scheduler ram and cpu settings based on the type of cluster/HPC scheduler.

        Args:
            job (flywheel.JobListEntry): The job to cast.

        Returns:
            (str, str): The scheduler ram and cpu settings.
        """
        # Update job config vars to support legacy ram and cpu settings
        job = self._check_legacy_ram_and_cpu_settings(job=job)

        # Set the dict variables we're checking
        settings = {"scheduler_ram": "", "scheduler_cpu": ""}
        self._determine_scheduler_settings(job=job, settings=settings)
        return self.format_scheduler_ram_and_cpu_settings(**settings)

    def _check_legacy_ram_and_cpu_settings(self, job: flywheel.JobListEntry):
        """
        Supports legacy ram and cpu settings for `slurm-ram` and `slurm-cpu`
        by setting the value of these to `scheduler_ram` and `scheduler_cpu`.

        These should be deprecated in next major release (3.0.0). Warn user
        to update their gears to `scheduler_ram` and `scheduler_cpu`.

        Args:
            job(flywheel.JobListEntry): The job to cast.

        Returns:
            flywheel.JobListEntry: The job with updated config settings.
        """
        # Check if these variables exist in the Flywheel job config. These
        # appear as strings, even if unset ('')
        if isinstance((job.config["config"]).get("slurm-ram"), str) or isinstance(
            (job.config["config"]).get("slurm-cpu"), str
        ):
            # ensure that supported ones aren't also defined.
            if isinstance(
                (job.config["config"]).get("scheduler_ram"), str
            ) or isinstance((job.config["config"]).get("scheduler_cpu"), str):
                raise ValueError(
                    "Legacy variables `slurm-ram` and `slurm-cpu` cannot exist"
                    "with `scheduler_ram` and `scheduler_cpu`. Please remove "
                    "legacy settings."
                )

            # transform legacy vars to supported ones
            (job.config["config"])["scheduler_ram"] = (job.config["config"]).get(
                "slurm-ram"
            )
            (job.config["config"])["scheduler_cpu"] = (job.config["config"]).get(
                "slurm-cpu"
            )

            self.log.warning(
                "Support for variables `slurm-ram` and `slurm-cpu` will be "
                "deprecated in future releases. Please update these to"
                "`scheduler_ram` and `scheduler_cpu`. You cannot have both "
                "legacy and current names defined within the same gear job "
                "config."
            )
            return job
        else:
            return job

    def _determine_scheduler_settings(self, job: flywheel.JobListEntry, settings: dict):
        """
        A template method for checking a scheduler setting(s).

        This should be used in other methods that follow this logic:

        1. Check if the setting is in the Flywheel gear config.
        2. If not, check if the settings are in the job tags.
        3. If not, check if the setting is in the `settings/cast.yml` file.
        4. If not, then set it to default values, typically set by a concrete
                cluster/scheduler object's formatting method.

        As an example, see `Base.determine_ram_and_cpu_settings().

        Args:
            job (flywheel.JobListEntry): The job to cast.
            settings (dict): The settings to check.
                        Each key represents a scheduler/cluster setting that should be
                        checked in the processed described above. The default key should
                        be something that represents an empty object (e.g., '', or None).

        Returns:
            dict: The settings with updated values.
        """

        for setting in settings.keys():
            # check if the Flywheel gear job has any scheduler settings
            self.log.info("Checking gear job for `%s` setting.")
            if setting_value := (job.config["config"]).get(setting):
                settings[setting] = setting_value
                self.log.info(
                    "Flywheel gear job `%s` = '%s'" % (setting, settings[setting])
                )
                continue

            # No setting in gear job; check in the tags of the job:
            self.log.info(
                "No `%s` setting configuration found in Flywheel gear job. "
                "Checking job tags." % setting
            )

            valid_tag = None
            valid_setting = None
            if valid_tag := self._get_valid_settings_tag(job, setting):
                valid_setting = self._validate_settings_tag(valid_tag, setting)

            if valid_tag and valid_setting:
                settings[setting] = valid_setting
                self.log.info("Job tag `%s` = '%s'" % (setting, settings[setting]))
                continue

            # If it doesn't, get these from the fw-cast/settings/cast.yml file.
            cast = self.config.cast
            self.log.info(
                "No `%s` setting found in Flywheel gear job. Checking "
                "`settings/cast.yml` file" % setting
            )
            settings[setting] = getattr(cast, setting)
            self.log.info("cast.yml %s = '%s'" % (setting, settings[setting]))

            # If these are still 'None' or '', the default level will be set by
            # the scheduler formatter.
            self.log.info(
                "No `%s` setting found in Flywheel cast.yml. Setting "
                "to scheduler default." % setting
            )
        return settings

    def _get_valid_settings_tag(self, job, setting):
        """Get the first valid settings tag from a job's tags.

        Args:
            job (flywheel.Job): The job.
            setting (str): The setting to use to evaluate valid tags.

        Returns:
            str: The first valid tag, or None if none are found.
        """
        valid_tags = VALID_TAGS[setting]
        for val_tag in valid_tags:
            for tag in job.tags:
                # Test for valid tag forms in the lower case version of the job tag
                if val_tag in tag.lower():
                    return tag

        return None

    def _validate_settings_tag(self, tag, settings_tag):
        """Validate a settings tag.

        NOTE: This method is written for validating Slurm cpu/ram settings. It should be
        overridden for other cluster/scheduler objects.


        Args:
            tag (str): The tag to validate.
            settings_tag (str): The settings tag.

        Returns:
            bool: True if the tag is valid, False otherwise.
        """
        if settings_tag == "scheduler_cpu":
            cpu = tag.split("=")[-1]
            if not cpu.isnumeric() or int(cpu) < 1:
                self.log.warning(
                    "CPU setting must be a positive integer. "
                    "Setting to scheduler default."
                )
                cpu = None
            return cpu
        elif settings_tag == "scheduler_ram":
            ram = tag.split("=")[-1]
            if not ram.lower().endswith("g"):
                if ram.isnumeric():
                    self.log.warning(
                        "Assuming Numeric value for RAM is in gigabytes (G)."
                    )
                    ram += "G"
                else:  # if it's not numeric, it's an invalid setting
                    self.log.warning(
                        "RAM setting must be in gigabytes (G). "
                        "Setting to scheduler default."
                    )
                    ram = None
                return ram

            if not ram[:-1].isnumeric():
                self.log.warning(
                    "RAM setting must be in gigabytes (G). "
                    "Setting to scheduler default."
                )
                ram = None
            return ram
        else:
            self.log.warning("Invalid settings tag. Setting to scheduler default.")
            return None

    def determine_job_priority(self, job: flywheel.JobListEntry):
        """Determine the priority of the job to pass on to the scheduler.

        Args:
            job (flywheel.JobListEntry): The Flywheel Job.

        Returns:
            int or None: The mapped integer representation of the job priority
        """
        # Get the flywheel job priority
        fw_priority = job.reload().priority
        # Set the default scheduler priority to None
        scheduler_priority = None

        if self.config.cast.map_job_priority:
            # Check if the priority is in the map
            if fw_priority in self.config.cast.fw_priority_map:
                scheduler_priority = self.config.cast.fw_priority_map[fw_priority]

        return scheduler_priority

    @abstractmethod
    def format_scheduler_ram_and_cpu_settings(
        self, scheduler_ram: str, scheduler_cpu: str
    ) -> (str, str):
        """Format the scheduler ram and cpu settings for the cluster.

        This is an abstract method and should never be called directly. It should
        be overridden by a concrete cluster/scheduler object.

        Args:
            scheduler_ram (str): RAM setting for the cluster.
            scheduler_cpu (str): CPU setting for the cluster.

        Raises:
            NotImplementedError: Error raised if the method is not overridden.
        """
        raise NotImplementedError
