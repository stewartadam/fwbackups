#!/bin/sh
publican clean_ids
publican build --formats=html,html-single,pdf --langs=all
