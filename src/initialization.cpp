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
  if ( !directoryInfo.exists() ) {
    directoryInfo.mkpath( directoryInfo.path() );
  }
  directoryInfo.setPath( join_path(get_configuration_directory(), "Sets") );
  if (!directoryInfo.exists()) {
    directoryInfo.mkpath( directoryInfo.path() );
  }
  return 1;
}

int initialize_logger() {
  QFile file( get_log_location() );
  if ( !file.exists() ) {
    file.open(QIODevice::WriteOnly | QIODevice::Text);
    file.close();
  }
  return 1;
}
