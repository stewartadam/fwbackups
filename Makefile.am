# Automake Automagic

EXTRA_DIST = \
    docs \
    intltool-extract.in \
    intltool-merge.in \
    intltool-update.in \
    fwbackups.spec.in \
    fwbackups.spec \
    AUTHORS \
    ChangeLog \
    COPYING \
    README \
    TODO \
    test.operations.py

DISTCLEANFILES = \
    intltool-extract \
    intltool-merge \
    intltool-update

SUBDIRS = \
    bin \
    po \
    pixmaps \
    src \
    src/fwbackups/operations \
    src/fwbackups

clean-local:
	rm -rf tests

uninstall-hook:
#	 Removes 1.43.3rc location of fwbackups python package
	rm -rf $(DESTDIR)$(datadir)/fwbackups/fwbackups
	rmdir $(DESTDIR)$(datadir)/fwbackups/

rpm: dist
	@(rpmbuild -ta fwbackups-$(PACKAGE_VERSION).tar.bz2)

srpm: dist
	@(rpmbuild -ts fwbackups-$(PACKAGE_VERSION).tar.bz2)

