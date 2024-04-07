import os
import socket
import pathlib
import datetime

import consoleiotools as cit
import consolecmdtools as cct


class Trackfile:
    __version__ = "0.0.2"

    def __init__(self, trackfile_dir: str = os.getcwd(), prefix: str = "FileTrack-", format: str = "json", group_by: str = ""):
        """Initialize Trackfile object.

        Args:
            trackfile_dir (str): The directory path of the trackfile.
            prefix (str): The prefix of the trackfile.
            format (str): The output format. Options: "json", "toml".
            group_by (str): Group by. Default is "" meaning no group. Options: "host", "os", "".
        """
        self.prefix = prefix
        self.trackfile_dir = trackfile_dir
        self.format = format
        if self.format.upper() == "TOML":
            import tomlkit  # lazyload
            self.suffix = ".toml"
            self.formatter = tomlkit
        elif self.format.upper() == "JSON":
            import json  # lazyload
            self.suffix = ".json"
            self.formatter = json
        else:
            raise Exception(f"Output format `{self.format}` does not support")
        self.group_by = group_by
        self.trackings = {}

    def __str__(self) -> str:
        return self.path

    @property
    def hosts(self) -> list:
        """list of known hosts in trackfile_dir"""
        trackfile_list = []
        for filename in os.listdir(self.trackfile_dir):
            if filename.startswith(self.prefix) and filename.endswith(self.suffix):
                trackfile_list.append(filename.split("-")[2].split(".")[0])
        return sorted(list(set(trackfile_list)))

    @property
    def files(self) -> list:
        trackfile_list = []
        for filename in os.listdir(self.trackfile_dir):
            if filename.startswith(self.prefix) and filename.endswith(self.suffix):
                if self.group_by == "host" and (self.hostname not in filename):
                    continue
                trackfile_list.append(os.path.join(self.trackfile_dir, filename))
        return sorted(trackfile_list)

    @property
    def latest(self) -> str:
        if not self.files:
            return ""
        return self.files[-1]

    @property
    def group(self):
        match self.group_by:
            case "host":
                return self.hostname
            case "os":
                return os.name
            case "":
                return ""
            case _:
                cit.err(f"Unsupported group_by: {self.group_by}")
                cit.bye()

    @property
    def filename(self):
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{self.prefix}{now}{'-' if self.group else ''}{self.group}{self.suffix}"

    @property
    def path(self):
        return os.path.join(self.trackfile_dir, self.filename)

    def compare_with(self, trackfile: "Trackfile") -> tuple[list, list]:
        trackings_1 = set(self.trackings.items())
        trackings_2 = set(trackfile.trackings.items())
        return [filename for filename, filehash in trackings_1 - trackings_2], [filename for filename, filehash in trackings_2 - trackings_1]

    @property
    def hostname(self) -> str:
        """Get hostname and check if hostname is new."""
        host = socket.gethostname().replace("-", "").replace(".", "")  # default hostname
        if host not in self.hosts:
            cit.warn(f"New hostname `{host}` detected.")
        return host

    @cit.as_session("Cleanup Outdated TrackFiles")
    def cleanup_outdated_trackfiles(self):
        if len(self.files) > 1:
            old_trackfiles = self.latest
            cit.ask("Cleanup old TrackFiles?")
            for trackfile in old_trackfiles:
                cit.echo(cct.get_path(trackfile).basename, pre="*")
            if cit.get_choice(["Yes", "No"]) == "Yes":
                for filepath in old_trackfiles:
                    os.remove(filepath)
                cit.info("Cleanup done")
            else:
                cit.warn("Cleanup canceled")

    @cit.as_session("Saving TrackFile")
    def to_file(self):
        with open(self.filename, "w", encoding="UTF8") as f:
            options = {}
            if self.format == "JSON":
                options = {"indent": 4, "ensure_ascii": False}
            f.write(self.formatter.dumps(self.trackings, **options))
            cit.info(f"New TrackFile created: [u]{self.path}[/]")

    @cit.as_session("Loading Old TrackFile")
    def from_file(self, path: str) -> bool:
        """Parse a TrackFile and load trackings into instance.

        Args:
            path (str): Path to the TrackFile.

        Returns:
            bool: True if successful.
        """
        if not path or not os.path.isfile(path):
            cit.warn("No TrackFile loaded.")
            return False
        cit.info(f"Parsing TrackFile `{path}`")
        with open(path, encoding="UTF8") as f:
            trackings = self.formatter.loads(f.read())
            cit.info(f"{len(trackings)} entries loaded")
        self.trackings = trackings
        return True

    @cit.as_session("Generating New TrackFile")
    def generate(self, target_dir: str = os.getcwd(), exts: list = [], hash_mode: str = "CRC32"):
        """Generate file tracking information.

        Args:
            target_dir (str): Target directory to scan.
            exts (list[str]): Accepted file extensions. Ex. ["mp3", "m4a"]. Default is [] meaning all files.
            hash_mode (str): "CRC32", "MD5", "NAME", "PATH", "MTIME".

        Returns:
            dict: {filename: filehash}
        """
        paths = []
        if not exts:
            exts = ["*",]
        for ext in exts:
            target_file_pattern = f"*.{ext}"
            cit.info(f"Target file pattern: {target_file_pattern}")
            paths += list(pathlib.Path(target_dir).rglob(target_file_pattern))
        for filepath in cit.track(paths, "Hashing...", unit="files"):
            if hash_mode == "CRC32":
                filehash = cct.crc32(filepath)
            elif hash_mode == "MTIME":
                filehash = int(os.path.getmtime(filepath))
            elif hash_mode == "NAME":
                filehash = os.path.basename(filepath)
            elif hash_mode == "PATH":
                filehash = filepath
            elif hash_mode == "MD5":
                filehash = cct.md5(filepath)
            else:
                filehash = None
            self.trackings[os.path.basename(filepath)] = filehash
