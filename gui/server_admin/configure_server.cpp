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
#include <fstream>
#include <iostream>
#include <sys/stat.h>
#include <QDir>

#include "configure_server.h"

#include "config.h"
#include "common.h"
#include "logger.h"

configureServerDialog::configureServerDialog(QDialog *parent) {
  fwLogger *logger = fwLogger::getInstance();
  
  setupUi(this); // this sets up GUI
}

void configureServerDialog::initalize_ca(QDir host_dir, QString target, QString fq_hostname) {
  logger->log_message(LEVEL_INFO, tr("Initializing %1 certificate authority for %2").arg(target, fq_hostname));
  QDir ca_dir(join_path(host_dir.absolutePath(), "ca"));
  QDir root_dir(join_path(ca_dir.absolutePath(), "roots"));
  QDir key_dir(join_path(ca_dir.absolutePath(), "keys"));
  if (!ca_dir.exists()) {
    host_dir.mkdir("ca");
  }
  if (!root_dir.exists()) {
    ca_dir.mkdir("roots");
  }
  if (!key_dir.exists()) {
    ca_dir.mkdir("keys");
  }
  QString csr_file(join_path(key_dir.absolutePath(), QString("%1RootCSR.pem").arg(target)));
  QString private_key_file(join_path(key_dir.absolutePath(), QString("%1RootKey.pem").arg(target)));
  QString ca_file(join_path(root_dir.absolutePath(), QString("%1CA.pem").arg(target)));
  QString serial_file(join_path(root_dir.absolutePath(), QString("%1CA.srl").arg(target)));
  QString openssl_conf_file(join_path(root_dir.absolutePath(), QString("openssl.cnf")));
  std::ofstream openssl_conf;
  std::ofstream serial;
  QString string = QString("# OpenSSL example configuration file.\n\
# This is mostly being used for generation of certificate requests.\n\
# Obtained from: http://www.boxbackup.org/trac/wiki/OpenSSLNotes\n\
RANDFILE               = /dev/arandom\n\
[ req ]\n\
distinguished_name     = req_distinguished_name\n\
prompt                 = no\n\
[ req_distinguished_name ]\n\
# Country Name (2 letter code)\n\
C                      = CA\n\
# State or Province Name (full name)\n\
ST                     = .\n\
# Locality Name (eg, city)\n\
L                      = .\n\
# Organization Name (eg, company)\n\
O                      = .\n\
# Organizational Unit Name (eg, section)\n\
OU                     = .\n\
# Common Name (eg, fully qualified host name)\n\
CN                     = %1\n\
# Administrator's email request\n\
emailAddress           = .\n").arg(fq_hostname);
  const char* buffer(string.toStdString().c_str());
  openssl_conf.open(openssl_conf_file.toStdString().c_str());
  openssl_conf << buffer;
  openssl_conf.close();
  // Generates a private key
  system(QString("openssl genrsa -out '%1' 2048").arg(private_key_file).toStdString().c_str());
  // Generates a root CSR
  system(QString("openssl req -config '%1' -new -key '%2' -sha1 -out '%3'").arg(openssl_conf_file, private_key_file, csr_file).toStdString().c_str());
  // Signs the root CSR to create a root certificate (CA)
  system(QString("openssl x509 -req -in '%1' -sha1 -extensions v3_ca -signkey '%2' -out '%3' -days 10000").arg(csr_file, private_key_file, ca_file).toStdString().c_str());
  // Generates the serial file
  serial.open(serial_file.toStdString().c_str());
  serial << "00\n";
  serial.close();
  // Clean up the openssl.cnf file
  QFile::remove(openssl_conf_file);
}

void configureServerDialog::initialize_server(QDir host_dir, QString fq_hostname, QDir backup_store_location) {
  logger->log_message(LEVEL_INFO, tr("Initializing server for %1").arg(fq_hostname));
  QDir server_config_dir(join_path(host_dir.absolutePath(), "bbstored"));
  QDir server_varrun_dir(join_path(host_dir.absolutePath(), "run"));
  QDir ca_dir(join_path(host_dir.absolutePath(), "ca"));
  QDir root_dir(join_path(ca_dir.absolutePath(), "roots"));
  QDir server_dir(join_path(ca_dir.absolutePath(), "servers"));
  if (!server_dir.exists()) {
    ca_dir.mkdir("servers");
  }
  if (!server_config_dir.exists()) {
    host_dir.mkdir("bbstored");
  }
  if (!server_varrun_dir.exists()) {
    host_dir.mkdir("run");
  }
  QString cert_file(join_path(server_dir.absolutePath(), QString("%1-cert.pem").arg(fq_hostname)));
  QString private_key_file(join_path(server_config_dir.absolutePath(), QString("%1-key.pem").arg(fq_hostname)));
  QString csr_file(join_path(server_dir.absolutePath(), QString("%1-csr.pem").arg(fq_hostname)));
  QString client_root_ca_file(join_path(root_dir.absolutePath(), QString("clientCA.pem")));
  QString server_config_root_ca_file(join_path(server_config_dir.absolutePath(), QString("clientCA.pem")));
  QString openssl_conf_file(join_path(server_config_dir.absolutePath(), QString("openssl.cnf")));
  QString bbstored_conf_file(join_path(server_config_dir.absolutePath(), QString("bbstored.conf")));
  QString account_txt_file(join_path(server_config_dir.absolutePath(), QString("accounts.txt")));
  QString raidfile_conf_file(join_path(server_config_dir.absolutePath(), QString("raidfile.conf")));
  QString pid_file(join_path(server_varrun_dir.absolutePath(), QString("bbstored.pid")));
  std::ofstream openssl_conf;
  std::ofstream bbstored_conf;
  std::ofstream account_txt;
  std::ofstream raidfile_conf;
  
  QString string = QString("# OpenSSL example configuration file.\n\
# This is mostly being used for generation of certificate requests.\n\
# Obtained from: http://www.boxbackup.org/trac/wiki/OpenSSLNotes\n\
RANDFILE               = /dev/arandom\n\
[ req ]\n\
distinguished_name     = req_distinguished_name\n\
prompt                 = no\n\
[ req_distinguished_name ]\n\
# Country Name (2 letter code)\n\
C                      = CA\n\
# State or Province Name (full name)\n\
ST                     = .\n\
# Locality Name (eg, city)\n\
L                      = .\n\
# Organization Name (eg, company)\n\
O                      = .\n\
# Organizational Unit Name (eg, section)\n\
OU                     = .\n\
# Common Name (eg, fully qualified host name)\n\
CN                     = %1\n\
# Administrator's email request\n\
emailAddress           = .\n").arg(fq_hostname);
  const char* buffer(string.toStdString().c_str());
  openssl_conf.open(openssl_conf_file.toStdString().c_str());
  openssl_conf << buffer;
  openssl_conf.close();
  
  // Generates a private key
  system(QString("openssl genrsa -out '%1' 2048").arg(private_key_file).toStdString().c_str());
  // Generates a server CSR
  system(QString("openssl req -config '%1' -new -key '%2' -sha1 -out '%3'").arg(openssl_conf_file, private_key_file, csr_file).toStdString().c_str());
  
  string = QString("RaidFileConf = %1\n\
AccountDatabase = %2\n\
\n\
# Uncomment this line to see exactly what commands are being received from clients.\n\
# ExtendedLogging = yes\n\
\n\
# scan all accounts for files which need deleting every 15 minutes.\n\
TimeBetweenHousekeeping = 900\n\
\n\
Server\n\
{\n\
	PidFile = %3\n\
	User = $username\n\
	ListenAddresses = inet:%4\n\
	CertificateFile = %5\n\
	PrivateKeyFile = %6\n\
	TrustedCAsFile = %7\n\
}\n").arg(raidfile_conf_file, account_txt_file, pid_file, fq_hostname, cert_file, private_key_file, client_root_ca_file);
  buffer = string.toStdString().c_str();
  bbstored_conf.open(bbstored_conf_file.toStdString().c_str());
  bbstored_conf << buffer;
  bbstored_conf.close();
  
  // Create the empty raidfile and account configs
  account_txt.open(account_txt_file.toStdString().c_str());
  account_txt << "\n";
  account_txt.close();
  
  string = QString("disc0\n\
{\n\
	SetNumber = 0\n\
	BlockSize = 2048\n\
	Dir0 = %1\n\
	Dir1 = %1\n\
	Dir2 = %1\n\
}\n").arg(backup_store_location.absolutePath());
  buffer = string.toStdString().c_str();
  raidfile_conf.open(raidfile_conf_file.toStdString().c_str());
  raidfile_conf << buffer;
  raidfile_conf.close();

  QFile::copy(client_root_ca_file, server_config_root_ca_file);
  
  // Clean up the openssl.cnf file
  QFile::remove(openssl_conf_file);
}

// FIXME: Add the CN checks, etc checks used in bbstored-certs
void configureServerDialog::sign_server(QDir host_dir, QString fq_hostname) {
  logger->log_message(LEVEL_INFO, tr("Signing certificate for %1").arg(fq_hostname));
  QDir ca_dir(join_path(host_dir.absolutePath(), "ca"));
  QDir root_dir(join_path(ca_dir.absolutePath(), "roots"));
  QDir key_dir(join_path(ca_dir.absolutePath(), "keys"));
  QDir server_dir(join_path(ca_dir.absolutePath(), "servers"));
  QDir server_config_dir(join_path(host_dir.absolutePath(), "bbstored"));
  QString csr_file(join_path(server_dir.absolutePath(), QString("%1-csr.pem").arg(fq_hostname)));
  QString serial_file(join_path(root_dir.absolutePath(), QString("serverCA.srl")));
  QString cert_file(join_path(server_dir.absolutePath(), QString("%1-cert.pem").arg(fq_hostname)));
  QString server_config_cert_file(join_path(server_config_dir.absolutePath(), QString("%1-cert.pem").arg(fq_hostname)));
  QString server_root_ca_file(join_path(root_dir.absolutePath(), QString("serverCA.pem")));
  QString server_root_key_file(join_path(key_dir.absolutePath(), QString("serverRootKey.pem")));
  system(QString("openssl x509 -req -in '%1' -sha1 -extensions usr_crt -CA '%2' -CAkey '%3' -CAserial '%4' -out '%5' -days 5000").arg(csr_file, server_root_ca_file, server_root_key_file, serial_file, cert_file).toStdString().c_str());
  // Clean up the CSR file
  QFile::remove(csr_file);
}

/*
void configureServerDialog::sign_client(QDir host_dir, QString fq_hostname) {
  QDir client_dir(join_path(ca_dir.absolutePath(), "clients"));
  if (!client_dir.exists()) {
    ca_dir.mkdir("clients");
  }
*/

void configureServerDialog::on_okButton_clicked() {
  QString fq_hostname(hostnameLineEdit->text());
  QDir config_dir(get_configuration_directory());
  QDir backup_store_location(storeLineEdit->text());
  QDir host_dir(join_path(config_dir.absolutePath(), fq_hostname));
  if (!host_dir.exists()) {
    config_dir.mkdir(fq_hostname);
  }
  this->initalize_ca(host_dir, "client", fq_hostname);
  this->initalize_ca(host_dir, "server", fq_hostname);
  this->initialize_server(host_dir, fq_hostname, backup_store_location);
  this->sign_server(host_dir, fq_hostname);
  this->accept();
}

void configureServerDialog::on_cancelButton_clicked() {
  this->reject();
}
