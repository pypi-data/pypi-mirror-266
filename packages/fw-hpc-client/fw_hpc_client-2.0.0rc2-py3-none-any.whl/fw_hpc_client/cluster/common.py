import copy
import os
import stat

import flywheel
from jinja2 import Template

from ..util import frame, net


class Common:
    """The common class holds functionality that you should not override.

    These implementations are subject to change as Flywheel changes.
    """

    config = None
    log = None
    fw = None

    # Populated on demand
    uid_whitelist = None

    def __init__(self, config, log):
        """Constructor for Common elements.

        Args:
            config (defn.Config): The configuration for the application.
            log (frame.Log): The logger.
        """

        self.config = config
        self.log = log
        self.fw = config.sdk

    def confirm_config_defaults_loaded(self):
        """
        Confirm that the sub-class has filled out the config settings.
        """

        optional_keys = [
            "command",
            "command_script_stdin",
            "script",
            "script_executable",
        ]

        for key in optional_keys:
            if self.config.cast.dict()[key] is None:
                frame.fatal(
                    f"config.cast. {key} not populated. "
                    "Modify your set_config_defaults implementation."
                )

    def get_jobs(self):
        """Fetch matching jobs to be cast.

        Returns:
            list: The matching jobs.
        """

        search = net.prepare_search(self.config.cast)
        filter_tags = self.config.cast.filter_tags

        cursor = None

        try:
            jobs = []
            cursor = self.fw.jobs.iter_find(filter=search)

            for job in cursor:
                # If the filter_tags is set, only include jobs that have all of the tags
                if filter_tags is not None:
                    if not net.job_has_all_tags(job, filter_tags):
                        continue

                jobs.append(job)

        except flywheel.rest.ApiException as e:
            frame.fw_fatal("Could not fetch FW jobs.", e)

        return jobs

    def determine_singularity_settings(self, job):
        """
        These config values do not vary by cluster type.

        Keeping this func in Common thus avoids copy-pasting problems.

        Args:
            job (flywheel.Job): The job.

        Returns:
            tuple: The singularity debug and write settings.
        """

        s_debug = job.config.get("singularity-debug", False)
        s_write = job.config.get("singularity-writable", False)

        if type(s_debug) is not bool:
            self.log.warn("Invalid singularity-debug type on job. Ignoring.")
            s_debug = False

        if type(s_write) is not bool:
            self.log.warn("Invalid singularity-writable type on job. Ignoring.")
            s_write = False

        return s_debug, s_write

    def load_whitelist(self):
        """
        Load the user whitelist, if enabled.
        """

        if self.uid_whitelist is None and self.config.cast.group_whitelist:
            self.log.debug("Loading whitelist...")
            t = frame.timer()

            try:
                self.uid_whitelist = net.load_user_id_whitelist(self.fw)
            except flywheel.rest.ApiException as e:
                frame.fw_fatal("Could not fetch HPC whitelist.", e)

            if self.uid_whitelist is not None and len(self.uid_whitelist) == 0:
                self.log.warn("HPC whitelist is active, but empty! No jobs will run.")

            ms = str(frame.elapsed_ms(t))
            self.log.debug("Loaded whitelist in " + ms + " ms.")

    def reject_whitelist(self, job, job_user):
        """Reject a job due to whitelist mistmatch.

        Args:
            job (flywheel.Job): The job.
            job_user (str): The user ID.

        Exceptions:
            flywheel.rest.ApiException: If the API call fails.
        """

        # Write a short rejection to stderr
        msg = "User " + str(job_user) + " is not on the HPC whitelist."
        self.log.warn(msg + " Dropping job.")

        # Write a long rejection to FW job logs
        msg += (
            "\nOnly white-listed users are allowed to run Gears on the HPC at this time."
            "\n"
            f"For more information please contact {self.config.cast.admin_contact_email}"
        )

        t = frame.timer()

        try:
            net.add_system_log(self.fw, job.id, msg)
            net.cancel_job(self.fw, job.id)
        except flywheel.rest.ApiException as e:
            frame.fw_fatal("Could not cancel FW job.", e)

        ms = str(frame.elapsed_ms(t))
        self.log.debug("Rejected job " + job.id + " in " + ms + " ms.")

    def check_whitelist(self, job):
        """
        Check if a job should run based on the user whitelist, if enabled.

        Return true IFF the job should run.

        Args:
            job (flywheel.Job): The job.

        Returns:
            bool: True if the job should run.
        """

        if self.config.cast.group_whitelist:
            self.load_whitelist()

            # Job origins are not guaranteed to exist, and are not always humans
            if job.origin is not None and job.origin.type == "user":
                job_user = job.origin.id

                if job_user not in self.uid_whitelist:
                    self.reject_whitelist(job, job_user)

                    return False

        return True

    def run_templating(self, job, values):
        """Generate the script and command templates.

        Args:
            job (flywheel.Job): The job.
            values (defn.Values): The values.

        Returns:
            tuple: The script text and command.
        """

        self.log.debug("Handling job " + job.id)

        if self.config.cast.show_script_template_values:
            self.log.debug("Template values:\n" + frame.pretty_json(values.dict()))

        # Generate the script
        script_text = Template(self.config.cast.script).render(values)

        if self.config.cast.show_script_template_result:
            self.log.debug("Script contents:\n" + script_text)

        # Write the script to disk
        handle = open(values.script_path, "w")
        handle.write(script_text)
        handle.close()

        if self.config.cast.script_executable:
            st = os.stat(values.script_path)
            os.chmod(values.script_path, st.st_mode | stat.S_IEXEC)

        # Generate the command
        command = copy.deepcopy(self.config.cast.command)
        command = list(map(lambda x: Template(x).render(values), command))

        if self.config.cast.dry_run:
            command.insert(0, "echo")

        if self.config.cast.show_commnd_template_result:
            self.log.debug("Command to execute:\n" + frame.pretty_json(command))

        return script_text, command

    def report_results(self, start, jobs_launched, jobs_skipped, jobs_rejected):
        """Record total runtime and print useful results.

        Args:
            start (float): The start time.
            jobs_launched (int): The number of jobs launched.
            jobs_skipped (int): The number of jobs skipped.
            jobs_rejected (int): The number of jobs rejected.
        """

        ms = str(frame.elapsed_ms(start))
        msg = ""

        if (jobs_launched + jobs_rejected + jobs_skipped) == 0:
            msg += "No jobs to handle."

        else:
            msg = "Launched " + str(jobs_launched)

            if jobs_rejected > 0:
                msg += ", rejected " + str(jobs_rejected)

            if jobs_skipped > 0:
                msg += ", skipped " + str(jobs_skipped)

            msg += " jobs."

        msg += " Runtime: " + ms + " ms."

        self.log.info(msg)
