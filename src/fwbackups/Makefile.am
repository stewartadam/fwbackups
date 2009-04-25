PYTHON_FILES = \
    config.py \
    const.py \
    cron.py \
    fwlogger.py \
    i18n.py \
    __init__.py \
    interface.py \
    remote.py \
    shutil_modded.py \
    subprocess_killable.py \
    widgets.py \
    winprocess.py

EXTRA_DIST = \
    $(PYTHON_FILES) \
    __init__.py.in

pydir = $(pythondir)/fwbackups
py_PYTHON = $(PYTHON_FILES)

clean-local:
	rm -f *.pyc *.pyo
