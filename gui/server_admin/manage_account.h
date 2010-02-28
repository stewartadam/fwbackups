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
#ifndef MANAGE_ACCOUNT_H
#define MANAGE_ACCOUNT_H

#include "logger.h"

#include "ui_manage_account.h"

class manageAccountDialog: public QDialog, private Ui::manageAccount {
  Q_OBJECT
    
public:
  manageAccountDialog(QString fq_hostname, QDialog *parent = 0);
public slots:
  void on_createAccountButton_clicked();
  void on_cancelButton_clicked();
private:
  fwLogger *logger;
  QString fq_hostname;
};

#endif
