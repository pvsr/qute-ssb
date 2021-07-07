import subprocess
import platform
import sys
from shutil import which
from pathlib import Path
from sys import exit, stderr

from xdg import BaseDirectory  # type: ignore
from typing import Optional


def error(msg: str) -> None:
    print(f"Error: {msg}", file=stderr)


def user_data_dir() -> Path:
    if platform.system() == "Linux":
        return Path(BaseDirectory.xdg_data_home) / "qutebrowser"
    if platform.system() == "Darwin":
        return Path.home() / "Library" / "Application Support" / "qutebrowser"
    error("This operation is only implemented for linux and macOS.")
    print(
        "If you're interested in adding support for another OS, send a PR "
        "to github.com/pvsr/qbpm adding the location of qutebrowser data such "
        "as history.sqlite on your OS to user_data_dir() in qpm/utils.py.",
        file=stderr,
    )
    exit(1)


def user_config_dir() -> Path:
    return Path(BaseDirectory.xdg_config_home) / "qutebrowser"


def get_default_menu() -> Optional[str]:
    if sys.platform == "darwin":
        return "applescript"
    for menu_cmd in ["rofi", "dmenu"]:
        if which(menu_cmd) is not None:
            return menu_cmd
