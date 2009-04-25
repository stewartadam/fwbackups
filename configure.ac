AC_INIT([fwbackups], 1.43.3rc2)
# Use bz2
AM_INIT_AUTOMAKE([dist-bzip2 no-dist-gzip])
# Sanity checks
AC_CONFIG_SRCDIR([src/fwbackups/__init__.py.in])
AC_CONFIG_SRCDIR([src/fwbackups-runapp.pyw])
# Tell automake we're using Python, and we need version >= 2.4
AM_PATH_PYTHON([2.4])

#ALL_LINGUAS="bn_IN bn ca cs da de el es fi fr gl gu hi hr hu is it ja ko ml ms nb nl or pa pl pt pt_BR ru sk sl sr@Latn sr sv ta tr uk zh_CN zh_TW"

# for gnome docs
GNOME_DOC_INIT
AC_CONFIG_MACRO_DIR([m4])

GETTEXT_PACKAGE=fwbackups
AC_SUBST(GETTEXT_PACKAGE)
AM_GLIB_GNU_GETTEXT
AC_PROG_INTLTOOL

AC_CONFIG_FILES([
bin/Makefile
bin/fwbackups
help/Makefile
pixmaps/Makefile
po/Makefile.in
src/Makefile
src/fwbackups/Makefile
src/fwbackups/operations/Makefile
src/fwbackups/__init__.py
Makefile
fwbackups.spec
])
AC_OUTPUT
