EXTRA_DIST = \
    fwbackups.svg \
    fwbackups.ico \
    fwbackups_un.ico \
    fwbackups-16.png \
    fwbackups-32.png \
    fwbackups-48.png \
    fwbackups-64.png \
    fwbackups-128.png

install-data-local:
	$(mkinstalldirs) $(DESTDIR)$(datadir)/icons/hicolor/{scalable,128x128,64x64,48x48,32x32,16x16}/apps/
	$(mkinstalldirs) $(DESTDIR)$(datadir)/fwbackups/
	$(INSTALL) -m 644 fwbackups.svg $(DESTDIR)$(datadir)/icons/hicolor/scalable/apps/fwbackups.svg
	$(INSTALL) -m 644 fwbackups-128.png $(DESTDIR)$(datadir)/icons/hicolor/128x128/apps/fwbackups.png
	$(INSTALL) -m 644 fwbackups-64.png $(DESTDIR)$(datadir)/icons/hicolor/64x64/apps/fwbackups.png
	$(INSTALL) -m 644 fwbackups-48.png $(DESTDIR)$(datadir)/icons/hicolor/48x48/apps/fwbackups.png
	$(INSTALL) -m 644 fwbackups-32.png $(DESTDIR)$(datadir)/icons/hicolor/32x32/apps/fwbackups.png
	$(INSTALL) -m 644 fwbackups-16.png $(DESTDIR)$(datadir)/icons/hicolor/16x16/apps/fwbackups.png
	$(INSTALL) -m 644 fwbackups-32.png $(DESTDIR)$(datadir)/fwbackups/fwbackups.png

uninstall-local:
	rm -f $(DESTDIR)$(datadir)/icons/hicolor/*/apps/fwbackups.*
	rm -f $(DESTDIR)$(datadir)/fwbackups/fwbackups.png
