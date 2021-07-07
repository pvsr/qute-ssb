import argparse
import os
from sys import platform
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from xdg import BaseDirectory  # type: ignore
from xdg.DesktopEntry import DesktopEntry  # type: ignore

from qpm import profiles
from qpm.profiles import Profile
from qpm.utils import error, user_data_dir, get_default_menu


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


application_dir = Path(BaseDirectory.xdg_data_home) / "applications" / "qbpm"


def desktop(profile_list: list[Profile], args: argparse.Namespace):
    for profile in profile_list:
        if profile.exists():
            profiles.create_desktop_file(profile)
        else:
            error(f"profile {profile.name} not found at {profile.root}")
    if args.choose:
        desktop = DesktopEntry(str(application_dir / f"qbpm.desktop"))
        desktop.set("Name", f"qbpm")
        # TODO allow passing in an icon value
        desktop.set("Icon", "qutebrowser")
        desktop.set("Exec", "qbpm choose %u")
        desktop.set("Categories", ["Network"])
        desktop.set("Terminal", False)
        desktop.set("StartupNotify", True)
        desktop.write()



DEFAULT_PROFILE_DIR = Path(BaseDirectory.xdg_data_home) / "qutebrowser-profiles"


def list_() -> None:
    for profile in sorted(DEFAULT_PROFILE_DIR.iterdir()):
        print(profile.name)


def choose(args: argparse.Namespace) -> None:
    if not args.menu:
        default_menu = get_default_menu()
        if default_menu:
            args.menu = default_menu
        else:
            error("No suitable menu program found, please install rofi or dmenu")
            return None
    elif args.menu not in ["rofi", "dmenu", "applescript"]:
        error(f"{args.menu} is not a valid menu program, please specify one of rofi, dmenu, or applescript")
    elif args.menu == "applescript" and platform != "darwin":
        error(f'Menu applescript cannot be used on a {platform} host')
        return None
    elif shutil.which(args.menu) is not None:
        error(f"{args.menu} not found on path")

    profile_list = '\n'.join([profile.name for profile
                             in sorted(DEFAULT_PROFILE_DIR.iterdir())])
    if not profile_list:
        error("No existing profiles found, create a profile first with qbpm new")
        return None

    if args.menu == "rofi":
        arg_string = ' '.join(args.qb_args)
        selection_cmd = subprocess.Popen(f'echo "{profile_list}" | rofi -dmenu -no-custom -p qutebrowser -mesg {arg_string}',
                                         shell=True, stdout=subprocess.PIPE,
                                         stderr=subprocess.DEVNULL)
        selection = selection_cmd.stdout.read().decode(errors="ignore").rstrip('\n')
    elif args.menu == "dmenu":
        selection_cmd = subprocess.Popen(f'echo "{profile_list}" | dmenu -p qutebrowser',
                                         shell=True, stdout=subprocess.PIPE,
                                         stderr=subprocess.DEVNULL)
        selection = selection_cmd.stdout.read().decode(errors="ignore").rstrip('\n')
    elif args.menu == "applescript":
        profile_list = '", "'.join(profile_list.split('\n'))
        arg_string = ' '.join(args.qb_args)
        cmd_string = f'''osascript -e \'set profiles to {{"{profile_list}"}}
set profile to choose from list profiles with prompt "qutebrowser: {arg_string}" default items {{item 1 of profiles}}
item 1 of profile\''''
        selection_cmd = subprocess.Popen(cmd_string, shell=True,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.DEVNULL)
        selection = selection_cmd.stdout.read().decode(errors="ignore").rstrip('\n')

    if selection:
        profile = Profile(selection, args.profile_dir, args.set_app_id)
        launch(profile, True, args.foreground, args.qb_args)
    else:
        error("No profile selected")

def edit(profile: Profile):
    if not profile.exists():
        error(f"profile {profile.name} not found at {profile.root}")
        return
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vim"
    os.execlp(editor, editor, str(profile.root / "config" / "config.py"))
