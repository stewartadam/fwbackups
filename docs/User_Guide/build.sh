#!/bin/sh
publican clean_ids
publican build --formats=html,html-single,pdf --langs=all
rm -rf ../html
rm -f ../pdf/fwbackups*.pdf
cp -a tmp/en-US/html ../
cp -f tmp/en-US/html-single/index.html ../html/index-single.html
cp -f tmp/en-US/pdf/fwbackups*.pdf ../pdf
