# Automake Automagic

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
    TODO

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
	rmdir $(DESTDIR)$(datadir)/fwbackups/

rpm: dist
	@(rpmbuild -ta fwbackups-$(PACKAGE_VERSION).tar.bz2)

srpm: dist
	@(rpmbuild -ts fwbackups-$(PACKAGE_VERSION).tar.bz2)

