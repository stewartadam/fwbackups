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
#include <qmessagebox.h>
#include <qdesktopservices.h>
#include <qurl.h>

#include "configure_server.h"
#include "manage_account.h"

#include "common.h"
#include "config.h"
#include "logger.h"

#include "server_admin.h"

/*******************************************
 ***************** Server App ****************
 *******************************************/

serverAdminApp::serverAdminApp(QMainWindow *parent) {
  fwLogger *logger = fwLogger::getInstance();
  
  setupUi(this); // this sets up GUI
  this->switch_servers();
  // Action handlers
  connect(qApp, SIGNAL(aboutToQuit()), this, SLOT(cleanup()));
  // This does the QStackedWidget switching (toolbar & View menu)
  connect(actionManage_Servers, SIGNAL(activated()), this, SLOT(switch_servers()));
  connect(actionManage_Servers_2, SIGNAL(activated()), this, SLOT(switch_servers()));
  connect(actionManage_Accounts, SIGNAL(activated()), this, SLOT(switch_accounts()));
  connect(actionManage_Accounts_2, SIGNAL(activated()), this, SLOT(switch_accounts()));
  connect(actionActive_Connections, SIGNAL(activated()), this, SLOT(switch_active_connections()));
  connect(actionActive_Connections_2, SIGNAL(activated()), this, SLOT(switch_active_connections()));
  
  logger->log_message(LEVEL_INFO, tr("fwbackups server administrator started"));
}

void serverAdminApp::cleanup() {
  logger->log_message(LEVEL_INFO, tr("fwbackups server administrator closed"));
}

/***************** Menu ****************/

// File menu

void serverAdminApp::on_actionQuit_activated() {
  qApp->closeAllWindows();
}

// Help menu

void serverAdminApp::on_actionAbout_activated() {
  QMessageBox::about(this, tr("About fwbackups"),
                     tr("<b>fwbackups</b> v%1<br />\n"
                     "<span style=\"font-weight: normal;\">"
                     "A feature-rich user backups program<br />\n"
                     "Copyright &copy; 2005 - 2010 Stewart Adam<br /><br />\n"
                     "<i>Visit <a href=\"http://www.fwbackups.com\">www.fwbackups.com</a> "
                     "for more information and product updates.</i></span>").arg(VERSION));
}

void serverAdminApp::on_actionHelp_activated() {
  QUrl url = QString("http://downloads.diffingo.com/fwbackups/docs/%1-html").arg(VERSION);
  QDesktopServices::openUrl(url);
}

void serverAdminApp::on_actionCheck_for_Updates_activated() {
  QUrl url = QString("http://www.diffingo.com/update.php?product=fwbackups&version=%1").arg(VERSION);
  QDesktopServices::openUrl(url);
}

/***************** Toolbar ****************/

void serverAdminApp::clear_toolbar_status() {
  actionManage_Servers->setChecked(false);
  actionManage_Accounts->setChecked(false);
  actionActive_Connections->setChecked(false);
}

void serverAdminApp::switch_servers() {
  this->clear_toolbar_status();
  mainStackedWidget->setCurrentWidget(serverPage);
  actionManage_Servers->setChecked(true);
}

void serverAdminApp::switch_accounts() {
  this->clear_toolbar_status();
  mainStackedWidget->setCurrentWidget(accountsPage);
  actionManage_Accounts->setChecked(true);
}

void serverAdminApp::switch_active_connections() {
  this->clear_toolbar_status();
  mainStackedWidget->setCurrentWidget(activeConnectionsPage);
  actionActive_Connections->setChecked(true);
}

/***************** Manage Servers ****************/

void serverAdminApp::on_serverNewButton_clicked() {
  configureServerDialog *swindow = new configureServerDialog();
  swindow->exec();
  delete swindow;
}

/***************** Manage Servers ****************/

/*
void configureServerDialog::sign_client(QDir host_dir, QString fq_hostname) {
  QDir client_dir(join_path(ca_dir.absolutePath(), "clients"));
  if (!client_dir.exists()) {
    ca_dir.mkdir("clients");
  }
*/

void serverAdminApp::on_accountAddButton_clicked() {
  QString fq_hostname(accountServerCombo->currentText());
  manageAccountDialog *awindow = new manageAccountDialog(fq_hostname);
  awindow->exec();
  delete awindow;
}


