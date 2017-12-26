fwbackups
======
A feature-rich user backup program that allows you to backup your documents on a
one-off or recurring scheduled basis.

***Note: fwbackups is in maintenance only mode.** Development of new features
are on hold, and only bugfixes are applied. See below for details.*

## Features
* Simple interface for configuring new backups or restoring documents from a
  previous backup
* Multiple backup formats: directory copy or tar archive
  * Incremental backup support (directory copy only)
  * Compression (archive format only)
  * Exclude files or folders
* Send backups to remote hosts with SFTP/SSH
* Automatic backup organization and cleanup
* Restore existing backup sets

## Platform compatibility
Linux, OS X (lightly tested) and Windows (rarely tested)

## User guide
Note: a copy of the user guide is available in HTML and PDF form in the `docs/`
folder included with a release download of fwbackups.

You can also always view the most recent user guides at the following URL:
http://www.diffingo.com/oss/fwbackups/documentation

## Building & Installation
Most distributions offer package management systems that make it extremely easy
to install additional software packages. If your distribution offers fwbackups
in its software repositories, it is recommended you install fwbackups that way
instead.

If a package is unavailable for your distribution or if you would like to build
from source, please review the [INSTALL.md](installation guide).

## Usage
fwbackups installs a menu entry under *Applications > System Tools* to start the
backup administrator, a GUI tool to manage sets or perform one-time backups
and restore operations. It can also be started from the CLI:
```
fwbackups
```

An existing backup set can be run manually by executing:
```
fwbackups-run SetName1 SetName2 [...]
```

To start a one-time backup without an existing set configuration, use:
```
fwbackups-runonce /src/Path1 /src/Path2 [...] /destination
```

Execute either command with the `--help` parameter for full options and usage
details.

## Translations
Translations are available [here](https://www.transifex.com/Magic/fwbackups/) - you're welcome to add or correct translations!

## Known Issues
### Linux-specific
* If you previously installed fwbackups a 1.43.3 release candidate from source
  (for example on Ubuntu), please remove the `/usr/share/fwbackups/fwbackups`
  directory manually before installing 1.43.4.
* An issue was identified in the previous version of fwbackups (1.43.3) where
  after upgrading, the backup schedule may have been erased. If you have been
  affected by this problem, simply open the administrator utility and then close
  it to reschedule all backups.

### Windows-specific
* If you have previously installed an older version of fwbackups (ie 1.43.2) and
  have not upgraded to Python 2.6, it is recommended that you uninstall Python,
  PyCron and fwbackups and then use the full installer to install fwbackups
  1.43.4 from scratch.

## Maintenance status
fwbackups is in maintenance mode, and releases will be published for only major
bugfixes (or if a new feature is added **and tested** with a pull request).

Although I would love to keep working on fwbackups, I unfortunately no longer
have the free time to give fwbackups the attention that it deserves. I have
learned a lot through maintaining fwbackups and want to thank all the users for
the support, feature requests, pull requests. I hope that you still find the
software useful.

Given the above, the plans around the 1.44 C++ rewrite of fwbackups are also on
hold. The `cplusplus` branch of this repo has a functional, cross-platform
Qt4-based UI and cmake build system with limited bindings to boxbackup, but
should be considered as abandoned/for reference only.
