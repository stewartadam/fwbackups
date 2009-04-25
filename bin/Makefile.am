EXTRA_DIST = \
    fwbackups \
    fwbackups-run.py \
    fwbackups-runonce.py

install-data-local:
	$(mkinstalldirs) $(DESTDIR)$(bindir)
	$(INSTALL) -m 755 fwbackups $(DESTDIR)$(bindir)/fwbackups
	$(INSTALL) -m 755 fwbackups-run.py $(DESTDIR)$(bindir)/fwbackups-run
	$(INSTALL) -m 755 fwbackups-runonce.py $(DESTDIR)$(bindir)/fwbackups-runonce

uninstall-local:
	rm -f $(DESTDIR)$(bindir)/fwbackups
	rm -f $(DESTDIR)$(bindir)/fwbackups-run
	rm -f $(DESTDIR)$(bindir)/fwbackups-runonce

clean:
	rm -f *~
