project('fwbackups',
          version: '1.43.8',
    meson_version: '>= 0.59.0',
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
# pylib can be unreliable - https://github.com/mesonbuild/meson/issues/10459
pylib = python.get_install_dir()
pymoduledir = join_paths(pylib, meson.project_name())
bindir = get_option('bindir')
pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

message('using prefix:', get_option('prefix'))
message(' |- bin:', get_option('bindir'))
message(' |- python lib dir:', pylib)

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
