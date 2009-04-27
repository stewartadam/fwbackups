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
#ifndef CUSTOM_WIDGET_H
#define CUSTOM_WIDGET_H

#include <QtGui>
#include <QDialog>
#include <QTabWidget>

/*************** Tab widget ****************/

class TabNTabBarWidget: public QTabWidget {
  Q_OBJECT

public:
  TabNTabBarWidget(QDialog *parent = 0);
  // and to make tabBar public
  using QTabWidget::tabBar;
};

/*************** Tree widget ****************/

class TreeItem {
public:
  TreeItem(const QVector<QVariant> &data, TreeItem *parent = 0);
  ~TreeItem();
  
  TreeItem *child(int number);
  int childCount() const;
  int columnCount() const;
  QVariant data(int column) const;
  bool insertChildren(int position, int count, int columns);
  bool insertColumns(int position, int columns);
  TreeItem *parent();
  bool removeChildren(int position, int count);
  bool removeColumns(int position, int columns);
  int childNumber() const;
  bool setData(int column, const QVariant &value);

private:
  QList<TreeItem*> childItems;
  QVector<QVariant> itemData;
  TreeItem *parentItem;
};

class TreeItem;
class TreeModel : public QAbstractItemModel {
  Q_OBJECT

public:
  TreeModel(const QStringList &headers, QObject *parent = 0);
  ~TreeModel();

  QVariant data(const QModelIndex &index, int role) const;
  QVariant headerData(int section, Qt::Orientation orientation,
                      int role = Qt::DisplayRole) const;
  QModelIndex index(int row, int column,
                    const QModelIndex &parent = QModelIndex()) const;
  QModelIndex parent(const QModelIndex &index) const;
  int rowCount(const QModelIndex &parent = QModelIndex()) const;
  int columnCount(const QModelIndex &parent = QModelIndex()) const;
  Qt::ItemFlags flags(const QModelIndex &index) const;
  bool setData(const QModelIndex &index, const QVariant &value,
               int role = Qt::DisplayRole);
  bool setHeaderData(int section, Qt::Orientation orientation,
                     const QVariant &value, int role = Qt::DisplayRole);
  bool insertColumns(int position, int columns,
                     const QModelIndex &parent = QModelIndex());
  bool removeColumns(int position, int columns,
                     const QModelIndex &parent = QModelIndex());
  bool insertRows(int position, int rows,
                  const QModelIndex &parent = QModelIndex());
  bool removeRows(int position, int rows,
                  const QModelIndex &parent = QModelIndex());
  void clear();

private:
  TreeItem *getItem(const QModelIndex &index) const;
  TreeItem *rootItem;
};
#endif
