import argparse
import json
import logging
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path
import flywheel
import requests
import yaml

from . import defn
from .basic_setup import reset_directories, setup_directories

# Suppress (some) FW SDK version spam
logging.getLogger("Flywheel").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

# Slightly less of an eyesore: log15 strings
logging.addLevelName(logging.CRITICAL, "CRIT")
logging.addLevelName(logging.ERROR, "EROR")
logging.addLevelName(logging.WARNING, "WARN")
logging.addLevelName(logging.INFO, "INFO")
logging.addLevelName(logging.DEBUG, "DBUG")

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
    # This level could be configurable.
    level=logging.DEBUG,
)

log = logging


def fatal(*args):
    """Log a fatal error and exit the program."""
    log.critical(*args)
    log.critical("Exiting.")
    sys.exit(1)


def fw_fatal(msg, e):
    """Log a critical error and exit the program.

    Args:
        msg (str): Error message
        e (error): Error object
    """
    log.critical(msg + " HTTP error follows:")
    fatal(e)


def pretty_json(obj):
    """Create a pretty-printed JSON string from an object.

    Args:
        obj (dict): The dictionary to be converted to a JSON string.

    Returns:
        str: JSON string.
    """
    return json.dumps(obj, indent=4, sort_keys=True, default=str)


def timer():
    """A simple timer function.

    Returns:
        datetime: The current date and time.
    """
    return datetime.now()


def elapsed_ms(start):
    """The number of milliseconds that have elapsed since the start time.
    Args:
        start (datetime): The start time to measure from.

    Returns:
        int: The number of milliseconds that have elapsed since the start time.
    """
    elapsed = datetime.now() - start

    return int(elapsed.total_seconds() * 1000)


def check_paths(base_folder):
    """Determine and check the various paths needed by the application.

    Args:
        base_folder (Pathlike): The base folder of the application.

    Returns:
        defn.Paths: The collection of paths used by the application.
    """

    p = defn.Paths(
        cast_path=base_folder,
        yaml_path=base_folder / "settings/cast.yml",
        scripts_path=base_folder / "logs/generated",
        hpc_logs_path=base_folder / "logs/queue",
        engine_run_path=base_folder / "logs/temp",
    )

    for path in [
        p.cast_path,
        p.yaml_path,
        p.scripts_path,
        p.hpc_logs_path,
        p.engine_run_path,
    ]:
        if not os.path.exists(path):
            fatal("Path %s is missing; run `hpc-client setup`", path)

    return p


def load_yaml_settings(yaml_path):
    """Parse cast.yml into a pydantic struct.

    Args:
        yaml_path (Pathlike): Path to the cast.yml file.

    Returns:
        dict: Dictionary representation of the instantiated defn.ConfigFile object.
    """
    with open(yaml_path) as handler:
        raw_map = yaml.full_load(handler)

    result = defn.ConfigFile.parse_obj(raw_map)

    return result


def load_env_settings():
    """Load sensitive settings that were sourced from credentials.sh

    Returns:
        defn.CredentialEnv: Credentials for the application.
    """

    return defn.CredentialEnv(
        host=os.environ.get("SCITRAN_RUNTIME_HOST", "localhost"),
        port=int(os.environ.get("SCITRAN_RUNTIME_PORT", 443)),
        credential=os.environ.get("SCITRAN_CORE_DRONE_SECRET", "changeme"),
    )


def prepare_config(args):
    """Prepare the configuration for the application.

    Args:
        args (Namespace): The namespace of parsed command-line arguments.

    Returns:
        defn.Config: The configuration for the application.
    """
    paths = check_paths(args.folder)
    cast = load_yaml_settings(paths.yaml_path).cast
    creds = load_env_settings()

    return defn.Config(
        cast=cast,
        paths=paths,
        creds=creds,
    )


def create_client(creds):
    """Create the Drone client for the Flywheel SDK.

    Args:
        creds (defn.CredentialEnv): Credentials for the application.

    Returns:
        flywheel.drone_client: The Drone client for the Flywheel SDK.
    """
    client = None
    log.info("Connecting to FW...")
    t = timer()

    try:
        client = flywheel.drone_login.create_drone_client(
            creds.host, creds.credential, "python", "hpc queue", port=creds.port
        )
    except requests.exceptions.ConnectionError as e:
        fw_fatal("Could not connect to FW.", e)

    ms = str(elapsed_ms(t))
    log.debug("Connected in " + ms + " ms.")

    return client


def cmd_parser():
    """Build the command-line arg parser.

    Returns:
        ArgumentParser: Argument parser for the command-line arguments.
    """

    args = argparse.ArgumentParser()

    args.description = "Cast Flywheel jobs onto --> HPC"

    default_folder = Path.cwd()
    # The command to run is optional, but defaults to "run"
    args.add_argument(
        "command",
        type=str,
        nargs="?",
        help="Command to run (run, setup, reset)",
        default="run",
    )
    args.add_argument(
        "--folder",
        type=str,
        default=default_folder,
        help="Run, setup, or reset in a specific folder",
    )
    args.add_argument(
        "--show-config", action="store_true", help="JSON export: all configs"
    )

    return args


def run_cmd():
    """Run the cast command.

    Returns:
        defn.Config: The configuration for the application.
    """

    args = cmd_parser().parse_args()
    args.folder = Path(args.folder)

    if args.command == "setup":
        log.debug("Setup command detected.")
        setup_directories(args.folder)
        log.info("Setup complete.")
        sys.exit(0)

    if args.command == "reset":
        log.debug("Reset command detected.")
        reset_directories(args.folder)
        log.info("Reset complete.")
        sys.exit(0)

    if args.command != "run":
        fatal("Unknown command: " + args.command)
        sys.exit(1)

    config = prepare_config(args)

    # Print all settings in JSON
    if args.show_config:
        log.debug("Printing config")

        c = config.dict()
        del c["sdk"]
        c["creds"]["credential"] = "<omitted>"

        print(pretty_json(c))
        sys.exit(0)

    config.sdk = create_client(config.creds)

    return config
