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

## Translations

Translations happen on [Weblate](https://hosted.weblate.org/projects/fwbackups/), which commits translated `po/*.po` files back to this repository. Please don't edit `po/*.po` by hand.

The template `po/fwbackups.pot` is committed so Weblate can pick up new strings. When you add or change a translatable string:

* If you added a new source file, run `bash update-potfiles.sh` from the `po/` directory
* Regenerate the template with `meson setup _build` (once) and `meson compile -C _build fwbackups-pot`
* Commit the updated `po/fwbackups.pot`

CI fails if `po/POTFILES` or `po/fwbackups.pot` is out of date.

Scripts in `bin/` keep a `.py` extension in the source tree so `xgettext` parses them as Python; meson drops the extension at install time.

## Editing the UI

With Glade now deprecated, to interactively edit the UI use the [cambalache](https://github.com/xjuan/cambalache) RAD tool.
