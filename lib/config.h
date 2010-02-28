/*  Copyright (C) 2009, 2010 Stewart Adam
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
#ifndef CONFIG_H
#define CONFIG_H

#include <QString>
#include <QStringList>
#include <QSettings>

QString get_configuration_directory();
QString get_set_configuration_directory();
QString get_set_configuration_path(QString setName);
QStringList get_all_set_names();
QSettings* get_set_configuration(QString setName);
QSettings* get_onetime_configuration();
QSettings* get_settings();
#endif
