FWDATA_FILES = \
    BugReport.glade \
    fwbackups.glade \
    fwbackups-autostart.desktop \
    fwbackups-runapp.py

EXTRA_DIST = \
    $(FWDATA_FILES) \
    fwbackups.desktop

fwdatadir = $(datadir)/fwbackups
fwdata_DATA = $(FWDATA_FILES)

install-data-local:
	$(mkinstalldirs) $(DESTDIR)$(datadir)/applications
	$(INSTALL) -m 644 fwbackups.desktop $(DESTDIR)$(datadir)/applications/fwbackups.desktop

uninstall-local:
	rm -f $(DESTDIR)$(datadir)/applications/fwbackups.desktop

clean-local:
	rm -f *.bak *.gladep
