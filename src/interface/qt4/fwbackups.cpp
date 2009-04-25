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
#include <sys/stat.h>
#include <qmessagebox.h>
// fwbackups
#include "common.h"
#include "configBackup.h"
#include "logger.h"
// Local
#include "fwbackups.h"


/*******************************************
 ***************** Main App ****************
 *******************************************/

fwbackupsApp::fwbackupsApp(QMainWindow *parent)
{
  setupUi(this); // this sets up GUI
  
  this->switch_overview();
  
  // This does the QStackedWidget switching
  connect(actionOverview, SIGNAL(activated()), this, SLOT(switch_overview()));
  connect(actionOverview_2, SIGNAL(activated()), this, SLOT(switch_overview()));
  connect(actionBackup_Sets, SIGNAL(activated()), this, SLOT(switch_backupsets()));
  connect(actionBackup_Sets_2, SIGNAL(activated()), this, SLOT(switch_backupsets()));
  connect(actionOperations, SIGNAL(activated()), this, SLOT(switch_operations()));
  connect(actionOperations_2, SIGNAL(activated()), this, SLOT(switch_operations()));
  connect(actionLog_Viewer, SIGNAL(activated()), this, SLOT(switch_logviewer()));
  connect(actionLog_Viewer_2, SIGNAL(activated()), this, SLOT(switch_logviewer()));
  connect(actionOne_Time_Backup, SIGNAL(activated()), this, SLOT(show_one_time_backup()));
  connect(actionOne_Time_Backup_2, SIGNAL(activated()), this, SLOT(show_one_time_backup()));
  connect(actionRestore, SIGNAL(activated()), this, SLOT(switch_restore()));
  connect(actionRestore_2, SIGNAL(activated()), this, SLOT(switch_restore()));
  connect(actionPreferences, SIGNAL(activated()), this, SLOT(show_preferences()));
  connect(qApp, SIGNAL(aboutToQuit()), this, SLOT(cleanup()));
  
  this->on_refreshLogButton_clicked();
  log_message(LEVEL_INFO, tr("fwbackups administrator started"));
  // Connecting our own slot to the logger
  // This will enable us to update the GUI when submitting a new log message
  //void (*pointer_function)(QString);
  //pointer_function = &fwbackupsApp::new_log_message
  //log_connect_function(pointer_function);
}

void fwbackupsApp::cleanup() {
  log_message(LEVEL_INFO, tr("fwbackups administrator closed"));
}

void fwbackupsApp::on_actionAbout_activated()
{
  QMessageBox::about(this, tr("About fwbackups"),
                     tr("<b>fwbackups</b> v1.44<br />\n"
                     "<span style=\"font-weight: normal;\">A feature-rich user backups program<br />\n"
                     "Copyright &copy; 2005 - 2009 Stewart Adam<br /><br />\n"
                     "<i>Visit <a href=\"http://www.fwbackups.com\">www.fwbackups.com</a> for more information and product updates.</i></span>"));
}

void fwbackupsApp::on_actionQuit_activated()
{
  qApp->closeAllWindows();
}

void fwbackupsApp::on_newSetButton_clicked()
{
  configBackupsDialog *cwindow = new configBackupsDialog;
  cwindow->setGuidedMode(false);
  cwindow->setAdvancedMode(false);
  cwindow->setType(TYPE_SET);
  cwindow->show();
}

void fwbackupsApp::fwbackupsApp::clear_toolbar_status() {
  actionOverview_2->setChecked(false);
  actionBackup_Sets_2->setChecked(false);
  actionOne_Time_Backup_2->setChecked(false);
  actionRestore_2->setChecked(false);
  actionOperations_2->setChecked(false);
  actionLog_Viewer_2->setChecked(false);
}

void fwbackupsApp::switch_overview()
{
  this->clear_toolbar_status();
  mainStackedWidget->setCurrentWidget(overviewPage);
  actionOverview_2->setChecked(true);
}

void fwbackupsApp::switch_backupsets()
{
  this->clear_toolbar_status();
  mainStackedWidget->setCurrentWidget(backupSetsPage);
  actionBackup_Sets_2->setChecked(true);
}

void fwbackupsApp::show_one_time_backup()
{
  configBackupsDialog *cwindow = new configBackupsDialog;
  cwindow->setGuidedMode(true);
  cwindow->setAdvancedMode(false);
  cwindow->setType(TYPE_ONETIME);
  cwindow->show();
}

void fwbackupsApp::switch_restore()
{
  this->clear_toolbar_status();
  mainStackedWidget->setCurrentWidget(restorePage);
  actionRestore_2->setChecked(true);
}

void fwbackupsApp::switch_operations()
{
  this->clear_toolbar_status();
  mainStackedWidget->setCurrentWidget(operationsPage);
  actionOperations_2->setChecked(true);
}

void fwbackupsApp::switch_logviewer()
{
  this->clear_toolbar_status();
  mainStackedWidget->setCurrentWidget(logViewerPage);
  actionLog_Viewer_2->setChecked(true);
}

void fwbackupsApp::show_preferences()
{
  prefsWindow *pwindow = new prefsWindow;
  pwindow->show();
}

void fwbackupsApp::on_saveLogButton_clicked() {
  QString filename = QFileDialog::getSaveFileName(this,
                                                  tr("Select Files"),
                                                  QString::null,
                                                  QString::null);
  if (filename.isEmpty()) {
    return;
  }
  QFile destination(filename);
  // FIXME: We should append messages to the log as they are generated, not in bulk at quit time
  // FIXME: Accents and other special characters don't work
  if (destination.open(QIODevice::WriteOnly | QIODevice::Text | QIODevice::Truncate)) {
    QTextStream textStream(&destination);
    textStream << logTextEdit->toPlainText();
  }
  destination.close();
}

void fwbackupsApp::on_clearLogButton_clicked() {
  QFile file( get_log_location() );
  file.open(QIODevice::WriteOnly | QIODevice::Text | QIODevice::Truncate);
  file.close();
  logTextEdit->clear();
}

void fwbackupsApp::on_refreshLogButton_clicked() {
  QFileInfo logInfo;
  QString logLocation = get_log_location();
  logTextEdit->clear();
  QFile file(logLocation);
  QString line;
  if (file.open(QIODevice::ReadOnly | QIODevice::Text)) {
    QTextStream textStream(&file);
    while (!textStream.atEnd()) {
      line = textStream.readLine(); // this excludes the ending '\n'
      logTextEdit->append(line);
    }
    file.close();
  } else {
  // FIXME: Handle error here
  logTextEdit->append(tr("The log file ") + logLocation + tr(" does not exist!"));
  }
}

/*******************************************
 *************** Preferences ***************
 *******************************************/

prefsWindow::prefsWindow(QDialog *parent)
{
  setupUi(this); // this sets up GUI
}

void prefsWindow::on_closeButton_clicked() {
  this->reject();
}
