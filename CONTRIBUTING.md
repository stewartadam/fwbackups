## Version Upgrades
To release a new version, please:
* Add `ChangeLog` entries
* Update version in `AC_INIT` in `configure.ac`
* Update version in `productnumber` in `docs/User_Guide/en_US/Book_Info.xml`
* Update revision history in `docs/User_Guide/en_US/Revision_History.xml`
* Add changelog entry in `fwbackups.spec.in`
* Generate docs using publican (see `docs/README`)

Then do `./autogen.sh;./configure;make dist`.