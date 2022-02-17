#!/bin/bash
# Install script for Ubuntu 20.04 Focal which manually grabs the python 2 packages from the 18.04 Bionic distribution
# and installs a modified version of fwbackups which forces python2 usage.
set -e

PREFIX=/usr/local
# https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash
for i in "$@"; do
  case $i in
    --prefix=*)
      PREFIX="${i#*=}"
      shift # past argument=value
      ;;
    -*|--*)
      echo "Unknown option $i"
      exit 1
      ;;
    *)
      echo "Unknown argument $i"
      exit 1
      ;;
  esac
done
PATH=${PREFIX}/bin:${PATH}

# add bionic sources to apt (will remove after install)
release=bionic; cat > "/etc/apt/sources.list.d/$release.list"<<EOF
deb http://archive.ubuntu.com/ubuntu $release universe
deb http://archive.ubuntu.com/ubuntu $release multiverse
deb http://security.ubuntu.com/ubuntu $release-security main
EOF
apt update

apt install autotools-dev x11-apps tzdata build-essential
apt install cron gettext intltool
apt install python2.7

# can install this list of packages without hacking depends
apt install libatk-adaptor libgtk2.0-0 libglade2-0 libglib2.0-0 python-cairo python-gobject-2 python-cryptography python-enum34 python-crypto

# manually obtained dependency list excluding python-is-python2,python,python:any needed to install packages list below
declare -a packages=( "python-paramiko" "python-gtk2" "python-glade2" "python-notify" )
for p in "${packages[@]}" ; do
  echo "Installing $p and fixing dependencies"
  apt download $p
  dpkg --force-depends -i "$p"*.deb
  rm "$p"*.deb
  # edit /var/lib/dpkg/status to remove Depends line from package
  ./edit_dpkg_status $p
  diff /var/lib/dpkg/status status_new || true   # exit 1 if different which they are
  mv status_new /var/lib/dpkg/status
done

# remove bionic sources from apt
rm -f /etc/apt/sources.list.d/$release.list
apt update

# configure and build fwbackups from source which has been modified to use python2
./autogen.sh
PYTHON=python2 ./configure --prefix=${PREFIX}
make install
