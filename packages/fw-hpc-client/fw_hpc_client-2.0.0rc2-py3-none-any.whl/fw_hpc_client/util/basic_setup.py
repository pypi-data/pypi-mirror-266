from pathlib import Path
import shutil
import logging

log = logging.getLogger(__name__)


def setup_directories(default_folder: Path = Path.cwd()):
    # Path to the settings directory
    settings_dir = default_folder / Path("settings")
    settings_dir.mkdir(parents=True, exist_ok=True)

    # Create directories
    (default_folder / "logs/queue").mkdir(parents=True, exist_ok=True)
    (default_folder / "logs/generated").mkdir(parents=True, exist_ok=True)
    (default_folder / "logs/temp").mkdir(parents=True, exist_ok=True)

    # Create symbolic link to /dev/null
    if not (default_folder / "logs/temp/log.json").exists():
        (default_folder / "logs/temp/log.json").symlink_to("/dev/null")

    # If the settings_dir is already populated, log it and return
    if list(settings_dir.glob("*")):
        log.info(
            "Settings directory already has files exists, skipping initialization."
        )
        log.info(
            "If you want to reset the settings directory, remove those files or "
            "run `hpc-client reset`."
        )
        return

    # Copy templates to new folder for modification
    for file in (Path(__file__).parents[1] / "assets/").iterdir():
        print(f"Copying {file.name} to {settings_dir/file.name}")
        shutil.copy(file, settings_dir / file.name)


def reset_directories(default_folder: Path = Path.cwd()):
    print("All configuration settings will be lost.")
    print("Are you sure you want to reset the settings directory? (yes/no).")
    response = input()
    if response.lower() != "yes":
        print("Reset cancelled.")
        return
    # Path to the settings directory
    settings_dir = default_folder / Path("settings")
    log_dir = default_folder / "logs"
    # Remove directories
    shutil.rmtree(settings_dir, ignore_errors=True)
    shutil.rmtree(log_dir, ignore_errors=True)
