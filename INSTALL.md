It is strongly recommended to download fwbackups from your package manager or by
using an application distribution system like Flatpak, which will automatically
include all dependencies.

If you wish to manually build and install fwbackups, read on.

- [Building fwbackups from source](#building-fwbackups-from-source)
  - [Dependencies](#dependencies)
  - [Try fwbackups (run from source)](#try-fwbackups-run-from-source)
  - [Build \& install](#build--install)
    - [Customized Python installations](#customized-python-installations)
    - [Installing Python packages](#installing-python-packages)
  - [Troubleshooting](#troubleshooting)
    - [Poetry install hangs on package installation with 'pending'](#poetry-install-hangs-on-package-installation-with-pending)
- [Building flatpak](#building-flatpak)

# Building fwbackups from source

## Dependencies

If you do want to build from source, fwbackups uses the [meson build system](https://mesonbuild.com/) and requires:

- Python 3
  - paramiko package
  - pygobject package
- GTK 4
- libadwaita 1.x
- gettext
- cronie (or any other cron service that provides `crontab`)
- `tar` (archive engine) or `rsync` (direct copy engine) binaries on system `$PATH`

These packages can be installed on Fedora-based systems:

```sh
dnf install meson cronie rsync gettext gtk4 libadwaita adwaita-icon-theme python3-paramiko python3-gobject
```

On Ubuntu/Debian-based systems:

```sh
apt-get install meson cron rsync gettext gtk4 libadwaita-1-0 adwaita-icon-theme python3-paramiko python3-gi
```

On MacOS:

```sh
brew install meson rsync gettext gtk4 libadwaita adwaita-icon-theme pygobject3
python3 -m pip install paramiko
```

## Try fwbackups (run from source)

If the above dependencies are installed, one can run fwbackups directly from the
source tree without building:

```sh
python -m fwbackups
```

Note that any backups sets will **not** run as scheduled when fwbackups is run
directly from source.

## Build & install

fwbackups can be built and installed to your system with:

```sh
meson setup _build -Dpython.install_env=auto --prefix=/usr
meson install -C _build
```

### Customized Python installations

On MacOS and systems with customized Python installations outside `/usr`, meson
may incorrectly identify the installation path due to [this issue]( https://github.com/mesonbuild/meson/issues/10459).

In these situations, the `force_system_python` build option should be enabled
to ensure the package folder for the detected python installation is used:

```sh
meson setup _build -Dpython.install_env=auto -Dforce_system_python=true
meson install -C _build
```

### Installing Python packages

If you cannot install the Python packages with your OS package manger (e.g
`apt-get`), it is recommended you setup a virtual environment to contain your
dependencies.

`poetry` can be used to install them in a Python virtual environment:

```sh
python3 -m pip install -U poetry
poetry install
```

It may be useful to include your system site packages to avoid installing GTK4 bindings within the virtual environment (i.e. on MacOS, where GTK4 is provided via `brew`):

```sh
poetry config virtualenvs.options.system-site-packages true
poetry install
```

Run fwbackups from the virtual environment with:

```sh
poetry run python -m fwbackups
```

## Troubleshooting

### Poetry install hangs on package installation with 'pending'

Try disabling the experimental installer:

```sh
poetry config experimental.new-installer false
```

More details at [poetry issue #3352](https://github.com/python-poetry/poetry/issues/3352).

# Building flatpak

Setup the out-of-source build:

```sh
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
mkdir -p _build_flatpak
```

Build and test the image locally:

```sh
flatpak-builder --user --install --force-clean build-dir com.diffingo.fwbackups.json
flatpak run com.diffingo.fwbackups
```

Install it:

```sh
flatpak-builder --repo=repo --force-clean _build_flatpak com.diffingo.fwbackups.json
flatpak build-update-repo repo
```

Run the administrator GUI:

```sh
flatpak-run com.diffingo.fwbackups
```

Run one of the CLI commands:

```sh
flatpak-run com.diffingo.fwbackups --command=/bin/env -- fwbackups-run 'setname'
```
