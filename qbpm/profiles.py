from functools import partial
from pathlib import Path
from sys import platform
from typing import List, Optional

from xdg import BaseDirectory  # type: ignore
from xdg.DesktopEntry import DesktopEntry  # type: ignore

from qbpm.utils import error, user_config_dir


class Profile:
    name: str
    profile_dir: Path
    set_app_id: bool
    root: Path

    def __init__(
        self, name: str, profile_dir: Optional[Path], set_app_id: bool = False
    ) -> None:
        self.name = name
        self.profile_dir = profile_dir or Path(
            BaseDirectory.save_data_path("qutebrowser-profiles")
        )
        self.set_app_id = set_app_id
        self.root = self.profile_dir / name

    def check(self) -> Optional["Profile"]:
        if "/" in self.name:
            error("profile name cannot contain slashes")
            return None
        if not self.profile_dir.resolve().is_dir():
            error(f"{self.profile_dir} is not a directory")
            return None
        return self

    def exists(self) -> bool:
        return self.root.exists() and self.root.is_dir()

    def cmdline(self) -> List[str]:
        macos_app = "/Applications/qutebrowser.app/Contents/MacOS/qutebrowser"
        if platform == "darwin" and Path(macos_app).exists():
            qb = macos_app
        else:
            qb = "qutebrowser"
        return [qb, "-B", str(self.root), "--qt-arg", "name", self.name] + (
            ["--desktop-file-name", self.name] if self.set_app_id else []
        )


def create_profile(profile: Profile, overwrite: bool = False) -> bool:
    if not profile.check():
        return False

    if not overwrite and profile.root.exists():
        error(f"{profile.root} already exists")
        return False

    config_dir = profile.root / "config"
    config_dir.mkdir(parents=True, exist_ok=overwrite)
    print(profile.root)
    return True


def create_config(
    profile: Profile, home_page: Optional[str] = None, overwrite: bool = False
) -> None:
    user_config = profile.root / "config" / "config.py"
    with user_config.open(mode="w" if overwrite else "x") as dest_config:
        out = partial(print, file=dest_config)
        out("config.load_autoconfig()")
        title_prefix = "{perc}{current_title}{title_sep}"
        out(f"c.window.title_format = '{title_prefix} qutebrowser ({profile.name})'")
        if home_page:
            out(f"c.url.start_pages = ['{home_page}']")
        main_config_dir = user_config_dir()
        out(f"config.source('{main_config_dir / 'config.py'}')")
        for conf in main_config_dir.glob("conf.d/*.py"):
            out(f"config.source('{conf}')")


application_dir = Path(BaseDirectory.xdg_data_home) / "applications" / "qbpm"


def create_desktop_file(profile: Profile):
    desktop = DesktopEntry(str(application_dir / f"{profile.name}.desktop"))
    desktop.set("Name", f"{profile.name} (qutebrowser profile)")
    # TODO allow passing in an icon value
    desktop.set("Icon", "qutebrowser")
    desktop.set("Exec", " ".join(profile.cmdline()) + " %u")
    desktop.set("Categories", ["Network"])
    desktop.set("Terminal", False)
    desktop.set("StartupNotify", True)
    desktop.write()


def ensure_profile_exists(profile: Profile, create: bool = True) -> bool:
    if profile.root.exists() and not profile.root.is_dir():
        error(f"{profile.root} is not a directory")
        return False
    if not profile.root.exists() and create:
        return new_profile(profile)
    if not profile.root.exists():
        error(f"{profile.root} does not exist")
        return False
    return True


def new_profile(
    profile: Profile,
    home_page: Optional[str] = None,
    desktop_file: bool = True,
    overwrite: bool = False,
) -> bool:
    if create_profile(profile, overwrite):
        create_config(profile, home_page, overwrite)
        if desktop_file:
            create_desktop_file(profile)
        return True
    return False
