# Contributing

## Making a releases

To release a new version, please:
* Add `ChangeLog` entries
* Update version in `meson.build`
* Update version in `productnumber` in `docs/User_Guide/en_US/Book_Info.xml`
* Update revision history in `docs/User_Guide/en_US/Revision_History.xml`
* Add changelog entry in `fwbackups.spec`
* Generate docs using publican (see `docs/README`)

Then do `meson setup _build;meson dist -C _build`.

## Editing the UI

With Glade now deprecated, to interactively edit the UI use the [cambalache](https://github.com/xjuan/cambalache) RAD tool.
