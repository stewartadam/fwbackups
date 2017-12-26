## Dependencies
* `python` version 2.x, min. version 2.4
* `pygtk` python package >= 2.10 (with Glade support)
* `crontab` (any cron service - `dcron`, `vixie-cron` or `cronie` for example)
* `paramiko` python package for remote host (SFTP) support
* Optional: `libnotify` bindings for Python (often called python-notify)

Developers and/or users wanting to build from source will also require `autotools`, `intltool` and `gettext`.

## Building from source
If you are **not** using a release download, you will need to generate the `configure` script by running `./autogen.sh` before running the steps below.

Configure and build fwbackups:
```
./configure --prefix=/usr
make
```
Then run `make install` as root (or use sudo) to permanently install it on your system.

## Uninstalling
If you have installed fwbackups from source, you may uninstall it by running `make uninstall` from the original source directory you built fwbackups in.

## Platform-specific notes
### Windows
*Note: fwbackups is no longer compatible with modern versions of Windows due to incompatibility with UAC and the unavailability of a dependency for Windows Vista+. **The Windows port of fwbackups is now unmaintained**. The text below refers was indended for use with Windows XP and will remain for archival purposes.*

fwbackups packages most of the dependencies for Windows in an easy-to-use installer. Simply visit the Downloads page and use the full setup installer to install Python 2.6, PyCron 0.5.9 as well as the required Python modules and GTK+ runtime.

Due to cryptography software export restrictions, binary versions of the paramiko or pycrypto libraries are not distributed in this installer. You can build your own NSIS cryptography module installer from the fwbackups source, or install these two modules manually to the fwbackups python add-on module directory in `C:\Program Files\fwbackups`.

### OS X
Although fwbackups does run on OS X, its dependencies need to be installed manually:
* PyGTK and gtk-mac-integration can be installed easily via [homebrew](https://brew.sh/): `brew install pygtk gtk-mac-integration`
* Python modules can be installed with: `pip --user install paramiko pycrypto`
