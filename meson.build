project('fwbackups',
          version: '1.43.8',
    meson_version: '>= 0.62.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

# imports
i18n = import('i18n')
python = import('python').find_installation('python3')
gnome = import('gnome')

# dependencies
gtk4_dep = dependency('gtk4', version: '>= 4.5.0')
adwaita_dep = dependency('libadwaita-1', version: '>= 1.2.0')

# common definitions
bindir = get_option('bindir')
pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
meson_purelib = python.get_install_dir()
system_purelib = python.get_path('purelib')

# by default
pylib = meson_purelib

# python detection can be unreliable - https://github.com/mesonbuild/meson/issues/10459
# if workaround was enabled then we ignore meson and install to the system python's purelib
python_detection_workaround = get_option('force_system_python')

if python_detection_workaround
  pylib = system_purelib
endif
pymoduledir = join_paths(pylib, meson.project_name())

conf = configuration_data()
conf.set('PYTHON', python.full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'fwbackups.spec.in',
  output: 'fwbackups.spec',
  configuration: conf,
  install: false
)

# run subdirectories
subdir('bin')
subdir('data')
subdir('po')
subdir('fwbackups')

# post-install actions
update_desktop_database = find_program('update-desktop-database', required: false)
gnome = import('gnome')
gnome.post_install(
  gtk_update_icon_cache: true,
  update_desktop_database: update_desktop_database.found(),
)

# output detections and installation paths
message('using prefix:', get_option('prefix'))
message('python.install_env:', get_option('python.install_env'))
if not pylib.startswith(get_option('prefix'))
  warning('python modules will be installed outside of the designated prefix.')
endif

message('python detection workaround:', python_detection_workaround)
message('|- meson-constructed python dir:', meson_purelib)
message('|- system python modules dir:\t ', system_purelib)
message('|- using python dir:\t\t ', pylib)
