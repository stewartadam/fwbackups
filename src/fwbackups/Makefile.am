PYTHON_FILES = \
    config.py \
    const.py \
    cron.py \
    fwlogger.py \
    i18n.py \
    __init__.py \
    interface.py \
    sftp.py \
    shutil_modded.py \
    widgets.py

EXTRA_DIST = \
    $(PYTHON_FILES) \
    __init__.py.in

pydir = $(pkgdatadir)/fwbackups
py_PYTHON = $(PYTHON_FILES)

clean-local:
	rm -f *.pyc *.pyo
