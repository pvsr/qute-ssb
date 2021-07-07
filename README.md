# qutebrowser profile manager

[![builds.sr.ht status](https://builds.sr.ht/~pvsr/qpm.svg)](https://builds.sr.ht/~pvsr/qpm?)

qutebrowser profile manager (qbpm) is a tool for creating and managing
[qutebrowser](https://github.com/qutebrowser/qutebrowser) profiles. There isn't
any built in concept of profiles in qutebrowser, but there is a `--basedir`
flag which allows you to use any random directory to store qutebrowser config
and data. By default qbpm creates profiles that source your main qutebrowser
configuration, but have their own history, bookmarks, etc. qutebrowser sessions
started from separate profiles are entirely isolated from each other, and can be
opened and closed independently.

## Usage
Create a new profile called "python", edit its `config.py`, then launch it:
```
$ qbpm new python
$ qbpm edit python
$ qbpm launch python docs.python.org
```

Notice that `qbpm launch` passes extra arguments directly to qutebrowser, so you
can use it to open urls in your profile and use any options you would pass to
qutebrowser:
```
$ qbpm launch python duck.com --target window --loglevel info
```

`qbpm from-session` can copy the tabs of a [saved qutebrowser
session](https://qutebrowser.org/doc/help/commands.html#session-save) to a new
profile. If you have a window full of tabs related to planning a vacation, you
could save it to a session called "vacation" using `:session-save -o vacation`
in qutebrowser, then create a new profile with those tabs:
```
$ qbpm from-session vacation
```

The default profile directory is `$XDG_DATA_HOME/qutebrowser-profiles`, where
`$XDG_DATA_HOME` is usually `$HOME/.local/share`, but you can create and launch
profiles from anywhere using `--profile-dir`/`-P`:
```
$ qbpm --profile-dir ~/dev/my-project new qb-profile
$ cd ~/dev/my-project
$ qbpm -P . launch qb-profile
# or
$ qutebrowser --basedir qb-profile
```

`qbpm` isn't the easiest command to type, so personally I use `qpm` as an alias.

## Installation
 - Pip: `pip install git+https://github.com/pvsr/qbpm.git#egg=qbpm`
 - Arch: [qbpm-git](https://aur.archlinux.org/packages/qbpm-git) in the AUR
 - Nix: clone the repository and run `nix-env -if default.nix`
 - MacOS: For command-line only usage, the pip command above is sufficient, but
   if you would like to set qbpm as the default browser app, first clone this
   repository, then install platypus by running `brew install playtpus`, and
   finally install the app by running `platypus -P contrib/qbpm.platypus
   /Applications/qbpm.app` inside the cloned repository. You should then be
   able to select qbpm as your default browser under: System Preferences
   \> General > Default web browser. Note that there is currently [an
   issue](https://github.com/qutebrowser/qutebrowser/issues/3719) with
   qutebrowser itself that results in unnecessary `file:///*` tabs being
   opened.

## Future ideas that may or may not happen
- Release through github
- More shared or copied config and data
- Use any profile as a base for new profiles (currently only the main config in
  `$XDG_CONFIG_HOME` is supported)
- Source `autoconfig.yml` instead of `config.py`
- Bundled config file optimized for single-site browsing
- `qbpm.conf` to configure the features above
- Someday: qutebrowser plugin
