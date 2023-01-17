# fwbackups

A feature-rich user backup program that allows you to backup your documents on a
one-off or recurring scheduled basis.

It is compatible with MacOS and Linux systems with Python 3 and GTK 4.

***Note: fwbackups is in maintenance only mode.*** See below for details.

## Features

- Simple interface for configuring new backups or restoring documents from a
  previous backup
- Multiple backup formats: directory copy or tar archive
  - Incremental backup support (directory copy only)
  - Compression (archive format only)
  - Exclude files or folders
- Send backups to remote hosts with SFTP/SSH
- Automatic backup organization and cleanup
- Restore existing backup sets

## User guide

The most recent version of user guide is available online, in HTML or PDF, [here](https://www.diffingo.com/oss/fwbackups/documentation).

## Building & Installation

If your distribution offers fwbackups in its software repositories, it is
recommended you install fwbackups that way instead.

fwbackups is also available as a Flatpak image under the name *com.diffingo.fwbackups*.

For instructions on how to build from source, read on in [INSTALL.md](INSTALL.md).

## Usage

The fwbackups desktop entry starts the backup administrator, a GUI tool to
manage backup sets or perform one-time backups and restore operations.

It can also be started from the CLI:

```sh
fwbackups
```

An existing backup set can be run manually by executing:

```sh
fwbackups-run SetName1 SetName2 [...]
```

To start a one-time backup without an existing set configuration, use:

```sh
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
