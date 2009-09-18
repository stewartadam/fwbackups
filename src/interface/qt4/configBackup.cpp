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

// interface - qt4
#include "custom_widgets.h"
#include "configBackup.h"

#include "common.h"
#include "config.h"
#include "logger.h"

configBackupsDialog::configBackupsDialog(int configType, QDialog *parent) {
  fwLogger *logger = fwLogger::getInstance();
  
  type = configType;
  advancedMode = true;
  /* "not" is a workaround for the if check that ensures guidedMode is not true
   * when calling setGuidedMode with a parmeter of true */
  guidedMode = not get_settings()->value("ConfiguringBackups/GuidedMode", true).toBool();
  keyFile = "";
  originalSetName = "";
  setupUi(this); // this sets up GUI
  
  // Double negative makes a positive! Now guidedMode != isGuided
  this->setGuidedMode(not guidedMode);
  this->setAdvancedMode(not advancedMode);
  this->setType(type); // Must be called after all set*Mode functions
  
  timeSimpleFrequencyCombo->setCurrentIndex(2); // default to "Weekly" frequency
  compressionTypeCombo->setEnabled(false); // default to no compression
  saveBackupToCombo->setCurrentIndex(0); // default to local drive
  // force refreshes
  this->on_saveBackupToCombo_currentIndexChanged(0);
  this->on_profileRecurringRadio_toggled(false);
  
  // Setup the path list
  QStringList headers;
  headers << tr("Location") << tr("Status");
  TreeModel *pathsTreeModel = new TreeModel(headers);
  pathsTreeView->setModel(pathsTreeModel);
  // Setup the first column nicely
  pathsTreeView->setColumnWidth(1, 35);
  pathsTreeView->setColumnWidth(0, 415);
}

/*
 * Toggles guided mode. Assumes that this function is called before the
 * configuration window is displayed.
 */
void configBackupsDialog::setGuidedMode(bool isGuided) {
  QString header;
  if (isGuided && ! guidedMode) {
    // Add Finished tab
    configurationTabs->insertTab(6, finishedTab, tr("Finished!"));
    configurationTabs->setCurrentIndex(0);
    configurationTabs->tabBar()->hide();
    // Disable use of these buttons
    okButton->hide();
    finishButton->hide();
    // Enable use of back/next/cancel
    backButton->setEnabled(false);
    backButton->show();
    cancelButton->show();
    nextButton->show();
    nextButton->setDefault(true);
    // Uses the checkbox on Profiles to enable advanced options
    toggleAdvancedButton->hide();
    advancedOptionsCheck->show();
    advancedOptionsLine->show();
    // Set header
    header = tr("Configure a Backup - Welcome");
    headerLabel->setText(header);
  } else if (! isGuided && guidedMode) {
    // Remove Finished tab
    configurationTabs->removeTab(6);
    configurationTabs->tabBar()->show();
    // Disable use of these buttons
    finishButton->hide();
    backButton->hide();
    nextButton->hide();
    // Enable use of ok/cancel
    cancelButton->show();
    okButton->show();
    okButton->setDefault(true);
    // Uses button to enable advanced options
    advancedOptionsCheck->hide();
    advancedOptionsLine->hide();
    toggleAdvancedButton->show();
    // Set header
    header = tr("Configure a Backup");
    headerLabel->setText(header);
  }
  guidedMode = isGuided;
}

/*
 * Toggles advanced mode. Assumes that this function is called before the
 * configuration window is displayed.
 */
void configBackupsDialog::setAdvancedMode(bool isAdvanced) {
  if (isAdvanced && ! advancedMode) {
    // Offer to return to basic mode
    toggleAdvancedButton->setText(tr("Basic..."));
    configurationTabs->insertTab(3, advancedOptionsTab, tr("Advanced Options"));
  } else if (! isAdvanced && advancedMode) {
    // Offer to move to advanced mode
    toggleAdvancedButton->setText(tr("Advanced..."));
    configurationTabs->removeTab(3); // Advanced Options tab
  }
  advancedMode = isAdvanced;
}


void configBackupsDialog::on_profileRecurringRadio_toggled(bool toggled) {
  int schedTabIndex; // for Scheduling tab
  if (advancedMode) {
    schedTabIndex = 5;
  } else {
    schedTabIndex = 4;
  }
  if (toggled) {
    configurationTabs->insertTab(schedTabIndex, schedulingTab, tr("Scheduling"));
  } else {
    configurationTabs->removeTab(schedTabIndex);
  }
}

/*
 * Configures the window appropriately for the set or one-time backup type.
 * WARNING: This function must be called after any set*Mode functions
 */
void configBackupsDialog::setType(int type) {
  switch (type) {
    case TYPE_SET:
      this->setWindowTitle(tr("Configure a Set Backup"));
      break;
    case TYPE_ONETIME:
      this->setWindowTitle(tr("Configure a One-Time Backup"));
      saveBackupToCombo->insertSeparator(99); // 99 -> separator appears last
      saveBackupToCombo->addItem(tr("Optical media"));
      if (guidedMode) {
        // Welcome tab is present
        configurationTabs->removeTab(3); // Automation tab
      } else {
        // Welcome tab has already been removed
        configurationTabs->removeTab(2); // Automation tab
      }
      break;
    default:
      this->setWindowTitle(tr("Configure a Backup"));
      break;
  }
}

QString configBackupsDialog::getKey() {
  return keyFile;
}

void configBackupsDialog::setKey(QString filename) {
  keyFile = filename;
  useKeyAuthenticationCheck->setChecked(true);
  useKeyAuthenticationCheck->setText( tr("Use key authentication: ") );
  QFileInfo fileinfo(keyFile);
  keyNameLabel->setText( fileinfo.completeBaseName() );  
}

void configBackupsDialog::clearKey() {
  keyFile = "";
  keyNameLabel->setText(keyFile);
  useKeyAuthenticationCheck->setText( tr("Use key authentication ") );
  useKeyAuthenticationCheck->setChecked(false);
}

bool configBackupsDialog::loadConfiguration(QString setName) {
  QSettings *config;
  if (type == TYPE_ONETIME) {
    config = get_onetime_configuration();
    setNameDescLabel->hide();
    setNameLabel->hide();
    setNameLineEdit->hide();
  } else {
    if (setName.isEmpty()) {
      return false;
    }
    setNameDescLabel->show();
    setNameLabel->show();
    setNameLineEdit->show();
    setNameLineEdit->setText(setName);
    config = get_set_configuration(setName);
    originalSetName = setName;
  }
  
  config->beginGroup("General");
  // FIXME: Import older versions here
  //config->value("Version", VERSION);
  // FIXME: Check me to determine if config type is correct
  //config->value("Type", type);
  switch ( config->value("Profile", 0).toInt() ) {
    case 0:
      profileContinuousRadio->setChecked(true);
      break;
    case 1:
      profileRecurringRadio->setChecked(true);
      break;
    case 2:
      profileManualRadio->setChecked(true);
      break;
    case 3:
      profileOneTimeRadio->setChecked(true);
      break;
    default: // just in case
      profileContinuousRadio->setChecked(true);
      break;
  }
  config->endGroup();
  
  
  config->beginGroup("IncludedItems");
  presetDeskopCheck->setChecked( config->value("Desktop", false).toBool() );
  presetDocumentsCheck->setChecked( config->value("Documents", false).toBool() );
  presetMusicCheck->setChecked( config->value("Music", false).toBool() );
  presetPicturesCheck->setChecked( config->value("Pictures", false).toBool() );
  presetVideosCheck->setChecked( config->value("Videos", false).toBool() );
  presetBookmarksCheck->setChecked( config->value("Bookmarks", false).toBool() );
  presetEmailCheck->setChecked( config->value("Emails", false).toBool() );
  presetSettingsCheck->setChecked( config->value("Settings", false).toBool() );
  config->endGroup();
    
  config->beginGroup("Destination");
  saveBackupToCombo->setCurrentIndex( config->value("DestinationType", 0).toInt() );
  
  config->beginGroup("Remote");
  protocolCombo->setCurrentIndex( config->value("Protocol", 0).toInt() );
  hostnameLineEdit->setText( config->value("Hostname", "").toString() );
  portSpin->setValue( config->value("Port", 22).toInt() );
  usernameLineEdit->setText( config->value("Username", "").toString() );
  passwordLineEdit->setText( config->value("Password", "").toString() );
  QString keyName = config->value("PublicKey", "").toString();
  if ( !keyName.isEmpty() ) {
    this->setKey(keyName);
  } else {
    this->clearKey();
  }
  
  config->endGroup(); // Remote
  
  locationLineEdit->setText( config->value("Destination", "").toString() );
  burnUsingCombo->setCurrentIndex( config->value("BurnDrive", 0).toInt() );
  config->endGroup(); // Destination
  
  timeSimpleFrequencyCombo->setCurrentIndex( config->value("Frequency", 2).toInt() );
  config->beginGroup("Frequency");
  timeSimpleMinuteSpin->setValue( config->value("Minute", 0).toInt() );
  // Get the value, split it by the ":" marker
  QStringList timelist = config->value("HourMinute", "0:0").toString().split(":");
  // Change the two QStrings in the list into ints in order create a QTime
  // for our string which was originally in "HOUR:MINUTES" format
  QTime time(timelist[0].toInt(), timelist[1].toInt());
  timeSimpleMinHourTimeEdit->setTime(time);
  timeSimpleDoWCombo->setCurrentIndex( config->value("DayOfWeek", 0).toInt() );
  timeSimpleDayCombo->setCurrentIndex( config->value("DayOfMonth", 0).toInt() );
  timeSimpleMonthCombo->setCurrentIndex( config->value("Month", 0).toInt() );
  config->endGroup(); // Frequency
  
  config->beginGroup("ManualConfiguration");
  timesManualMinuteLineEdit->setText( config->value("Minutes", "").toString() );
  timesManualHourLineEdit->setText( config->value("Hours", "").toString() );
  timesManualDoMLineEdit->setText( config->value("DaysOfMonth", "").toString() );
  timesManualMonthLineEdit->setText( config->value("Months", "").toString() );
  timesManualDoWLineEdit->setText( config->value("DaysOfWeek", "").toString() );
  config->endGroup(); // ManualConfiguration
    
  config->endGroup(); // Scheduling
  
  
  config->beginGroup("BackupType");
  switch ( config->value("Format", 0).toInt() ) {
    case 0:
      formatArchiveRadio->setChecked(true);
      break;
    case 1:
      formatCopyRadio->setChecked(true);
      break;
    default: // just in case
      formatArchiveRadio->setChecked(true);
      break;
  }
  
  int compression = config->value("Compression", -1).toInt();
  // -1 means no compression, >= 0 means compression, using this combobox index
  if (compression == -1) {
    compressionCheck->setChecked(false);
    compressionTypeCombo->setCurrentIndex(0);
  } else {
    compressionCheck->setChecked(true);
    compressionTypeCombo->setCurrentIndex(compression);
  }
  config->endGroup(); // BackupType
  
  
  config->beginGroup("Options");
  recursiveCheck->setChecked( config->value("Recursive", 1).toBool() );
  includeHiddenCheck->setChecked( config->value("IncludeHidden", 1).toBool() );
  followSymlinksCheck->setChecked( config->value("FollowSymlinks", 0).toBool() );
  switch ( config->value("Archiving", 1).toInt() ) {
    case 0:
      archivingCheck->setChecked(false);
      break;
    case 1:
      archivingCheck->setChecked(true);
      archivingKeepAllRadio->setChecked(true);
      break;
    case 2:
      archivingCheck->setChecked(true);
      archivingKeepOnlyRadio->setChecked(true);
      break;
    default: // just in case
      archivingCheck->setChecked(false);
      break;
  }
  archiveBackupSpin->setValue( config->value("ArchiveCount", 3).toInt() );
  config->endGroup(); // Options
  
  logger->log_message(LEVEL_DEBUG, tr("Configuration loaded for set: %1").arg(setName) );
  return true;
}

bool configBackupsDialog::saveConfiguration(QString setName) {
  QSettings *config;
  if (type == TYPE_ONETIME) {
    config = get_onetime_configuration();
  } else {
    if (setName.isEmpty()) {
      return false;
    }
    config = get_set_configuration(setName);
  }
  int profile;
  if (profileContinuousRadio->isChecked()) { profile = 0; }
  else if (profileRecurringRadio->isChecked()) { profile = 1; }
  else if (profileManualRadio->isChecked()) { profile = 2; }
  else if (profileOneTimeRadio->isChecked()) { profile = 3; }
  else { profile = 0; } // just in case
  
  config->beginGroup("General");
  config->setValue("Version", VERSION);
  config->setValue("Type", type);
  config->setValue("Profile", profile);
  config->endGroup();
  
  
  config->beginGroup("IncludedItems");
  // FIXME: Need to check "Home" if all of these are true
  config->setValue("Desktop", presetDeskopCheck->isChecked());
  config->setValue("Documents", presetDocumentsCheck->isChecked());
  config->setValue("Music", presetMusicCheck->isChecked());
  config->setValue("Pictures", presetPicturesCheck->isChecked());
  config->setValue("Videos", presetVideosCheck->isChecked());
  config->setValue("Bookmarks", presetBookmarksCheck->isChecked());
  config->setValue("Emails", presetEmailCheck->isChecked());
  config->setValue("Settings", presetSettingsCheck->isChecked());
  config->endGroup();
  
  
  config->beginGroup("Destination");
  config->setValue("DestinationType", saveBackupToCombo->currentIndex());
  
  config->beginGroup("Remote");
  config->setValue("Protocol", protocolCombo->currentIndex());
  config->setValue("Hostname", hostnameLineEdit->text());
  config->setValue("Port", portSpin->value());
  config->setValue("Username", usernameLineEdit->text());
  config->setValue("Password", passwordLineEdit->text());
  config->setValue("PublicKey", this->getKey());
  config->endGroup(); // Remote
  
  config->setValue("Destination", locationLineEdit->text());
  config->setValue("BurnDrive", burnUsingCombo->currentIndex());
  config->endGroup(); // Destination
  
  config->beginGroup("Scheduling");
  config->setValue("Frequency", timeSimpleFrequencyCombo->currentIndex());
  
  config->beginGroup("Frequency");
  config->setValue("Minute", timeSimpleMinuteSpin->value());
  config->setValue("HourMinute", timeSimpleMinHourTimeEdit->time().toString("h:m"));
  config->setValue("DayOfWeek", timeSimpleDoWCombo->currentIndex());
  config->setValue("DayOfMonth", timeSimpleDayCombo->currentIndex());
  config->setValue("Month", timeSimpleMonthCombo->currentIndex());
  config->endGroup(); // Frequency
  
  config->beginGroup("ManualConfiguration");
  config->setValue("Minutes", timesManualMinuteLineEdit->text());
  config->setValue("Hours", timesManualHourLineEdit->text());
  config->setValue("DaysOfMonth", timesManualDoMLineEdit->text());
  config->setValue("Months", timesManualMonthLineEdit->text());
  config->setValue("DaysOfWeek", timesManualDoWLineEdit->text());
  config->endGroup(); // ManualConfiguration
    
  config->endGroup(); // Scheduling
  
  
  int format;
  if (formatArchiveRadio->isChecked()) { format = 0; }
  else if (formatCopyRadio->isChecked()) { format = 1; }
  else { format = 0; } // just in case
  
  int compression;
  if (compressionCheck->isChecked()) { compression = compressionTypeCombo->currentIndex(); }
  else { compression = -1; }
  
  config->beginGroup("BackupType");
  config->setValue("Type", format);
  config->setValue("Compression", compression);
  config->endGroup(); // BackupType
  
  
  int archiving;
  if (not archivingCheck->isChecked()) { format = 0; }
  else if (archivingCheck->isChecked() && archivingKeepAllRadio->isChecked()) { format = 1; }
  else if (archivingCheck->isChecked() && archivingKeepOnlyRadio->isChecked()) { format = 1; }
  else { format = 0; } // just in case
  
  config->beginGroup("Options");
  config->setValue("Recursive", recursiveCheck->isChecked());
  config->setValue("IncludeHidden", includeHiddenCheck->isChecked());
  config->setValue("FollowSymlinks", followSymlinksCheck->isChecked());
  
  config->setValue("Archiving", archiving);
  config->setValue("ArchiveCount", archiveBackupSpin->value());
  config->endGroup(); // Options
  
  // Send message to log about changes
  switch (type) {
    case TYPE_SET:
      if ( QFile::exists( config->fileName() ) ) {
        // File exists: Updating existing set
        logger->log_message(LEVEL_DEBUG, tr("Creating new set configuration: %1").arg(setName) );
      } else {
        // Doesn't exist: Creating new set, or in the process of renaming one
        logger->log_message(LEVEL_DEBUG, tr("Saving changes to set configuration: %1").arg(setName) );
      }
      break;
    case TYPE_ONETIME:
      logger->log_message(LEVEL_DEBUG, tr("Creating new one-time backup configuration") );
      break;
  }
  
  config->sync();
  return true;
  
}

/* Configuration - Bottom Buttons */
void configBackupsDialog::on_toggleAdvancedButton_clicked() {
  this->setAdvancedMode(not advancedMode);
}

void configBackupsDialog::on_cancelButton_clicked() {
  this->reject();
}

void configBackupsDialog::on_okButton_clicked() {
  QString name = setNameLineEdit->text();
  // If this is true, then user requested to rename set
  if (originalSetName != name) {
    // saveConfiguration() will create a new set with the new name, so we must
    // cleanup by removing the set config file with the old name
    QFile::remove( get_set_configuration_path(originalSetName) );
    logger->log_message(LEVEL_INFO, tr("Renaming set %1 to %2").arg(originalSetName).arg(name) );
  }
  this->saveConfiguration(name);
  this->accept();
}

void configBackupsDialog::on_finishButton_clicked() {
  this->on_okButton_clicked();
}

void configBackupsDialog::on_backButton_clicked() {
  int index = configurationTabs->currentIndex();
  int (last) = configurationTabs->count() - 2;
  QString header;
  configurationTabs->setCurrentIndex(index-1);
  nextButton->setEnabled(true);
  if (index == 1) { // Switching to first page 
    header = tr("Configure a Backup - Welcome");
    backButton->setEnabled(false);
  } else {
    header = tr("Configure a Backup - Step %1/%2").arg(index-1).arg(last);
  }
  headerLabel->setText(header);
}

void configBackupsDialog::on_nextButton_clicked() {
  int index = configurationTabs->currentIndex();
  int lastPage = configurationTabs->count() - 2;
  QString header;
  configurationTabs->setCurrentIndex(index+1);
  backButton->setEnabled(true);
  if (index == lastPage) { // Switching to last page
    backButton->hide();
    cancelButton->hide();
    nextButton->hide();
    finishButton->show();
    finishButton->setDefault(true);
    header = tr("Configure a Backup - Finished!");
  } else {
    header = tr("Configure a Backup - Step %1/%2").arg(index+1).arg(lastPage);
  }
  headerLabel->setText(header);
}



/* Configuration - Welcome */
void configBackupsDialog::on_advancedOptionsCheck_toggled(bool checked) {
  this->setAdvancedMode(checked);
}


/* Configuration - Files & Folders */

void configBackupsDialog::on_presetBookmarksProgramsButton_clicked() {
  chooseProgramsDialog *cpwindow = new chooseProgramsDialog();
  cpwindow->setLabel( tr("Select the browsers whose bookmarks you would like to backup:") );
  cpwindow->addCheck( tr("Microsoft Windows Explorer") );
  cpwindow->addCheck( tr("Microsoft Internet Explorer") );
  cpwindow->addCheck( tr("Mozilla Firefox") );
  cpwindow->addCheck( tr("Opera") );
  cpwindow->addCheck( tr("Safari") );
  cpwindow->show();
}

void configBackupsDialog::on_presetEmailProgramsButton_clicked() {
  chooseProgramsDialog *cpwindow = new chooseProgramsDialog();
  cpwindow->setLabel( tr("All messages, contact and account settings stored in the selected E-mail clients will be backed up.") );
  cpwindow->addCheck( tr("Evolution") );
  cpwindow->addCheck( tr("Microsoft Outlook") );
  cpwindow->addCheck( tr("Mozilla Thunderbird") );
  cpwindow->addCheck( tr("Outlook Express") );
  cpwindow->addCheck( tr("Windows Mail") );
  cpwindow->show();
}

void configBackupsDialog::on_presetSettingsProgramsButton_clicked() {
  chooseProgramsDialog *cpwindow = new chooseProgramsDialog();
  
# if defined(WIN32)
  cpwindow->setLabel( tr("Select the Windows Registry hives you would like to backup:") );
  cpwindow->addCheck( tr("System settings (HKEY_CURRENY_USER)") );
  cpwindow->addCheck( tr("User settings (HKEY_LOCAL_MACHINE)") );
# elif defined(__APPLE__)
  cpwindow->setLabel( tr("Select the items you would like to backup:") );
  cpwindow->addCheck( tr("System settings (/Library/Preferences)") );
  cpwindow->addCheck( tr("User settings (~/Library/Preferences)") );
# elif defined(__linux__)
  cpwindow->setLabel( tr("Select which configuration folders you would like to backup:") );
  cpwindow->addCheck( tr("User settings (~/.local)") );
  cpwindow->addCheck( tr("User settings (~/.config)") );
#endif
  cpwindow->show();
}

void configBackupsDialog::on_addFilesButton_clicked() {
  QStringList filenames = QFileDialog::getOpenFileNames(this,
                                                        tr("Select Files"),
                                                        QString::null,
                                                        QString::null);
  foreach (QString filename, filenames) {
    QModelIndex index = pathsTreeView->selectionModel()->currentIndex();
    QAbstractItemModel *model = pathsTreeView->model();
    if (!model->insertRow(index.row()+1, index.parent())) {
      return;
    }
    QModelIndex child = model->index(index.row()+1, 0, index.parent());
    model->setData(child, QVariant(filename), Qt::DisplayRole);
    child = model->index(index.row()+1, 1, index.parent());
    model->setData(child, QVariant( tr("OK") ), Qt::DisplayRole);
  }
}

void configBackupsDialog::on_addFoldersButton_clicked() {
  QString directory = QFileDialog::getExistingDirectory(this,
                                                        tr("Select a Folder"),
                                                        QString::null,
                                                        QFileDialog::ShowDirsOnly | QFileDialog::DontResolveSymlinks);
  if (directory.isEmpty()) {
    return;
  }
  // FIXME: Turn this into a function?
  QModelIndex index = pathsTreeView->selectionModel()->currentIndex();
  QAbstractItemModel *model = pathsTreeView->model();
  if (!model->insertRow(index.row()+1, index.parent())) {
    return;
  }
  QModelIndex child = model->index(index.row()+1, 0, index.parent());
  // FIXME: Actually check
  model->setData(child, QVariant(directory), Qt::DisplayRole);
  child = model->index(index.row()+1, 1, index.parent());
  model->setData(child, QVariant(tr("OK")), Qt::DisplayRole);
}

void configBackupsDialog::on_removeItemsButton_clicked() {
  int offset = 0;
  QModelIndexList indexList = pathsTreeView->selectionModel()->selectedRows(0);
  qSort(indexList);
  QAbstractItemModel *model = pathsTreeView->model();
  foreach (QModelIndex index, indexList) {
    // Trouble: index.row() doesn't update itself after a row has been removed.
    model->removeRow(index.row()-offset, index.parent());
    // Solution: Create a row offset
    offset++;
  }
}

void configBackupsDialog::on_presetHomeCheck_toggled(bool checked) {
  presetDeskopCheck->setChecked(checked);
  presetDocumentsCheck->setChecked(checked);
  presetMusicCheck->setChecked(checked);
  presetPicturesCheck->setChecked(checked);
  presetVideosCheck->setChecked(checked);
  presetDeskopCheck->setEnabled(not checked);
  presetDocumentsCheck->setEnabled(not checked);
  presetMusicCheck->setEnabled(not checked);
  presetPicturesCheck->setEnabled(not checked);
  presetVideosCheck->setEnabled(not checked);
  }


/* Configuration - Destination */
void configBackupsDialog::on_saveBackupToCombo_currentIndexChanged(int index) {
  QString location;
  QString hostname;
  locationLineEdit->clear();
  hostnameLineEdit->clear();
  
  switch (index) {
    case 0: // Local disk + removable media
      destinationStackedWidget->setCurrentIndex(0);
      break;
    case 1: // Internet
      destinationStackedWidget->setCurrentIndex(1);
      break;
    //case 2: separator
    case 3: // Optical media
      destinationStackedWidget->setCurrentIndex(2);
      break;
    default: // something goes wrong, show local
      destinationStackedWidget->setCurrentIndex(0);
      break;
  }
}

void configBackupsDialog::on_useKeyAuthenticationCheck_clicked() {
  if ( useKeyAuthenticationCheck->isChecked() ) {
    on_changeKeyButton_clicked();
  } else {
    this->clearKey();
  }
}

void configBackupsDialog::on_changeKeyButton_clicked() {
  QString filename = QFileDialog::getOpenFileName(this,
                                                  tr("Select a Key"),
                                                  QString::null,
                                                  QString::null);
  if (filename.isEmpty()) {
    // if a key was set prior to clicking "Change key", don't erase that filename
    if ( this->getKey().isEmpty() ) { this->clearKey(); }
    return;
  }
  
  this->setKey(filename);
}

void configBackupsDialog::on_locationBrowseButton_clicked() {
  QString directory = QFileDialog::getExistingDirectory(this,
                                                        tr("Select a Folder"),
                                                        QString::null,
                                                        QFileDialog::ShowDirsOnly | QFileDialog::DontResolveSymlinks);
  if (directory.isEmpty()) {
    return;
  }
  locationLineEdit->setText(directory);
}

void configBackupsDialog::on_showPasswordCheck_toggled(bool checked) {
  if (checked == true) {
    passwordLineEdit->setEchoMode(QLineEdit::Normal);
  } else {
    passwordLineEdit->setEchoMode(QLineEdit::Password);
  }
}



/* Configuration - Triggers */
void configBackupsDialog::on_timeSimpleFrequencyCombo_currentIndexChanged(int index) {
  switch (index) {
    case 0: //Hourly
      timeStackedWidget->setCurrentIndex(0);
      timeSimpleMinuteSpin->show();
      timeSimpleMinuteLabel->show();
      timeSimpleMinHourTimeEdit->hide();
      timeSimpleMinHourLabel->hide();
      timeSimpleDoWCombo->hide();
      timeSimpleDoWLabel->hide();
      timeSimpleDayCombo->hide();
      timeSimpleDayLabel->hide();
      timeSimpleMonthCombo->hide();
      timeSimpleMonthLabel->hide();
      break;
    case 1: //Daily
      timeStackedWidget->setCurrentIndex(0);
      timeSimpleMinuteSpin->hide();
      timeSimpleMinuteLabel->hide();
      timeSimpleMinHourTimeEdit->show();
      timeSimpleMinHourLabel->show();
      timeSimpleDoWCombo->hide();
      timeSimpleDoWLabel->hide();
      timeSimpleDayCombo->hide();
      timeSimpleDayLabel->hide();
      timeSimpleMonthCombo->hide();
      timeSimpleMonthLabel->hide();
      break;
    case 2: //Weekly
      timeStackedWidget->setCurrentIndex(0);
      timeSimpleMinuteSpin->hide();
      timeSimpleMinuteLabel->hide();
      timeSimpleMinHourTimeEdit->show();
      timeSimpleMinHourLabel->show();
      timeSimpleDoWCombo->show();
      timeSimpleDoWLabel->show();
      timeSimpleDayCombo->hide();
      timeSimpleDayLabel->hide();
      timeSimpleMonthCombo->hide();
      timeSimpleMonthLabel->hide();
      break;
    case 3: //Monthly
      timeStackedWidget->setCurrentIndex(0);
      timeSimpleMinuteSpin->hide();
      timeSimpleMinuteLabel->hide();
      timeSimpleMinHourTimeEdit->show();
      timeSimpleMinHourLabel->show();
      timeSimpleDoWCombo->hide();
      timeSimpleDoWLabel->hide();
      timeSimpleDayCombo->show();
      timeSimpleDayLabel->show();
      timeSimpleMonthCombo->hide();
      timeSimpleMonthLabel->hide();
      break;
    case 4: //Custom
      timeStackedWidget->setCurrentIndex(1);
      break;
    default: // something goes wrong, show all
      timeStackedWidget->setCurrentIndex(0);
      timeSimpleMinuteSpin->show();
      timeSimpleMinuteLabel->show();
      timeSimpleMinHourTimeEdit->show();
      timeSimpleMinHourLabel->show();
      timeSimpleDoWCombo->show();
      timeSimpleDoWLabel->show();
      timeSimpleDayCombo->show();
      timeSimpleDayLabel->show();
      timeSimpleMonthCombo->show();
      timeSimpleMonthLabel->show();
      break;
  }
}

/* Configuration - Backup Type */
void configBackupsDialog::on_compressionCheck_toggled(bool checked) {
  compressionTypeCombo->setEnabled(checked);
}

/*******************************************
 ************* Choose Programs *************
 *******************************************/
chooseProgramsDialog::chooseProgramsDialog(QDialog *parent) {
  setupUi(this); // this sets up GUI
  prorgamsVerticalLayout->setEnabled(true);
}

QCheckBox *chooseProgramsDialog::addCheck(QString label) {
  QCheckBox *check = new QCheckBox(label);
  prorgamsVerticalLayout->addWidget(check);
  return check;
}

void chooseProgramsDialog::setLabel(QString label) {
  instructionalLabel->setText(label);
}


void chooseProgramsDialog::on_okButton_clicked() {
  this->accept();
}



