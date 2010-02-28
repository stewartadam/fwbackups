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
#ifndef CONFIGBACKUP_H
#define CONFIGBACKUP_H

#include "ui_configure_backup.h"
#include "ui_choose_programs.h"

// Define constants for the set types
#define TYPE_SET 1
#define TYPE_ONETIME 2
// Define contants for the destination types
#define TYPE_DESTINATION_LOCAL 1
#define TYPE_DESTINATION_REMOTE 2

class configBackupsDialog: public QDialog, private Ui::configBackup {
  Q_OBJECT
    
public:
  configBackupsDialog(QWidget *parent, int type);
  void setAdvancedMode(bool isAdvanced);
  bool saveConfiguration(QString setName = "");
  bool loadConfiguration(QString setName = "");

public slots:
  /* Configuration - Bottom Buttons */
  void on_cancelButton_clicked();
  void on_nextButton_clicked();
  void on_backButton_clicked();
  void on_finishButton_clicked();
  void on_advancedOptionsCheck_toggled(bool checked);
  /* Configuration - Profiles */
  void on_profileRecurringRadio_toggled(bool toggled);
  /* Configuration - Files and Folders */
  void on_presetBookmarksProgramsButton_clicked();
  void on_presetEmailProgramsButton_clicked();
  void on_presetSettingsProgramsButton_clicked();
  void on_addFilesButton_clicked();
  void on_addFoldersButton_clicked();
  void on_removeItemsButton_clicked();
  void on_presetHomeCheck_toggled(bool checked);
  /* Configuration - Advanced Options */
  /* Configuration - Destination */
  /* Configuration - Scheduling */
  void on_timeSimpleFrequencyCombo_currentIndexChanged(int index);
private:
  void setType(int configType);
  int type;
  bool advancedMode;
  QString originalSetName;
};

class chooseProgramsDialog: public QDialog, private Ui::chooseProgramsDialog {
  Q_OBJECT
public:
  chooseProgramsDialog(QWidget *parent = 0);
  QCheckBox *addCheck(QString label);
  void setLabel(QString label);
public slots:
  void on_okButton_clicked();
};
#endif
