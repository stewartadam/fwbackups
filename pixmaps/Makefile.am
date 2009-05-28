EXTRA_DIST = \
    fwbackups.svg \
    fwbackups.ico \
    fwbackups_un.ico \
    fwbackups-32.png \
    fwbackups-64.png \
    fwbackups-128.png

install-data-local:
	$(mkinstalldirs) $(DESTDIR)$(datadir)/pixmaps/
	$(mkinstalldirs) $(DESTDIR)$(datadir)/fwbackups/
	$(INSTALL) -m 644 fwbackups.svg $(DESTDIR)$(datadir)/pixmaps/fwbackups.svg
	$(INSTALL) -m 644 fwbackups-32.png $(DESTDIR)$(datadir)/fwbackups/fwbackups.png

uninstall-local:
	rm -f $(DESTDIR)$(datadir)/pixmaps/fwbackups.svg
	rm -f $(DESTDIR)$(datadir)/fwbackups/fwbackups.png
