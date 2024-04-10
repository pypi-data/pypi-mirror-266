from typing import Any, List, Optional

from pydantic import BaseModel, Field
from pathlib import Path


class ConfigFileCast(BaseModel):
    """Represents cast.yml cast settings"""

    cluster: str
    dry_run: bool
    scheduler_ram: Optional[str]
    scheduler_cpu: Optional[str]

    admin_contact_email: str
    group_whitelist: bool

    cast_on_tag: bool
    filter_tags: Optional[List[str]]

    cast_gear_whitelist: List[str] = Field(default_factory=list)

    show_script_template_values: bool
    show_script_template_result: bool
    show_commnd_template_result: bool

    command: Optional[List[str]]
    command_script_stdin: Optional[bool]

    script: Optional[str]
    script_executable: Optional[bool]

    use_hold_engine: bool

    map_job_priority: Optional[bool]
    fw_priority_map: Optional[dict]


class ConfigFile(BaseModel):
    """Represents a cast.yml settings file."""

    cast: ConfigFileCast


class Paths(BaseModel):
    """Represents various absolute paths used by the application."""

    cast_path: Path
    yaml_path: Path
    scripts_path: Path
    hpc_logs_path: Path
    engine_run_path: Path


class CredentialEnv(BaseModel):
    """Represents parsed environment variable settings."""

    host: str
    port: int
    credential: str


class Config(BaseModel):
    """Represents all cast settings as used by the application."""

    cast: ConfigFileCast
    paths: Paths
    creds: CredentialEnv
    sdk: Optional[Any]


class JobSettings(BaseModel):
    """Represents all HPC-relevant job settings.

    This is for creating and submitting the HPC job.
    """

    fw_id: str

    singularity_debug: bool
    singularity_writable: bool

    # The meaning of the following values vary by cluster type.
    ram: Optional[str]
    cpu: Optional[str]
    gpu: Optional[str]  # 0 or more GPUs

    # Job Priority
    priority: Optional[int]


class ScriptTemplate(BaseModel):
    """Represents the values available when templating an HPC script."""

    job: JobSettings
    script_path: Path
    script_log_path: Path
    cast_path: Path
    engine_run_path: Path


class FlywheelJob(BaseModel):
    """Represents some minimum properties for a flywheel job.

    Currently, it's only being used for testing, so only properties relevant for
    testing are needed.
    """

    config: dict
    destination: dict
    gear_id: str
    gear_info: dict
    id: str
    inputs: list
    origin: dict
    state: str
    tags: list
    priority: str
