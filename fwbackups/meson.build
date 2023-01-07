pymoduledir = join_paths(pylib, meson.project_name())

configure_file(
  input: '__init__.py.in',
  output: '__init__.py',
  configuration: conf,
  install: true,
  install_dir: pymoduledir
)
install_subdir('.', install_dir: pymoduledir, exclude_files: '__init__.py.in', strip_directory: true)