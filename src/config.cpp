/*  Copyright (C) 2009 Stewart Adam
 *  This file is part of fwbackups.
 
 * fwbackups is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * fwbackups is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 
 * You should have received a copy of the GNU General Public License
 * along with fwbackups; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
// Global
#include <QString>
#include <QSettings>
// fwbackups
#include "common.h"
// local
#include "config.h"

QString get_configuration_directory() {
#if defined(WIN32)
  return join_path(get_appdata_directory(), "fwbackups");
#elif defined(__APPLE__)
  return join_path(get_appdata_directory(), "Library/Application Support/fwbackups");
#else
  return join_path(get_home_directory(), ".fwbackups");
#endif
}

QSettings* get_settings() {
#if defined(__APPLE__)
  QString settingsLocation = join_path(get_home_directory(), "Library/Preferences/com.diffingo.fwbackups.plist");
  return new QSettings(settingsLocation, QSettings::NativeFormat);
#else
  QString settingsLocation = join_path(get_configuration_directory(), "fwbackups-preferences.conf");
  return new QSettings(settingsLocation, QSettings::IniFormat);
#endif
}

QSettings* get_set_config(QString setName) {
  QString setConfigDirectory = join_path(get_configuration_directory(), "Sets");
  return new QSettings(join_path(setConfigDirectory, setName+".conf"), QSettings::IniFormat);
}
