# Automake Automagic

DISTCHECK_CONFIGURE_FLAGS = --disable-scrollkeeper

EXTRA_DIST = \
    intltool-extract.in \
    intltool-merge.in \
    intltool-update.in \
    fwbackups.spec.in \
    fwbackups.spec \
    AUTHORS \
    ChangeLog \
    COPYING \
    COPYING-DOCS \
    README \
    TODO \
    gnome-doc-utils.make

DISTCLEANFILES = \
    intltool-extract \
    intltool-merge \
    intltool-update \
    aclocal.m4

SUBDIRS = \
    bin \
    help \
    po \
    pixmaps \
    src \
    src/fwbackups \
    src/fwbackups/operations

uninstall-local:
	rm -f $(DESTDIR)$(pkgdatadir)/pixmaps/*.png

maintainer-clean-local:
	rm -f fwbackups-$(PACKAGE_VERSION).tar.bz2
	rm -f configure install-sh missing

rpm: dist
	@(rpmbuild -ta fwbackups-$(PACKAGE_VERSION).tar.bz2)

srpm: dist
	@(rpmbuild -ts fwbackups-$(PACKAGE_VERSION).tar.bz2)
