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
#include <QFileInfo>
#include <QDir>
// fwbackups
#include "common.h"
#include "config.h"
#include "logger.h"

int initialize_configuration_directory() {
  QDir directoryInfo( get_configuration_directory() );
  if ( !directoryInfo.exists() ) { // try to create the directory
    if ( !directoryInfo.mkpath( directoryInfo.path() ) ) { // it failed
      return 0;
    }
  }
  directoryInfo.setPath( get_set_configuration_directory() );
  if (!directoryInfo.exists()) { // try to create the directory
    if ( !directoryInfo.mkpath( directoryInfo.path() ) ) { // it failed
      return 0;
    }
  }
  return 1;
}

int initialize_configuration() {
  if ( !initialize_configuration_directory() ) {
    return 0;
  }
  get_settings()->setValue("Version", VERSION);
  return 1;
}

int initialize_logger() {
  QFile file( fwLogger::get_log_location() );
  if ( !file.exists() ) { // try to create an empty file
    if ( !file.open(QIODevice::WriteOnly | QIODevice::Text) ) { // it failed
      return 0;
    }
    file.close();
  }
  return 1;
}
