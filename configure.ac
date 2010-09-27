AC_INIT([fwbackups], 1.43.3rc5)
AM_INIT_AUTOMAKE([dist-bzip2 no-dist-gzip])
AC_CONFIG_SRCDIR([src/fwbackups/__init__.py.in])

# Search for Python >= 2.4
AM_PATH_PYTHON([2.4])

# Setup gettext translation
ALL_LINGUAS=""
GETTEXT_PACKAGE=fwbackups
AC_SUBST(GETTEXT_PACKAGE)
# I tried hard, but it looks like we can't escape the grasp of glib.
AM_GLIB_GNU_GETTEXT
# Use intltool
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
Makefile
fwbackups.spec
])

# Start
AC_OUTPUT

