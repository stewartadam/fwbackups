#!/bin/sh

# List of supported languages, space separated
ALL_LANGS="en-US"

for lang in $ALL_LANGS; do
  if [ -d "$lang" ];then
    echo "*** $lang/ exists; skipping"
  else
    echo "*** $lang/ does not exist; creating"
    publican update_po --langs="$lang"
  fi
done

echo "*** Updating POT translation file"
publican update_pot
echo "*** Updating all language PO translation files"
publican update_po --langs=all
