import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from xdg import BaseDirectory  # type: ignore

from qbpm import profiles
from qbpm.profiles import Profile
from qbpm.utils import error, user_data_dir


def from_session(
    session: str,
    profile_name: Optional[str] = None,
    profile_dir: Optional[Path] = None,
    desktop_file: bool = True,
    overwrite: bool = False,
) -> Optional[Profile]:
    if session.endswith(".yml"):
        session_file = Path(session).expanduser()
        session_name = session_file.stem
    else:
        session_name = session
        session_file = user_data_dir() / "sessions" / (session_name + ".yml")
    if not session_file.is_file():
        error(f"{session_file} is not a file")
        return None

    profile = Profile(profile_name or session_name, profile_dir)
    if not profiles.new_profile(profile, None, desktop_file, overwrite):
        return None

    session_dir = profile.root / "data" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=overwrite)
    shutil.copy(session_file, session_dir / "_autosave.yml")

    return profile


def launch(
    profile: Profile, strict: bool, foreground: bool, qb_args: List[str]
) -> bool:
    if not profiles.ensure_profile_exists(profile, not strict):
        return False

    args = profile.cmdline() + qb_args
    if foreground:
        os.execlp("qutebrowser", *args)
    else:
        p = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        try:
            # give qb a chance to validate input before returning to shell
            stdout, stderr = p.communicate(timeout=0.1)
            print(stderr.decode(errors="ignore"), end="")
        except subprocess.TimeoutExpired:
            pass

    return True


def desktop(profile: Profile):
    if profile.exists():
        profiles.create_desktop_file(profile)
    else:
        error(f"profile {profile.name} not found at {profile.root}")


DEFAULT_PROFILE_DIR = Path(BaseDirectory.xdg_data_home) / "qutebrowser-profiles"


def list_() -> None:
    for profile in sorted(DEFAULT_PROFILE_DIR.iterdir()):
        print(profile.name)


def edit(profile: Profile):
    if not profile.exists():
        error(f"profile {profile.name} not found at {profile.root}")
        return
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vim"
    os.execlp(editor, editor, str(profile.root / "config" / "config.py"))
