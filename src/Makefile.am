FWDATA_FILES = \
    BugReport.glade \
    cronwriter.py \
    fwbackups.glade \
    fwbackups-autostart.desktop \
    fwbackups-runapp.pyw

EXTRA_DIST = \
    $(FWDATA_FILES) \
    fwbackups.desktop

fwdatadir = $(DESTDIR)$(datadir)
fwdata_DATA = $(FWDATA_FILES)

install-data-local:
	$(mkinstalldirs) $(DESTDIR)$(datadir)/applications
	$(INSTALL) -m 644 fwbackups.desktop $(DESTDIR)$(datadir)/applications/fwbackups.desktop

uninstall-local:
	rm -f $(DESTDIR)$(datadir)/applications/fwbackups.desktop
#	rm -f $(DESTDIR)$(datadir)/fwbackups/

clean-local:
	rm -f *.bak *.gladep
