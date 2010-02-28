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
#include <stdio.h>

#include "manage_account.h"

#include "config.h"
#include "common.h"
#include "logger.h"

manageAccountDialog::manageAccountDialog(QString fq_hostname, QDialog *parent) {
  fwLogger *logger = fwLogger::getInstance();
  setupUi(this); // this sets up GUI
}

void manageAccountDialog::on_createAccountButton_clicked() {
  this->accept();
}

void manageAccountDialog::on_cancelButton_clicked() {
  this->reject();
}
