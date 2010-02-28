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
#ifndef RESTORE_H
#define RESTORE_H

#include "ui_restore.h"
#include "custom_widgets.h"

class restoreDialog: public QDialog, private Ui::restoreDialog
{
  Q_OBJECT
    
public:
  restoreDialog(QWidget *parent);
  void setGuidedMode(bool isGuided);
  bool guidedMode;

public slots:
  /* Configuration - Bottom Buttons */
  void on_cancelButton_clicked();
  void on_nextButton_clicked();
  void on_backButton_clicked();
  void on_startRestoreButton_clicked();
  /* Configuration - Source */
  void on_destBrowseButton_clicked();
};

#endif
