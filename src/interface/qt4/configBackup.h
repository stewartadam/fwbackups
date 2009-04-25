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

#include "ui_configBackup.h"
#include "custom_widgets.h"

#define TYPE_SET 1
#define TYPE_ONETIME 2

class configBackupsDialog: public QDialog, private Ui::configBackup
{
  Q_OBJECT
    
public:
  configBackupsDialog(QDialog *parent = 0);
  void setGuidedMode(bool isGuided);
  void setAdvancedMode(bool isAdvanced);
  void setType(int type);
  void setVisible_remoteGrid(bool isVisible);
  bool advancedMode;
  bool guidedMode;

public slots:
  /* Configuration - Bottom Buttons */
  void on_toggleAdvancedButton_clicked();
  void on_cancelButton_clicked();
  void on_nextButton_clicked();
  void on_backButton_clicked();
  void on_okButton_clicked();
  void on_finishButton_clicked();
  void on_advancedOptionsCheck_toggled(bool checked);
  /* Configuration - Destination */
  void on_saveBackupToCombo_currentIndexChanged(int index);
  void on_useKeyAuthenticationCheck_toggled(bool checked);
  void on_changeKeyButton_clicked();
  void on_locationBrowseButton_clicked();
  /* Configuration - Files and Folders */
  void on_addFilesButton_clicked();
  void on_addFoldersButton_clicked();
  void on_removeItemsButton_clicked();
  void on_presetHomeCheck_toggled(bool checked);
  /* Configuration - Triggers */
  void on_startPeriodicallyRadio_toggled(bool checked);
  void on_showPasswordCheck_toggled(bool checked);
  void on_timeSimpleFrequencyCombo_currentIndexChanged(int index);
  /* Configuration - Backup Type */
  void on_compressionCheck_toggled(bool checked);
};

#endif
