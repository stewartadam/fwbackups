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

#include "custom_widgets.h"

/*
 * This is a subclass of QTabBar that allows us to hide the tab bar if needed
 */
TabNTabBarWidget::TabNTabBarWidget(QDialog *parent) {
  // defined, but empty since we don't really need it.
}

/*
 * This implements our own model for use in our list-based widgets
 */
TreeItem::TreeItem(const QVector<QVariant> &data, TreeItem *parent) {
  parentItem = parent;
  itemData = data;
}

TreeItem::~TreeItem() {
  qDeleteAll(childItems);
}

TreeItem *TreeItem::child(int number) {
  return childItems.value(number);
}
 
int TreeItem::childCount() const {
  return childItems.count();
}

int TreeItem::childNumber() const {
  if (parentItem) {
    return parentItem->childItems.indexOf(const_cast<TreeItem*>(this));
  }

  return 0;
}

int TreeItem::columnCount() const {
  return itemData.count();
}

QVariant TreeItem::data(int column) const {
  return itemData.value(column);
}


bool TreeItem::insertChildren(int position, int count, int columns) {
  if (position < 0 || position > childItems.size()) {
    return false;
  }
  for (int row = 0; row < count; ++row) {
    QVector<QVariant> data(columns);
    TreeItem *item = new TreeItem(data, this);
    childItems.insert(position, item);
  }
  return true;
 }
 
bool TreeItem::insertColumns(int position, int columns) {
  if (position < 0 || position > itemData.size()) {
    return false;
  }

  for (int column = 0; column < columns; ++column) {
    itemData.insert(position, QVariant());
  }

  foreach (TreeItem *child, childItems) {
    child->insertColumns(position, columns);
  }
  return true;
}

TreeItem *TreeItem::parent() {
  return parentItem;
}

bool TreeItem::removeChildren(int position, int count) {
  if (position < 0 || position + count > childItems.size()) {
    return false;
  }

  for (int row = 0; row < count; ++row) {
    delete childItems.takeAt(position);
  }

  return true;
}

bool TreeItem::removeColumns(int position, int columns) {
  if (position < 0 || position + columns > itemData.size()) {
    return false;
  }

  for (int column = 0; column < columns; ++column) {
    itemData.remove(position);
  }

  foreach (TreeItem *child, childItems) {
    child->removeColumns(position, columns);
  }

  return true;
}

bool TreeItem::setData(int column, const QVariant &value) {
    if (column < 0 || column >= itemData.size()) {
        return false;
    }

    itemData[column] = value;
    return true;
}
 
 


TreeModel::TreeModel(const QStringList &headers, QObject *parent)
  : QAbstractItemModel(parent) {
  QVector<QVariant> rootData;
  foreach (QString header, headers)
    rootData << header;
  rootItem = new TreeItem(rootData);
}

TreeModel::~TreeModel() {
  delete rootItem;
}

int TreeModel::columnCount(const QModelIndex &parent) const {
  return rootItem->columnCount();
}

QVariant TreeModel::data(const QModelIndex &index, int role) const {
  if (!index.isValid()) {
    return QVariant();
  }

  if (role == Qt::DisplayRole) {
    TreeItem *item = getItem(index);
    return item->data(index.column());
  } else if (role == Qt::DecorationRole) {
    TreeItem *item = getItem(index);
    return QIcon( item->data(1).toString() );
  } else {
    return QVariant();
  }

  
}

Qt::ItemFlags TreeModel::flags(const QModelIndex &index) const {
  if (!index.isValid()) {
    return 0;
  }

  return Qt::ItemIsEnabled | Qt::ItemIsSelectable;
}

TreeItem *TreeModel::getItem(const QModelIndex &index) const {
  if (index.isValid()) {
    TreeItem *item = static_cast<TreeItem*>(index.internalPointer());
    if (item) return item;
  }
  return rootItem;
}

QVariant TreeModel::headerData(int section, Qt::Orientation orientation,
                                int role) const {
  if (orientation == Qt::Horizontal && role == Qt::DisplayRole) {
    return rootItem->data(section);
  }
  return QVariant();
}

QModelIndex TreeModel::index(int row, int column, const QModelIndex &parent) const {
  if (parent.isValid() && parent.column() != 0) {
    return QModelIndex();
  }

  TreeItem *parentItem = getItem(parent);

  TreeItem *childItem = parentItem->child(row);
  if (childItem) {
    return createIndex(row, column, childItem);
  } else {
    return QModelIndex();
  }
}

bool TreeModel::insertColumns(int position, int columns, const QModelIndex &parent) {
  bool success;

  beginInsertColumns(parent, position, position + columns - 1);
  success = rootItem->insertColumns(position, columns);
  endInsertColumns();

  return success;
}

bool TreeModel::insertRows(int position, int rows, const QModelIndex &parent) {
  TreeItem *parentItem = getItem(parent);
  bool success;
  
  beginInsertRows(parent, position, position + rows - 1);
  success = parentItem->insertChildren(position, rows, rootItem->columnCount());
  endInsertRows();
  
  return success;
}

QModelIndex TreeModel::parent(const QModelIndex &index) const {
  if (!index.isValid()) {
    return QModelIndex();
  }

  TreeItem *childItem = getItem(index);
  TreeItem *parentItem = childItem->parent();

  if (parentItem == rootItem) {
    return QModelIndex();
  }

  return createIndex(parentItem->childNumber(), 0, parentItem);
}

bool TreeModel::removeColumns(int position, int columns, const QModelIndex &parent) {
  bool success;

  beginRemoveColumns(parent, position, position + columns - 1);
  success = rootItem->removeColumns(position, columns);
  endRemoveColumns();

  if (rootItem->columnCount() == 0) {
    removeRows(0, rowCount());
  }

  return success;
}

bool TreeModel::removeRows(int position, int rows, const QModelIndex &parent) {
  TreeItem *parentItem = getItem(parent);
  bool success = true;

  beginRemoveRows(parent, position, position + rows - 1);
  success = parentItem->removeChildren(position, rows);
  endRemoveRows();

  return success;
}

int TreeModel::rowCount(const QModelIndex &parent) const {
  TreeItem *parentItem = getItem(parent);
  
  return parentItem->childCount();
}

bool TreeModel::setData(const QModelIndex &index, const QVariant &value,
                        int role) {
  if (role == Qt::DisplayRole || role == Qt::DecorationRole) {
    TreeItem *item = getItem(index);
    bool result = item->setData(index.column(), value);
    if (result) {
      emit dataChanged(index, index);
    }
    return result;
  } else {
    return false;
  }
}

bool TreeModel::setHeaderData(int section, Qt::Orientation orientation,
                              const QVariant &value, int role) {
  if ( !(role == Qt::DisplayRole || role == Qt::DecorationRole) || orientation != Qt::Horizontal) {
    return false;
  }
  bool result = rootItem->setData(section, value);
  if (result) {
    emit headerDataChanged(orientation, section, section);
  }
  return result;
}

void TreeModel::clear() {
  QVector<QVariant> rootData;
  delete rootItem;
  rootItem = new TreeItem(rootData);
  reset();
}


