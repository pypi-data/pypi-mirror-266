import os
import tomllib

import fuzzyfinder
import consolecmdtools as cct
import consoleiotools as cit

from . import Trackfile


__version__ = '0.0.2'


def get_configs(config_path: str = "filetrack.toml") -> dict:
    """Get configurations from the config file.

    Args:
        config_path (str, optional): The path or the file name of the config file. Defaults to "filetrack.toml".

    Returns:
        dict: The configurations.

    Raises:
        FileNotFoundError: If the config file is not found.
    """
    if os.path.isfile(config_path):
        with open(config_path, "rb") as fl:
            config = tomllib.load(fl)
        return config
    raise FileNotFoundError(f"Config file not found at {config_path}")


def diffs(old_ft: Trackfile.Trackfile, new_ft: Trackfile.Trackfile) -> bool:
    """Check if there are any differences between the old and new trackfiles.

    Args:
        old_ft (Filetrack.Trackfile): The old trackfile.
        new_ft (Filetrack.Trackfile): The new trackfile.

    Returns:
        bool: True if there are differences, False otherwise.
    """
    pres = {
        "delete": "[red]-[/]",
        "add": "[green]+[/]",
        "move_from": "[blue]-[/]",
        "move_to": "[blue]+[/]",
    }
    if not old_ft.trackings and not new_ft.trackings:
        return False
    entries_deleted, entries_added = old_ft.compare_with(new_ft)
    if not entries_deleted and not entries_added:
        cit.info("No changes")
        return False
    cit.info("Changes since last time: ✍️")
    for filename in entries_deleted:
        if entries_added:
            fuzzy = list(fuzzyfinder.fuzzyfinder(filename, entries_added))
            if len(fuzzy) > 0:
                cit.echo(f"{pres['move_from']} {filename}")
                cit.echo(f"{pres['move_to']} {fuzzy[0]}")
                entries_added.remove(fuzzy[0])
            else:
                cit.echo(f"{pres['delete']} {filename}")
    for filename in entries_added:
        cit.echo(f"{pres['add']} {filename}")
    return True


def run_filetrack(config_path: str = "filetrack.toml", target_dir: str = os.getcwd(), target_exts: list[str] = ["mp3", "m4a"], trackfile_dir: str = os.getcwd(), trackfile_format: str = "json", hash_mode: str = "CRC32", group_by: str = ""):
    """Run filetrack

    Args:
        config_path (str, optional): The path or the file name of the config file. Defaults to "filetrack.toml".
        target_dir (str): The directory path of the files to be tracked. Default is the current working folder.
        target_exts (list[str], optional): The target extensions. Defaults to TARGET_EXTS.
        trackfile_dir (str): The directory path of the trackfile. Default is the current working folder.
        trackfile_format (str, optional): The output format. Defaults to "json". Options: "json", "toml".
        hash_mode (str, optional): The hash mode. Defaults to "CRC32". Options: "CRC32", "MD5", "NAME", "PATH", "MTIME".
        group_by (str, optional): Group by. Defaults to "". Options: "host", "os", "".
    """
    cit.rule("▶ [yellow]Run Filetrack")
    configs = get_configs(config_path)
    if target_configs := configs.get("target"):
        target_dir = target_configs.get("dir") or target_dir
        target_exts = target_configs.get("exts") or target_exts
    if trackfile_configs := configs.get("trackfile"):
        trackfile_dir = trackfile_configs.get("dir") or trackfile_dir
        trackfile_format = trackfile_configs.get("format") or trackfile_format
        hash_mode = trackfile_configs.get("hash_mode") or hash_mode
        group_by = trackfile_configs.get("group_by") or group_by
        trackfile_prefix = trackfile_configs.get("prefix") or "FileTrack-"
    target_dir = cct.get_path(target_dir)
    trackfile_dir = cct.get_path(trackfile_dir)
    old_ft = Trackfile.Trackfile(trackfile_dir=trackfile_dir, prefix=trackfile_prefix, format=trackfile_format, group_by=group_by)
    new_ft = Trackfile.Trackfile(trackfile_dir=trackfile_dir, prefix=trackfile_prefix, format=trackfile_format, group_by=group_by)
    cit.info(f"Version: {__version__}. (TrackFile version: {Trackfile.Trackfile.__version__})")
    cit.info(f"Trackfile Dir: 📂 [u]{trackfile_dir}[/]")
    cit.info(f"Trackfile Format: 📜 {trackfile_format}")
    cit.info(f"Target Dir: 📂 [u]{target_dir}[/]")
    cit.info(f"Target Extensions: 📜 {target_exts}")
    cit.info(f"Hash Mode: 🧮 {hash_mode}")
    if group_by == "host":
        cit.info(f"Group by hostname: 💻 {new_ft.hostname}")
    elif group_by == "os":
        cit.info(f"Group by OS: 🖥️ {os.name}")
    # fill trackings
    old_ft.from_file(old_ft.latest)
    new_ft.generate(target_dir, target_exts, hash_mode)
    if not old_ft.trackings or diffs(old_ft, new_ft):
        cit.info("[Done]")
        new_ft.to_file()
        new_ft.cleanup_outdated_trackfiles()
    cit.pause()
