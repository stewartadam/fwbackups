# Automake Automagic

EXTRA_DIST = \
    intltool-extract.in \
    intltool-merge.in \
    intltool-update.in \
    fwbackups.spec.in \
    AUTHORS \
    ChangeLog \
    COPYING \
    COPYING-DOCS \
    README \
    TODO

DISTCLEANFILES = \
    intltool-extract \
    intltool-merge \
    intltool-update

SUBDIRS = \
    bin \
    help \
    po \
    pixmaps \
    src \
    src/fwbackups \
    src/fwbackups/operations

uninstall-local:
	rm -rf $(DESTDIR)$(datadir)/fwbackups/

maintainer-clean-local:
	rm -f fwbackups-$(PACKAGE_VERSION).tar.bz2
	rm -f configure install-sh missing

rpm: dist
	@(rpmbuild -ta fwbackups-$(PACKAGE_VERSION).tar.bz2)

srpm: dist
	@(rpmbuild -ts fwbackups-$(PACKAGE_VERSION).tar.bz2)
