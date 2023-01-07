#!/bin/sh
set -eu

POTFILES=po/POTFILES

if [ ! -f ../pyproject.toml ];then
  echo 'Must be called from po/ directory'
  exit 1
fi

pushd ..

rm -f "$POTFILES"

find fwbackups -name '*.ui' >> "$POTFILES"
find fwbackups -name '*.py' >> "$POTFILES"
find bin -name 'fwbackups*' >> "$POTFILES"

echo "data/com.diffingo.fwbackups.desktop.in" >> "$POTFILES"
echo "data/com.diffingo.fwbackups.appdata.xml.in" >> "$POTFILES"

popd
