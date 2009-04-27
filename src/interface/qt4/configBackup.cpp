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

// Global
// fwbackups
#include "config.h"
// interface - qt4
#include "custom_widgets.h"
// Local
#include "configBackup.h"

configBackupsDialog::configBackupsDialog(QDialog *parent) {
  advancedMode = true;
  /* "not" is a workaround for the if check that ensures guidedMode is not true
   * when calling setGuidedMode with a parmeter of true */
  guidedMode = not get_settings()->value("guidedMode", true).toBool();
  setupUi(this); // this sets up GUI
  
  // Double negative makes a positive! Now guidedMode != isGuided
  this->setGuidedMode(not guidedMode);
  this->setAdvancedMode(true);
  
  timeSimpleFrequencyCombo->setCurrentIndex(2); // default to "Weekly" frequency
  compressionTypeCombo->setEnabled(false); // default to no compression
  startPeriodicallyRadio->setChecked(true); // default to periodic backup
  saveBackupToCombo->setCurrentIndex(0); // default to local drive
  this->on_saveBackupToCombo_currentIndexChanged(0); // force refresh
  
  burnUsingCombo->hide();
  burnUsingLabel->hide();
  
  QStringList headers;
  headers << tr("Location") << tr("Status");
  TreeModel *pathsTreeModel = new TreeModel(headers);
  pathsTreeView->setModel(pathsTreeModel);
  // Setup the first column nicely
  pathsTreeView->setColumnWidth(1, 35);
  pathsTreeView->setColumnWidth(0, 415);
}

void configBackupsDialog::setGuidedMode(bool isGuided) {
  QString header;
  if (isGuided && ! guidedMode) {
    configurationTabs->insertTab(0, welcomeTab, tr("Welcome"));
    configurationTabs->insertTab(6, finishedTab, tr("Finished!"));
    configurationTabs->setCurrentIndex(0);
    configurationTabs->tabBar()->hide();
    finishButton->hide();
    toggleAdvancedButton->hide();
    okButton->hide();
    backButton->show();
    cancelButton->show();
    nextButton->show();
    backButton->setEnabled(false);
    header = tr("Configure a Backup - Welcome");
    headerLabel->setText(header);
  } else if (! isGuided && guidedMode) {
    configurationTabs->removeTab(0);
    configurationTabs->removeTab(5); // 6 but since we already removed one...
    configurationTabs->tabBar()->show();
    finishButton->hide();
    backButton->hide();
    toggleAdvancedButton->show();
    cancelButton->show();
    okButton->show();
    okButton->setDefault(true);
    nextButton->hide();
    header = tr("Configure a Backup");
    headerLabel->setText(header);
  }
  guidedMode = isGuided;
}

void configBackupsDialog::setAdvancedMode(bool isAdvanced) {
  if (isAdvanced && ! advancedMode) {
    toggleAdvancedButton->setText(tr("Basic..."));
    configurationTabs->insertTab(4, modeFormatTab, tr("Backup Type"));
    configurationTabs->insertTab(5, optionsTab, tr("Options"));
  } else if (! isAdvanced && advancedMode) {
    toggleAdvancedButton->setText(tr("Advanced..."));
    if (guidedMode) {
      configurationTabs->removeTab(4);
      configurationTabs->removeTab(4); // 5 but since we already removed one...
    } else {
      configurationTabs->removeTab(3);
      configurationTabs->removeTab(3); // 4 but since we already removed one...
    }
  }
  advancedMode = isAdvanced;
}

void configBackupsDialog::setType(int type) {
  switch (type) {
    case TYPE_SET:
      this->setWindowTitle(tr("Configure a Set Backup"));
      break;
    case TYPE_ONETIME:
      this->setWindowTitle(tr("Configure a One-Time Backup"));
      saveBackupToCombo->insertSeparator(9999);
      saveBackupToCombo->addItem(tr("Optical media"));
      break;
    default:
      this->setWindowTitle(tr("Configure a Backup"));
      break;
  }
}

/* Configuration - Bottom Buttons */
void configBackupsDialog::on_toggleAdvancedButton_clicked() {
  this->setAdvancedMode(not advancedMode);
}

void configBackupsDialog::on_cancelButton_clicked() {
  this->reject();
}

void configBackupsDialog::on_okButton_clicked() {
  this->accept();
}

void configBackupsDialog::on_finishButton_clicked() {
  this->accept();
}

void configBackupsDialog::on_backButton_clicked() {
  int index = configurationTabs->currentIndex();
  char buf[1]; // FIXME: do we have to clean this up?
  QString header;
  configurationTabs->setCurrentIndex(index-1);
  nextButton->setEnabled(true);
  if (index == 1) { // Switching to first page 
    header = tr("Configure a Backup - Welcome");
    backButton->setEnabled(false);
  } else {
    header = tr("Configure a Backup - Step ");
    sprintf(buf, "%i", index-1);
    header.append(buf);
    if (advancedMode == true) { 
      header.append("/5");
    } else {
      header.append("/3");
    }
  }
  headerLabel->setText(header);
}

void configBackupsDialog::on_nextButton_clicked() {
  int index = configurationTabs->currentIndex();
  int lastPage;
  char buf[1]; //fixme: do we have to clean this up?
  QString header;
  configurationTabs->setCurrentIndex(index+1);
  backButton->setEnabled(true);
  if (advancedMode == true) {
    lastPage = 5;
  } else {
    lastPage = 3;
  }
  if (index == lastPage) { // Switching to last page
    backButton->hide();
    cancelButton->hide();
    nextButton->hide();
    finishButton->show();
    finishButton->setDefault(true);
    header = tr("Configure a Backup - Finished!");
  } else {
    header = tr("Configure a Backup - Step ");
    // +2 because we need to +1 offset
    sprintf(buf, "%i", index+1);
    header.append(buf);
    if (advancedMode == true)
    {
      header.append("/5");
    } else {
      header.append("/3");
    }
  }
  headerLabel->setText(header);
}



/* Configuration - Welcome */
void configBackupsDialog::on_advancedOptionsCheck_toggled(bool checked) {
  this->setAdvancedMode(checked);
}


/* Configuration - Files & Folders */
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
    model->setData(child, QVariant("OK"), Qt::DisplayRole);
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
  // This adds the checked items, inactively, to the treeview.
  // This might confuse users more than help them; keep it disabled for now.
  /*if (checked) {
    QAbstractItemModel *model = pathsTreeView->model();
    // Adds "Home" as first entry
    if (!model->insertRow(0, QModelIndex())) {
      return;
    }
    QModelIndex index = model->index(0, 0, QModelIndex());
    // FIXME: Actually check
    model->setData(index, QVariant("Home"), Qt::DisplayRole);
    index = model->index(0, 1, index.parent());
    model->setData(index, QVariant("OK"), Qt::DisplayRole);
    
    // Adds each subitem as children
    // FIXME: Why does this not work when column > 0?
    // Workaround: Reset index to use column 0
    index = model->index(0, 0, QModelIndex());
    QStringList stringList;
    stringList << "Desktop" << "Documents" << "Music" << "Pictures" << "Videos";
    foreach (QString string, stringList) {
      if (!model->insertRow(model->rowCount(index), index)) {
        return;
      }
      QModelIndex child = model->index(model->rowCount(index)-1, 0, index);
      model->setData(child, QVariant(string), Qt::DisplayRole);
      child = model->index(model->rowCount(index)-1, 1, index);
      model->setData(child, QVariant("OK"), Qt::DisplayRole);
      pathsTreeView->selectionModel()->setCurrentIndex(child,
                                                       QItemSelectionModel::ClearAndSelect);
    }
  } else {
    QAbstractItemModel *model = pathsTreeView->model();
    model->removeRow(0, QModelIndex());
  }*/
}


/* Configuration - Destination */
void configBackupsDialog::setVisible_remoteGrid(bool isVisible) {
  if (isVisible == true) {
    remoteGroupBox->show();
  } else {
    remoteGroupBox->hide();
    showPasswordCheck->setChecked(false);
  }
}

void configBackupsDialog::on_saveBackupToCombo_currentIndexChanged(int index) {
  QString location;
  QString hostname;
  locationLineEdit->clear();
  hostnameLineEdit->clear();
  
  switch (index) {
    case 0: // Local disk + removable media
      this->setVisible_remoteGrid(false);
      burnUsingCombo->hide();
      burnUsingLabel->hide();
      locationLabel->show();
      locationBrowseButton->setEnabled(true);
      locationBrowseButton->show();
      locationLineEdit->setEnabled(true);
      locationLineEdit->show();
      protocolCombo->setEnabled(true);
      hostnameLineEdit->setEnabled(true);
      portSpin->setEnabled(true);
      break;
    case 1: // Internet
      this->setVisible_remoteGrid(true);
      burnUsingCombo->hide();
      burnUsingLabel->hide();
      locationLabel->show();
      locationBrowseButton->setEnabled(false);
      locationBrowseButton->show();
      locationLineEdit->setEnabled(true);
      locationLineEdit->show();
      protocolCombo->setEnabled(true);
      hostnameLineEdit->setEnabled(true);
      portSpin->setEnabled(true);
      break;
    case 2: // fwbackups server
      this->setVisible_remoteGrid(true);
      burnUsingCombo->hide();
      burnUsingLabel->hide();
      locationLabel->show();
      locationBrowseButton->show();
      locationBrowseButton->setEnabled(false);
      locationLineEdit->show();
      locationLineEdit->setEnabled(false);
      location = tr("<Account Storage>");
      locationLineEdit->setText(location);
      hostname = "accounts.fwbackups.com";
      hostnameLineEdit->setText(hostname);
      portSpin->setValue(22);
      protocolCombo->setCurrentIndex(0);
      protocolCombo->setEnabled(false);
      hostnameLineEdit->setEnabled(false);
      portSpin->setEnabled(false);
      break;
    //case 3: separator
    case 4: // Optical media
      this->setVisible_remoteGrid(false);
      burnUsingCombo->show();
      burnUsingLabel->show();
      locationLabel->hide();
      locationLineEdit->hide();
      locationBrowseButton->hide();
      break;
    default: // something goes wrong, show all
      this->setVisible_remoteGrid(true);
      locationLabel->show();
      locationLineEdit->setEnabled(true);
      locationLineEdit->show();
      locationBrowseButton->setEnabled(true);
      locationBrowseButton->show();
      burnUsingCombo->show();
      burnUsingLabel->show();
      protocolCombo->setEnabled(true);
      hostnameLineEdit->setEnabled(true);
      portSpin->setEnabled(true);
      break;
  }
}

void configBackupsDialog::on_useKeyAuthenticationCheck_toggled(bool checked) {
  if (checked) {
    //changeKeyButton->show();
    on_changeKeyButton_clicked();
  } else {
    QString string = tr("Use key authentication");
    useKeyAuthenticationCheck->setText(string);
    //changeKeyButton->hide();
  }
}

void configBackupsDialog::on_changeKeyButton_clicked() {
  QString string = tr("Use key authentication: ");
  QString filename = QFileDialog::getOpenFileName(this,
                                                  tr("Select a Key"),
                                                  QString::null,
                                                  QString::null);
  if (filename.isEmpty()) {
    /* FIXME: This unchecks the button on every cancel, not just the first */
    useKeyAuthenticationCheck->setChecked(false);
    return;
  }
  /* FIXME: Run file size checks and determine key type */
  QFileInfo fileinfo(filename);
  string += fileinfo.baseName();
  useKeyAuthenticationCheck->setText(string);
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
void configBackupsDialog::on_startPeriodicallyRadio_toggled(bool checked) {
  if (checked) {
    timeLine->setEnabled(true);
    timeDescLabel->setEnabled(true);
    timeFrequencyLabel->setEnabled(true);
    timeSimpleFrequencyCombo->setEnabled(true);
    timeStackedWidget->setEnabled(true);
  } else {
    timeLine->setEnabled(false);
    timeDescLabel->setEnabled(false);
    timeFrequencyLabel->setEnabled(false);
    timeSimpleFrequencyCombo->setEnabled(false);
    timeStackedWidget->setEnabled(false);
  }
}

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
    case 4: //Yearly
      timeStackedWidget->setCurrentIndex(0);
      timeSimpleMinuteSpin->hide();
      timeSimpleMinuteLabel->hide();
      timeSimpleMinHourTimeEdit->show();
      timeSimpleMinHourLabel->show();
      timeSimpleDoWCombo->hide();
      timeSimpleDoWLabel->hide();
      timeSimpleDayCombo->show();
      timeSimpleDayLabel->show();
      timeSimpleMonthCombo->show();
      timeSimpleMonthLabel->show();
      break;
    case 5: //Custom
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
