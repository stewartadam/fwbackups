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
#include <QFile>
#include <QTextStream>
#include <stdio.h>
#include <time.h>
// fwbackups
#include "common.h"
// Local
#include "logger.h"

QString get_log_directory() {
# ifdef WIN32
  return join_path(get_appdata_directory(), LOGGER_DIR);
# else
  return join_path(get_home_directory(), LOGGER_DIR);
# endif
}

QString get_log_location() {
  QString location = join_path(get_log_directory(), "fwbackups-userlog.txt");
  return location;
}

int log_message(int message_level, QString message_text) {
  QFile file;
  QString message_prefix;
  time_t rawtime;
  struct tm * timeinfo;
  char message_time[80];
  time(&rawtime);
  timeinfo = localtime(&rawtime);
  strftime(message_time, 80, "%b %d %Y %H:%M:%S :: ", timeinfo);
  message_prefix = message_time;
  switch(message_level) {
    case LEVEL_DEBUG:
      message_prefix += "DEBUG       :  ";
      break;
    case LEVEL_INFO:
      message_prefix += "INFORMATION :  ";
      break;
    case LEVEL_WARNING:
      message_prefix += "WARNING     :  ";
      break;
    case LEVEL_ERROR:
      message_prefix += "ERROR       :  ";
      break;
    case LEVEL_CRITICAL:
      message_prefix += "CRITICAL    :  ";
      break;
  }
  // Construct the final log message
  message_text.prepend(message_prefix);
  if ( !message_text.endsWith("\n") ) {
    message_text.append("\n");
  }
  // Print it
  fprintf(stderr, message_text.toUtf8().data());
  // Log it
  file.setFileName( get_log_location() );
  file.open(QIODevice::Append | QIODevice::Text);
  // FIXME: is file.open() needed?
  QTextStream textStream(&file);
  textStream << message_text;
  file.close();
  //(*connected_func_pointer)(message_text);
  return 1;
}
