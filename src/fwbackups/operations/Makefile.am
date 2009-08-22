PYTHON_FILES = \
    __init__.py \
    backup.py \
    restore.py

EXTRA_DIST = \
    $(PYTHON_FILES)

pydir = $(pkgpythondir)/operations
py_PYTHON = $(PYTHON_FILES)

uninstall-hook:
	rmdir $(DESTDIR)$(pkgpythondir)/operations

clean-local:
	rm -f *.pyc *.pyo
