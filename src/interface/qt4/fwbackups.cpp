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

#include <sys/stat.h>
#include <qmessagebox.h>

#include "configBackup.h"
#include "restore.h"

#include "common.h"
#include "config.h"
#include "logger.h"

#include "fwbackups.h"


/*******************************************
 ***************** Main App ****************
 *******************************************/

fwbackupsApp::fwbackupsApp(QMainWindow *parent) {
  setupUi(this); // this sets up GUI
  
  this->switch_overview();
  
  
  // Action handlers
  connect(qApp, SIGNAL(aboutToQuit()), this, SLOT(cleanup()));
  // This does the QStackedWidget switching (toolbar & View menu)
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
  connect(actionRestore, SIGNAL(activated()), this, SLOT(show_restore()));
  connect(actionRestore_2, SIGNAL(activated()), this, SLOT(show_restore()));
  
  this->on_refreshLogButton_clicked();
  log_message(LEVEL_INFO, tr("fwbackups administrator started"));
  // Connecting our own slot to the logger
  // This will enable us to update the GUI when submitting a new log message
  //void (*pointer_function)(QString);
  //pointer_function = &fwbackupsApp::new_log_message
  //log_connect_function(pointer_function);
  
  QStringList headers;
  headers << tr("Name") << tr("Icon");
  TreeModel *setsTreeModel = new TreeModel(headers);
  setsListView->setModel(setsTreeModel);
  this->refreshSets();
}

void fwbackupsApp::cleanup() {
  log_message(LEVEL_INFO, tr("fwbackups administrator closed"));
}

void fwbackupsApp::refreshSets() {
  QAbstractItemModel *model = setsListView->model();
  // Get the root index
  QModelIndex root = setsListView->rootIndex();
  // How many children = rows to remove?
  int nRemoved = 0;
  int nRows = model->rowCount(root);
  while( nRemoved <= nRows ) {
    // Always row=0 because as we remove row=0, index at row=1 becomes row=0
    model->removeRow(0, root);
    nRemoved++;
  }
  // Add the new rows
  QModelIndex index = model->index(0, 0, root);
  QStringList sets = get_all_set_names();
  totalBackupSetsLabel->setText(QString::number( sets.length() ));
  foreach (QString set, sets) {
    if (!model->insertRow(index.row()+1, index.parent())) {
      return;
    }
    // Set name
    QModelIndex child = model->index(index.row()+1, 0, index.parent());
    model->setData(child, QVariant(set), Qt::DisplayRole);
    // Icon resource path
    child = model->index(index.row()+1, 1, index.parent());
    model->setData(child, QVariant(":/program-icons/program-icons/copy.png"), Qt::DecorationRole);
  }
}

/***************** Menu ****************/

// File menu

void fwbackupsApp::on_actionImport_Sets_activated() {
  QStringList filenames = QFileDialog::getOpenFileNames(this,
                                                        tr("Select Sets"),
                                                        QString::null,
                                                        "Set configuration files (*.conf)");
  foreach (QString filename, filenames) {
    qDebug() << filename;
  }

}

void fwbackupsApp::on_actionExport_Sets_activated() {
  exportSetsWindow *ewindow = new exportSetsWindow;
  ewindow->show();
}

void fwbackupsApp::on_actionQuit_activated() {
  qApp->closeAllWindows();
}

// Edit menu

void fwbackupsApp::on_actionPreferences_activated() {
  prefsWindow *pwindow = new prefsWindow;
  pwindow->show();
}

// Help menu

void fwbackupsApp::on_actionAbout_activated() {
  QMessageBox::about(this, tr("About fwbackups"),
                     tr("<b>fwbackups</b> v%1<br />\n"
                     "<span style=\"font-weight: normal;\">"
                     "A feature-rich user backups program<br />\n"
                     "Copyright &copy; 2005 - 2009 Stewart Adam<br /><br />\n"
                     "<i>Visit <a href=\"http://www.fwbackups.com\">www.fwbackups.com</a> "
                     "for more information and product updates.</i></span>").arg(VERSION));
}

void fwbackupsApp::on_actionHelp_activated() {
  QString url = QString("http://downloads.diffingo.com/fwbackups/docs/%1-html").arg(VERSION);
  QDesktopServices::openUrl(url);
}

void fwbackupsApp::on_actionCheck_for_Updates_activated() {
  QString url = QString("http://www.diffingo.com/update.php?product=fwbackups&version=%1").arg(VERSION);
  QDesktopServices::openUrl(url);
}


/***************** Toolbar ****************/

void fwbackupsApp::fwbackupsApp::clear_toolbar_status() {
  actionOverview_2->setChecked(false);
  actionBackup_Sets_2->setChecked(false);
  actionOne_Time_Backup_2->setChecked(false);
  actionRestore_2->setChecked(false);
  actionOperations_2->setChecked(false);
  actionLog_Viewer_2->setChecked(false);
}

void fwbackupsApp::switch_overview() {
  this->clear_toolbar_status();
  mainStackedWidget->setCurrentWidget(overviewPage);
  actionOverview_2->setChecked(true);
}

void fwbackupsApp::switch_backupsets() {
  this->clear_toolbar_status();
  mainStackedWidget->setCurrentWidget(backupSetsPage);
  actionBackup_Sets_2->setChecked(true);
}

void fwbackupsApp::show_one_time_backup() {
  configBackupsDialog *cwindow = new configBackupsDialog(TYPE_ONETIME);
  cwindow->show();
}

void fwbackupsApp::show_restore() {
  restoreDialog *rwindow = new restoreDialog;
  rwindow->setGuidedMode(true);
  rwindow->show();
}

void fwbackupsApp::switch_operations() {
  this->clear_toolbar_status();
  mainStackedWidget->setCurrentWidget(operationsPage);
  actionOperations_2->setChecked(true);
}

void fwbackupsApp::switch_logviewer() {
  this->clear_toolbar_status();
  mainStackedWidget->setCurrentWidget(logViewerPage);
  actionLog_Viewer_2->setChecked(true);
}

/***************** Sets ****************/

void fwbackupsApp::on_newSetButton_clicked() {
  configBackupsDialog *cwindow = new configBackupsDialog(TYPE_SET);
  cwindow->show();
}

void fwbackupsApp::on_editSetButton_clicked() {
  QModelIndex selected = setsListView->selectionModel()->selectedIndexes()[0];
  QString setName = setsListView->model()->data(selected, 0).toString();
  configBackupsDialog *cwindow = new configBackupsDialog(TYPE_SET);
  cwindow->loadConfiguration(setName);
  cwindow->show();
}

void fwbackupsApp::on_deleteSetButton_clicked() {
  QModelIndex selected = setsListView->selectionModel()->selectedIndexes()[0];
  QString setName = setsListView->model()->data(selected, 0).toString();
  QString filename = get_set_configuration_path(setName);
  // FIXME: Check if exists before removing.
  // It will not exist/be removed if the filename has no .conf suffix due to ^^
  QFile set(filename);
  set.remove();
  QString message = tr("Removing set");
  message += " `" + setName + "'";
  log_message(LEVEL_INFO, message);
  this->refreshSets();
}

/***************** Logger ****************/

void fwbackupsApp::on_saveLogButton_clicked() {
  QString filename = QFileDialog::getSaveFileName(this,
                                                  tr("Select Files"),
                                                  QString::null,
                                                  QString::null);
  if (filename.isEmpty()) {
    return;
  }
  QFile destination(filename);
  // FIXME: We should append messages to the log viewer as they are generated, not in bulk at quit time
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
 *************** Export Sets ***************
 *******************************************/

exportSetsWindow::exportSetsWindow(QDialog *parent) {
  setupUi(this); // this sets up GUI
  QListWidgetItem *item;
  foreach ( QString set, get_all_set_names() ) {
    item = new QListWidgetItem(set, exportSetsList);
    item->setFlags( Qt::ItemIsUserCheckable | Qt::ItemIsEnabled );
    item->setCheckState(Qt::Unchecked);
  }
}

void exportSetsWindow::on_cancelButton_clicked() {
  this->reject();
}

void exportSetsWindow::on_exportSetsButton_clicked() {
  QString directory = QFileDialog::getExistingDirectory(this,
                                                        tr("Select a Folder"),
                                                        QString::null,
                                                        QFileDialog::ShowDirsOnly | QFileDialog::DontResolveSymlinks);
  if (directory.isEmpty()) {
    return;
  }
  QAbstractItemModel *model = exportSetsList->model();
  QModelIndex root = exportSetsList->rootIndex();
  int nRows = model->rowCount(root);
  int nProcessed = 0;
  while (nRows > nProcessed) {
    QModelIndex index = model->index(nProcessed, 0, root);
    QString setName = index.data().toString();
    if (exportSetsList->item(nProcessed)->checkState() == Qt::Checked) {
      QString filename = get_set_configuration_path(setName);
      // FIXME: Check if exists before copying.
      // It will not exist/be removed if the filename has no .conf suffix due to ^^
      // FIXME: What happens if we select the Sets directory?
      QFile::copy(filename, join_path(directory, setName+".conf"));
    }
    nProcessed++;
  }
  // finally
  this->accept();
}

/*******************************************
 *************** Preferences ***************
 *******************************************/

prefsWindow::prefsWindow(QDialog *parent) {
  setupUi(this); // this sets up GUI
  QSettings *settings = get_settings();
  
  settings->beginGroup("ConfiguringBackups");
  guidedModeCheck->setChecked(settings->value("GuidedMode", true).toBool());
  warnBeforeReplaceCheck->setChecked(settings->value("WarnBeforeReplacing", true).toBool());
  settings->endGroup();
  
  
# if defined(__APPLE__)
  trayAreaLabel->hide();
  trayIconCheck->hide();
  startMinimizedCheck->hide();
  minimizeTrayCheck->hide();
# endif
  
  settings->beginGroup("TrayArea");
  trayIconCheck->setChecked(settings->value("Show", true).toBool());
  startMinimizedCheck->setChecked(settings->value("StartMinimized", false).toBool());
  minimizeTrayCheck->setChecked(settings->value("MinimizeOnClose", false).toBool());
  settings->endGroup();
  
  settings->beginGroup("Misc");
  popupNotificationsCheck->setChecked(settings->value("ShowPopupNotifications", true).toBool());
  startOnLoginCheck->setChecked(settings->value("StartOnLogin", false).toBool());
  if (settings->value("AlwaysShowDebug", LEVEL_INFO).toInt() == LEVEL_DEBUG) {
    showDebugMessagesCheck->setChecked(true);
  } else {
    showDebugMessagesCheck->setChecked(false);
  }
  
  settings->endGroup();
}

void prefsWindow::on_closeButton_clicked() {
    QSettings *settings = get_settings();
  
  settings->beginGroup("ConfiguringBackups");
  settings->setValue("GuidedMode", guidedModeCheck->isChecked());
  settings->setValue("WarnBeforeReplacing", warnBeforeReplaceCheck->isChecked());
  settings->endGroup();
  
  settings->beginGroup("TrayArea");
  settings->setValue("Show", trayIconCheck->isChecked());
  settings->setValue("StartMinimized", startMinimizedCheck->isChecked());
  settings->setValue("MinimizeOnClose", minimizeTrayCheck->isChecked());
  settings->endGroup();
  
  settings->beginGroup("Misc");
  settings->setValue("ShowPopupNotifications", popupNotificationsCheck->isChecked());
  settings->setValue("StartOnLogin", startOnLoginCheck->isChecked());
  // FIXME: Make this actually set the logging level in the program
  if ( showDebugMessagesCheck->isChecked() ) {
    settings->setValue("AlwaysShowDebug", LEVEL_DEBUG);
  } else {
    settings->setValue("AlwaysShowDebug", LEVEL_INFO);
  }
  settings->endGroup();
  this->accept();
}
