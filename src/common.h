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
#ifndef COMMON_H
#define COMMON_H

#include <QString>
// Pulls in some system limits, including PATH_MAX
#include <limits.h>

// Update me every release
#define VERSION_MAJOR 1
#define VERSION_MINOR 44
#define VERSION_PATCH 0
#define VERSION "1.44.0"

// PATH_MAX is MAX_PATH on Windows, so reverse it
#if defined( WIN32 )
#  include <malloc.h>
#  ifndef PATH_MAX
#    define PATH_MAX MAX_PATH
#  endif
#endif

// Define the path & directory separation characters
#if defined( WIN32 )
#  define DIR_SEP "\\"
#  define PATH_SEP ";"
#else
#  define DIR_SEP "/"
#  define PATH_SEP ":"
#endif

QString join_path(QString path1, QString path2);
QString get_directory(bool b_appdata, bool b_common_appdata);
QString get_home_directory();
QString get_appdata_directory();

#endif