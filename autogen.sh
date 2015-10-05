#!/bin/sh
# Run this to generate all the initial makefiles, etc.
autoreconf --install --force --verbose
echo "Running intltoolize"
intltoolize --copy --force --automake
