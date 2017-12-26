AC_INIT([fwbackups], 1.43.6)
AC_CONFIG_SRCDIR([src/fwbackups/__init__.py.in])
AM_INIT_AUTOMAKE([foreign dist-bzip2 no-dist-gzip tar-ustar])

# Search for Python >= 2.4
AM_PATH_PYTHON([2.4])

# Setup translation
# See https://blogs.gnome.org/jjardon/2010/10/08/use-upstream-gettext-instead-the-glib-one/
# See https://github.com/cgwalters/intltool-git-mirror/blob/master/README
GETTEXT_PACKAGE=fwbackups
AC_SUBST(GETTEXT_PACKAGE)
IT_PROG_INTLTOOL([0.35.0], [no-xml])

# Output files
AC_CONFIG_FILES([
bin/Makefile
bin/fwbackups
pixmaps/Makefile
po/Makefile.in
src/Makefile
src/fwbackups/Makefile
src/fwbackups/operations/Makefile
src/fwbackups/__init__.py
src/fwbackups/const.py
Makefile
fwbackups.spec
])

# Start
AC_OUTPUT
