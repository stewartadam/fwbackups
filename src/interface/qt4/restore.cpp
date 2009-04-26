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
#include "restore.h"

restoreDialog::restoreDialog(QDialog *parent) {
  guidedMode = false;
  setupUi(this); // this sets up GUI
  
  this->setGuidedMode(true);
  
  /* FIXME: Add all sets as options in restoreFromCombo */
  
  restoreFromCombo->setCurrentIndex(0); // default to local drive
  this->on_restoreFromCombo_currentIndexChanged(0); // force refresh
  
}

void restoreDialog::setGuidedMode(bool isGuided) {
  QString header;
  if (isGuided && ! guidedMode) {
    configurationTabs->insertTab(0, welcomeTab, tr("Welcome"));
    configurationTabs->insertTab(3, finishedTab, tr("Finished!"));
    configurationTabs->setCurrentIndex(0);
    configurationTabs->tabBar()->hide();
    startRestoreButton->hide();
    backButton->show();
    cancelButton->show();
    nextButton->show();
    backButton->setEnabled(false);
    header = tr("Restore Files, Folders and Settings - Welcome");
    headerLabel->setText(header);
  } else if (! isGuided && guidedMode) {
    configurationTabs->removeTab(0);
    configurationTabs->removeTab(2); // 3 but since we already removed one...
    configurationTabs->tabBar()->show();
    startRestoreButton->hide();
    startRestoreButton->setDefault(true);
    backButton->hide();
    cancelButton->show();
    nextButton->hide();
    header = tr("Restore Files, Folders and Settings");
    headerLabel->setText(header);
  }
  guidedMode = isGuided;
}



/* Configuration - Bottom Buttons */
void restoreDialog::on_cancelButton_clicked() {
  this->reject();
}

void restoreDialog::on_startRestoreButton_clicked() {
  this->accept();
}

void restoreDialog::on_backButton_clicked() {
  int index = configurationTabs->currentIndex();
  char buf[1]; // FIXME: do we have to clean this up?
  QString header;
  configurationTabs->setCurrentIndex(index-1);
  nextButton->setEnabled(true);
  if (index == 1) { // Switching to first page 
    header = tr("Restore Files, Folders and Settings - Welcome");
    backButton->setEnabled(false);
  } else {
    header = tr("Restore Files, Folders and Settings - Step ");
    sprintf(buf, "%i", index-1);
    header.append(buf);
    header.append("/2");
  }
  headerLabel->setText(header);
}

void restoreDialog::on_nextButton_clicked() {
  int index = configurationTabs->currentIndex();
  int lastPage;
  char buf[1]; //fixme: do we have to clean this up?
  QString header;
  configurationTabs->setCurrentIndex(index+1);
  backButton->setEnabled(true);
  lastPage = 2;
  if (index == lastPage) { // Switching to last page
    backButton->hide();
    cancelButton->hide();
    nextButton->hide();
    startRestoreButton->show();
    startRestoreButton->setDefault(true);
    header = tr("Restore Files, Folders and Settings - Finished!");
  } else {
    header = tr("Restore Files, Folders and Settings - Step ");
    // +2 because we need to +1 offset
    sprintf(buf, "%i", index+1);
    header.append(buf);
    header.append("/2");
  }
  headerLabel->setText(header);
}



/* Configuration - Destination */
void restoreDialog::setVisible_remoteGrid(bool isVisible) {
  if (isVisible == true) {
    remoteGroupBox->show();
  } else {
    remoteGroupBox->hide();
    showPasswordCheck->setChecked(false);
  }
}

void restoreDialog::on_restoreFromCombo_currentIndexChanged(int index) {
  QString location;
  QString hostname;
  folderLineEdit->clear();
  hostnameLineEdit->clear();
  
  switch (index) {
    case 0: // Local disk + removable media
      this->setVisible_remoteGrid(false);
      folderLabel->show();
      folderBrowseButton->setEnabled(true);
      folderBrowseButton->show();
      folderLineEdit->setEnabled(true);
      folderLineEdit->show();
      protocolCombo->setEnabled(true);
      hostnameLineEdit->setEnabled(true);
      portSpin->setEnabled(true);
      break;
    case 1: // Internet
      this->setVisible_remoteGrid(true);
      folderLabel->show();
      folderBrowseButton->setEnabled(false);
      folderBrowseButton->show();
      folderLineEdit->setEnabled(true);
      folderLineEdit->show();
      protocolCombo->setEnabled(true);
      hostnameLineEdit->setEnabled(true);
      portSpin->setEnabled(true);
      break;
    case 2: // fwbackups server
      this->setVisible_remoteGrid(true);
      folderLabel->show();
      folderBrowseButton->show();
      folderBrowseButton->setEnabled(false);
      folderLineEdit->show();
      folderLineEdit->setEnabled(false);
      location = tr("<Account Storage>");
      folderLineEdit->setText(location);
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
      folderLabel->hide();
      folderLineEdit->hide();
      folderBrowseButton->hide();
      break;
    default: // something goes wrong, show all
      this->setVisible_remoteGrid(true);
      folderLabel->show();
      folderLineEdit->setEnabled(true);
      folderLineEdit->show();
      folderBrowseButton->setEnabled(true);
      folderBrowseButton->show();
      protocolCombo->setEnabled(true);
      hostnameLineEdit->setEnabled(true);
      portSpin->setEnabled(true);
      break;
  }
}

void restoreDialog::on_useKeyAuthenticationCheck_toggled(bool checked) {
  if (checked) {
    //changeKeyButton->show();
    on_changeKeyButton_clicked();
  } else {
    QString string = tr("Use key authentication");
    useKeyAuthenticationCheck->setText(string);
    //changeKeyButton->hide();
  }
}

void restoreDialog::on_changeKeyButton_clicked() {
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

void restoreDialog::on_folderBrowseButton_clicked() {
  QString directory = QFileDialog::getExistingDirectory(this,
                                                        tr("Select a Folder"),
                                                        QString::null,
                                                        QFileDialog::ShowDirsOnly | QFileDialog::DontResolveSymlinks);
  if (directory.isEmpty()) {
    return;
  }
  folderLineEdit->setText(directory);
}

void restoreDialog::on_showPasswordCheck_toggled(bool checked) {
  if (checked == true) {
    passwordLineEdit->setEchoMode(QLineEdit::Normal);
  } else {
    passwordLineEdit->setEchoMode(QLineEdit::Password);
  }
}
