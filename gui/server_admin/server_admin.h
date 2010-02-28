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
#ifndef SERVER_ADMIN_H
#define SERVER_ADMIN_H

#include "logger.h"

#include "ui_server_admin.h"

class serverAdminApp: public QMainWindow, private Ui::mainWindow
{
  Q_OBJECT
    
public:
  serverAdminApp(QMainWindow *parent = 0);
  void clear_toolbar_status();

public slots:
  void cleanup();
  // Menu
  //   |-- File
  void on_actionQuit_activated();
  //   |-- Help
  void on_actionAbout_activated();
  void on_actionHelp_activated();
  void on_actionCheck_for_Updates_activated();
  // Toolbar
  void switch_servers();
  void switch_accounts();
  void switch_active_connections();
  // Manage Servers
  void on_serverNewButton_clicked();
  // Manage Accounts
  void on_accountAddButton_clicked();
private:
  fwLogger *logger;
};

#endif
