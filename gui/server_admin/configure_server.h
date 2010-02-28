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
#ifndef CONFIGURE_SERVER_H
#define CONFIGURE_SERVER_H

#include <QDir>

#include "logger.h"

#include "ui_configure_server.h"

class configureServerDialog: public QDialog, private Ui::configureServer {
  Q_OBJECT
    
public:
  configureServerDialog(QDialog *parent = 0);
  void initalize_ca(QDir host_dir, QString target, QString fq_hostname);
  void initialize_server(QDir host_dir, QString fq_hostname, QDir backup_store_location);
  void sign_server(QDir host_dir, QString fq_hostname);
public slots:
  void on_okButton_clicked();
  void on_cancelButton_clicked();
private:
  fwLogger *logger;
};

#endif
