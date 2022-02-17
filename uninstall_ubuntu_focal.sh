#!/bin/bash

apt remove libglade2-0 python-cairo python-gobject-2 python-cryptography python-enum34 python-crypto
apt remove python-paramiko python-gtk2 python-glade2 python-notify
make uninstall
