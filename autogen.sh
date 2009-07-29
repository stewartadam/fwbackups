#!/bin/sh
# Run this to generate all the initial makefiles, etc.

srcdir=`dirname $0`
test -z "$srcdir" && srcdir=.

(test -f $srcdir/configure.ac) || {
    echo -n "**Error**: Directory "\`$srcdir\'" does not look like the"
    echo " top-level package directory"
    exit 1
}

(${AUTORECONF:-autoreconf} --version) < /dev/null > /dev/null 2>&1 || {
    echo
    echo "**Error**: You must have \`autoreconf' installed."
    echo "Download the appropriate package for your distribution,"
    echo "or get the source tarball at ftp://ftp.gnu.org/pub/gnu/"
    DIE=1
}

(${AUTOMAKE:-automake} --version) < /dev/null > /dev/null 2>&1 || {
    echo
    echo "**Error**: You must have \`automake' installed."
    echo "You can get it from: ftp://ftp.gnu.org/pub/gnu/"
    DIE=1
}

if test -n "$DIE"; then
    exit 1
fi

if test -z "$*"; then
    echo "**Warning**: I am going to run \`configure' with no arguments."
    echo "If you wish to pass any to it, please specify them on the"
    echo \`$0\'" command line."
    echo
fi

conf_flags=""

${AUTORECONF:-autoreconf} --install --verbose && ./configure $conf_flags $@

# This is no longer needed after autotools have run
rm -rf autom4te.cache
