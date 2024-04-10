import flywheel

from . import frame


def add_system_log(fw, job_id, msg):
    """Add a system log message to a FW job log.

    Args:
        fw (flywheel.Client): Flywheel client instance.
        job_id (str): The job ID.
        msg (str): The message to add to the job log.

    Returns:
        dict: The updated job object.
    """

    if not msg.endswith("\n"):
        msg = msg + "\n"

    return fw.add_job_logs(job_id, [{"fd": -1, "msg": msg + "\n"}])


def cancel_job(fw, job_id):
    """Cancel a FW job.

    Args:
        fw (flywheel.Client): Flywheel client instance.
        job_id (str): The job ID.
    """

    fw.modify_job(job_id, flywheel.Job(state="cancelled"))


def prepare_search(cast_config):
    """Prepare search syntax for use with the API.

    Args:
        cast_config (defn.Config): The configuration for the application.

    Returns:
        str: The search syntax.
    """

    search = ""

    use_hpc_tag = cast_config.cast_on_tag
    gears = cast_config.cast_gear_whitelist

    if cast_config.use_hold_engine:
        search += "state=running"
    else:
        search += "state=pending"

    # Check for invalid config
    if use_hpc_tag and len(gears) > 0:
        frame.fatal(
            "Invalid configuration - cast_on_tag and cast_gear_whitelist are mutually exclusive"
        )

    if not use_hpc_tag and len(gears) <= 0:
        frame.fatal(
            "Invalid configuration - one of cast_on_tag or cast_gear_whitelist must be in use"
        )

    # Search syntax ands conditions together
    if use_hpc_tag:
        search += ",tags=hpc"

    if len(gears) > 0:
        search += ",gear_info.name=~" + "|".join(gears)

    return search


from typing import List

def job_has_all_tags(job: flywheel.Job, filter_tags: List[str]) -> bool:
    """Check if a job has a set of tags.

    Args:
        job (flywheel.Job): The job.
        filter_tags (list): The tags to check for.

    Returns:
        bool: True if the job has all the tags, False otherwise.
    """
    job_tags = job.tags

    # Ensure that each filter tag is present in the job tags.
    for tag in filter_tags:
        if tag not in job_tags:
            # if not present, return False
            return False

    return True


def load_user_id_whitelist(fw):
    """Load user IDs from a FW-group-defined whitelist.

    Args:
        fw (flywheel.Client): Flywheel client instance.

    Returns:
        list: A list of user IDs with permissions to run jobs on the HPC.
    """
    # Group name is intentionally not configurable.
    group_name = "hpc-whitelist"
    group_perms = fw.get_group(group_name)["permissions"]

    return list(map(lambda x: x.id, group_perms))
