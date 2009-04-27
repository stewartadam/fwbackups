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
#ifndef LOGGER_H
#define LOGGER_H

#include <QString>

// Our constants
#define LEVEL_DEBUG 0
#define LEVEL_INFO 1
#define LEVEL_WARNING 2
#define LEVEL_ERROR 3
#define LEVEL_CRITICAL 4

int log_message(int message_level, QString message);
QString get_log_location();
QString get_log_directory();
//void log_connect_function(int (*function_pointer)(QString));

#endif