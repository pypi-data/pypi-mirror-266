#!/usr/bin/env python

# MIT License

# Copyright (c) 2021-2022 Rafael Arvelo

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#
# This file provides utility functions and classes for the DataViewer Application
#

import os
import sys
import numpy
import pandas
import typing
import logging

# Update PYTHONPATH
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui", "images"))

from   PyQt5.QtWidgets      import QApplication, QHeaderView, QLineEdit, QTableWidget, QWidget, QAbstractItemView, QComboBox, QCheckBox,\
                                   QDialog, QStyledItemDelegate, QStyleOptionViewItem, QTableWidgetItem, QCompleter, QFileSystemModel
from   PyQt5.QtCore         import Qt, QObject, QAbstractItemModel, QModelIndex, QFileInfo, pyqtSignal, pyqtSlot
from   PyQt5.QtGui          import QColor, QShowEvent, QStandardItem, QStandardItemModel

from   ui.ui_progresswidget import Ui_ProgressWidget
from   ui.ui_tableeditor    import Ui_TableEditor
from   dataframemodel       import PlotInfoListModel, DataFrameModel, DataFrameFactory, ColorRule, ColorRulesModel, DataFrameParser, PlotInfo
from   customchartdialog    import CustomChartDialog

# Global Logging Handler
class QLogger(QObject, logging.Handler):
    message          = pyqtSignal(int, str)
    formattedMessage = pyqtSignal(int, str)
    def __init__(self, level : int = logging.INFO, parent : QObject = None):
        QObject.__init__(self, parent=parent)
        logging.Handler.__init__(self, level)
    
    def emit(self, record : logging.LogRecord) -> None:
        msg = self.format(record)
        self.message.emit(record.levelno, record.message)
        self.formattedMessage.emit(record.levelno, msg)

# Custom File System Model implementation
class FileSystemModel(QFileSystemModel):
    FILE_SIZE_UNITS      = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    FILE_SIZE_MULTIPLIER = 1024

    def fileSizeStr(self, size : int):
        fileSize  = size
        sizeUnits = 0
        for i in range(len(self.FILE_SIZE_UNITS)): 
            if fileSize >= self.FILE_SIZE_MULTIPLIER:
                fileSize   = fileSize / self.FILE_SIZE_MULTIPLIER
                sizeUnits += 1
            else:
                break
        
        if sizeUnits <= 0:
            sizeStr = str(int(fileSize))
        else:
            sizeStr = "%6.2f" % float(fileSize)
        
        return f"{sizeStr} {self.FILE_SIZE_UNITS[sizeUnits]}" if sizeUnits < len(self.FILE_SIZE_UNITS) else str(size)

    def fileToolTip(self, info : QFileInfo) -> str:
        if isinstance(info, QFileInfo) and info.exists():
            if info.isDir():
                return info.absoluteFilePath()
            else:
                return f"{info.absoluteFilePath()} ({self.fileSizeStr(info.size())})"
        return ""

    def data(self, index : QModelIndex, role: int = ...) -> typing.Any:
        if index.isValid() and role == Qt.ToolTipRole: 
            return self.fileToolTip(self.fileInfo(index))

        return super().data(index, role=role)

# Widget to encapsulate a label, QProgressBar, and cancel button
class ProgressWidget(QWidget):
    cancelled = pyqtSignal()
    def __init__(self, parent : QWidget = None):
        super().__init__(parent=parent)
        self.ui : Ui_ProgressWidget = Ui_ProgressWidget()
        self.ui.setupUi(self)
        self.ui.cancelButton.clicked.connect(self.cancelled)

    @pyqtSlot(int)
    def startProgress(self, steps : int):
        self.ui.progressBar.reset()
        self.ui.progressBar.setMaximum(steps)
        self.show()

    @pyqtSlot(str)
    def updateProgressMsg(self, message : str):
        self.ui.label.setText(message)

    @pyqtSlot(int, int)
    def updateProgress(self, step : int, maximum : int):
        self.ui.progressBar.setValue(step)
        if maximum != self.ui.progressBar.maximum():
            self.ui.progressBar.setMaximum(maximum)

    @pyqtSlot()
    def finishProgress(self):
        self.ui.label.clear()
        self.ui.progressBar.setValue(self.ui.progressBar.maximum())
        self.hide()
    

# Widget to encapsulate a QTableWidget for editing a data structure
class TableEditor(QDialog):
    def __init__(self, header : typing.List[str], parent : QWidget = None):
        super().__init__(parent=parent)
        self.colHeaderLabels : typing.List[str] = header
        self.ui              : Ui_TableEditor   = Ui_TableEditor()
        self.ui.setupUi(self)
        self.ui.tableWidget.setHorizontalHeaderLabels(self.colHeaderLabels)
        self.ui.tableWidget.setColumnCount(len(self.colHeaderLabels))
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.ui.tableWidget.horizontalHeader().setSelectionMode(QAbstractItemView.NoSelection)
        self.ui.tableWidget.verticalHeader().setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.ui.tableWidget.verticalHeader().setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget.selectionModel().selectionChanged.connect(self.onSelectionChanged)
        self.ui.addButton.clicked.connect(self.addRow)
        self.ui.removeButton.clicked.connect(self.removeRows)
        self.ui.copyButton.clicked.connect(self.copyRows)
        self.ui.clearButton.clicked.connect(self.clear)
        self.ui.defaultsButton.clicked.connect(self.resetToDefaults)
        self.ui.defaultsButton.hide()
        self.updateTable()
    
    # Copy the contents of the data structure being edited into this table
    def updateTable(self) -> None:
        pass # Intended to be implemented in subclasses
    
    # Copy the contents of this table into the data structure being edited 
    def updateData(self) -> None:
        pass # Intended to be implemented in subclasses

    # Reset the contents of the table to the defaults
    def resetToDefaults(self) -> None:
        pass # Intended to be implemented in subclasses

    def showEvent(self, e : QShowEvent) -> None:
        result = super().showEvent(e)
        self.ui.tableWidget.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(self.ui.tableWidget.horizontalHeader().count()-1, QHeaderView.Stretch)
        return result

    @pyqtSlot()
    def accept(self) -> None:
        self.updateData()
        return super().accept()

    @pyqtSlot()
    def onSelectionChanged(self) -> None:
        selection     = self.ui.tableWidget.selectionModel().selectedRows()
        any_selection = len(selection) > 0
        self.ui.removeButton.setEnabled(any_selection)
        self.ui.copyButton.setEnabled(any_selection)
    
    def getAllItems(self) -> typing.List[typing.List[QTableWidgetItem]]:
        items = []
        for row in range(self.ui.tableWidget.rowCount()):
            items.append([self.ui.tableWidget.item(row, col) for col in range(self.ui.tableWidget.columnCount())])
        return items

    def getSelectedItems(self) -> typing.Tuple[typing.List[typing.List[QTableWidgetItem]], int]:
        selection     = self.ui.tableWidget.selectionModel().selectedRows()
        row           = selection[-1].row() if len(selection) > 0 else self.ui.tableWidget.rowCount()
        selectedItems = []
        for sel in selection:
            selectedItems.append([self.ui.tableWidget.item(sel.row(), col) for col in range(self.ui.tableWidget.columnCount())])
        return selectedItems, row

    # Convenience function to add a row of items to a QTableWidget
    @staticmethod
    def addRowToTable(tableWidget : QTableWidget, row : int = None, items : typing.List[QTableWidgetItem] = None) -> int:
        # Insert row after current selection (if applicable)
        if not(isinstance(row, int)) or row < 0 or row > tableWidget.rowCount():
            selection = tableWidget.selectionModel().selectedRows()
            row       = selection[-1].row() if len(selection) > 0 else tableWidget.rowCount()
        
        # Create a new (empty) row
        tableWidget.insertRow(row)

        # Add the given items (if provided)
        if isinstance(items, list) and len(items) == tableWidget.columnCount():
            for i in range(len(items)):
                tableWidget.setItem(row, i, items[i])
        return row

    @pyqtSlot()
    def addRow(self, row : int = None, items : typing.List[QTableWidgetItem] = None) -> int:
        self.addRowToTable(self.ui.tableWidget, row, items)

    @pyqtSlot()
    def copyRows(self) -> None:
        selectedItems, row = self.getSelectedItems()
        if row < self.ui.tableWidget.rowCount():
            row += 1
        for itemList in selectedItems:
            self.ui.tableWidget.insertRow(row)
            for col in range(len(itemList)):
                item = itemList[col]
                if isinstance(item, QTableWidgetItem):
                    self.ui.tableWidget.setItem(row, col, item.clone())
            row += 1

    @pyqtSlot()
    def removeRows(self, row : int = None, count : int = 0) -> None:
        if not(isinstance(row, int)) or row < 0 or row >= self.ui.tableWidget.rowCount():
            selection = self.ui.tableWidget.selectionModel().selectedRows()
            row       = selection[0].row() if len(selection) > 0 else -1
            count     = len(selection)
        if isinstance(row  , int) and row   > -1 and row   <  self.ui.tableWidget.rowCount() and \
           isinstance(count, int) and count >  0 and count <= self.ui.tableWidget.rowCount():
            self.ui.tableWidget.model().removeRows(row, count)

    @pyqtSlot()
    def clear(self) -> None:
        self.ui.tableWidget.clear()
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.setColumnCount(len(self.colHeaderLabels))
        self.ui.tableWidget.setHorizontalHeaderLabels(self.colHeaderLabels)
  
# Item Editor Delegates
class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, items : typing.Iterable[str], parent : QObject = None) -> None:
        super().__init__(parent=parent)
        self.items = items
    
    def createEditor(self, parent: QWidget, option : QStyleOptionViewItem, index : QModelIndex) -> QWidget:
        comboBox = QComboBox(parent)
        comboBox.addItems(self.items)
        return comboBox
    
    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex) -> None:
        if isinstance(editor, QComboBox) and index.isValid():
          model.setData(index, editor.currentText(), Qt.EditRole)
      
    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        if index.isValid():
            value = index.data(Qt.EditRole)
            if isinstance(editor, QComboBox) and isinstance(value, str):
                comboIndex = editor.findText(value)
                if comboIndex > -1:
                  editor.setCurrentIndex(comboIndex)

# A QSyledItemDelegate to encapsulate a QCheckbox
class CheckBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent : QObject = None) -> None:
        super().__init__(parent=parent)
    
    def createEditor(self, parent: QWidget, option : QStyleOptionViewItem, index : QModelIndex) -> QWidget:
        checkBox = QCheckBox(parent)
        return checkBox
    
    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex) -> None:
        if isinstance(editor, QCheckBox) and index.isValid():
          model.setData(index, editor.isChecked(), Qt.EditRole)
      
    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        if index.isValid():
            value = index.data(Qt.EditRole)
            if isinstance(editor, QCheckBox) and isinstance(value, bool):
                editor.setChecked(value)

# A QSyledItemDelegate to encapsulate a QLineEdit with a QCompleter
class LineEditDelegate(QStyledItemDelegate):
    def __init__(self, completer : typing.Union[typing.List[str], QCompleter], parent : QObject = None) -> None:
        super().__init__(parent=parent)
        self.completer = completer
    
    def createEditor(self, parent: QWidget, option : QStyleOptionViewItem, index : QModelIndex) -> QWidget:
        lineEdit = QLineEdit(parent)
        if isinstance(self.completer, QCompleter):
            completer = self.completer
        else:
            completer = QCompleter(self.completer, lineEdit)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        lineEdit.setCompleter(completer)

        return lineEdit
    
    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex) -> None:
        if isinstance(editor, QLineEdit) and index.isValid():
          model.setData(index, editor.text(), Qt.EditRole)
      
    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        if index.isValid():
            value = index.data(Qt.EditRole)
            if isinstance(editor, QLineEdit) and isinstance(value, str):
                editor.setText(value)

# A QSyledItemDelegate to encapsulate a QComboBox with all of the built-in Qt Colors
class ColorEditorDelegate(ComboBoxDelegate):
    def __init__(self, parent: QObject = None) -> None:
        super().__init__(items=QColor.colorNames(), parent=parent)
    
    def createEditor(self, parent: QWidget, option : QStyleOptionViewItem, index : QModelIndex) -> QWidget:
        comboBox = QComboBox(parent)
        for i in range(len(self.items)):
            color = QColor(self.items[i])
            if color.isValid():
                comboBox.addItem(self.items[i])
                comboBox.setItemData(i, color, Qt.DecorationRole)
        return comboBox
  
    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex) -> None:
        if isinstance(editor, QComboBox) and index.isValid():
            name  = editor.itemData(editor.currentIndex(), Qt.DisplayRole)
            color = editor.itemData(editor.currentIndex(), Qt.DecorationRole)
            model.setData(index, name, Qt.EditRole)
            model.setData(index, color, Qt.DecorationRole)
      
    def setEditorData(self, editor : QWidget, index: QModelIndex) -> None:
        if index.isValid():
            value = index.data(Qt.EditRole)
            color = QColor(value)
            if isinstance(editor, QComboBox) and isinstance(value, int):
                for i in range(editor.count()):
                    itemData = editor.itemData(Qt.UserRole)
                    if itemData == value or itemData == color.name():
                        editor.setCurrentIndex(i)
                        break

# Combined Item Delegate for the Color Rule Editor Widget
class ColorRuleEditorDelegate(QStyledItemDelegate):
    def __init__(self, model : DataFrameModel, parent : QObject = None) -> None:
        super().__init__(parent=parent)
        self.model          = model
        self.columnDelegate = ComboBoxDelegate(self.model.df.columns, self)
        self.colorDelegate  = ColorEditorDelegate(self)
    
    def createEditor(self, parent : QWidget, option : QStyleOptionViewItem, index : QModelIndex) -> QWidget:
        if index.column() == ColorRulesModel.COLUMN_NAME_COLUMN:
            return self.columnDelegate.createEditor(parent, option, index)
        elif index.column() == ColorRulesModel.COLOR_COLUMN:
            return self.colorDelegate.createEditor(parent, option, index)
        else:
            return super().createEditor(parent, option, index)
    
    def setModelData(self, editor : QWidget, model: QAbstractItemModel, index : QModelIndex) -> None:
        if index.column() == ColorRulesModel.COLUMN_NAME_COLUMN:
            return self.columnDelegate.setModelData(editor, model, index)
        elif index.column() == ColorRulesModel.COLOR_COLUMN:
            return self.colorDelegate.setModelData(editor, model, index)
        else:
            return super().setModelData(editor, model, index)
      
    def setEditorData(self, editor : QWidget, index: QModelIndex) -> None:
        if index.column() == ColorRulesModel.COLUMN_NAME_COLUMN:
            return self.columnDelegate.setEditorData(editor, index)
        elif index.column() == ColorRulesModel.COLOR_COLUMN:
            return self.colorDelegate.setEditorData(editor, index)
        else:
            return super().setEditorData(editor, index)

# Combined Item Delegate for the DataFrameParserEditor Widget
class DataFrameParserEditorDelegate(QStyledItemDelegate):
    NAME_COLUMN           = 0
    PATTERN_COLUMN        = 1
    READ_FUNC_COLUMN      = 2
    WRITE_FUNC_COLUMN     = 3
    READ_ITERABLE_COLUMN  = 4
    WRITE_ITERABLE_COLUMN = 5
    SUFFIX_COLUMN         = 6
    DEFAULT_COLUMN        = 7
    READ_KWARGS_COLUMN    = 8
    WRITE_KWARGS_COLUMN   = 9
    COLUMN_COUNT          = 10
    def __init__(self, parent : QObject = None) -> None:
        super().__init__(parent=parent)
        # Intentionally creating separate factory to use the default parsers for completions
        self.factory           = DataFrameFactory(self)
        self.logger            = logging.getLogger(__name__)
        parsers                = self.factory.parsers.values()
        read_functions         = []
        write_functions        = []
        for parser in parsers:
            parserFields = parser.toDict()
            if 'read_func' in parserFields.keys():
                read_functions.append(parserFields['read_func'])
            if 'write_func' in parserFields.keys():
                write_functions.append(parserFields['write_func'])

        self.readFuncDelegate  = LineEditDelegate(read_functions, self)
        self.writeFuncDelegate = LineEditDelegate(write_functions, self)
        self.checkBoxDelegate  = CheckBoxDelegate(self)
    
    def createEditor(self, parent : QWidget, option : QStyleOptionViewItem, index : QModelIndex) -> QWidget:
        if index.column() == self.READ_FUNC_COLUMN:
            return self.readFuncDelegate.createEditor(parent, option, index)
        elif index.column() == self.WRITE_FUNC_COLUMN:
            return self.writeFuncDelegate.createEditor(parent, option, index)
        elif index.column() in [self.READ_ITERABLE_COLUMN, self.WRITE_ITERABLE_COLUMN, self.DEFAULT_COLUMN]:
            return self.checkBoxDelegate.createEditor(parent, option, index)
        else:
            return super().createEditor(parent, option, index)
    
    def setModelData(self, editor : QWidget, model: QAbstractItemModel, index : QModelIndex) -> None:
        if index.column() == self.READ_FUNC_COLUMN:
            return self.readFuncDelegate.setModelData(editor, model, index)
        elif index.column() == self.WRITE_FUNC_COLUMN:
            return self.writeFuncDelegate.setModelData(editor, model, index)
        elif index.column() in [self.READ_ITERABLE_COLUMN, self.WRITE_ITERABLE_COLUMN, self.DEFAULT_COLUMN]:
            result = self.checkBoxDelegate.setModelData(editor, model, index)

            # Only allow 1 parser to be the default at once
            if index.column() == self.DEFAULT_COLUMN and index.data(Qt.EditRole):
                for row in range(model.rowCount()):
                    if row != index.row():
                        model.setData(model.index(row, self.DEFAULT_COLUMN), False, Qt.EditRole)

            return result
        else:
            return super().setModelData(editor, model, index)
      
    def setEditorData(self, editor : QWidget, index: QModelIndex) -> None:
        if index.column() == self.READ_FUNC_COLUMN:
            return self.readFuncDelegate.setEditorData(editor, index)
        elif index.column() == self.WRITE_FUNC_COLUMN:
            return self.writeFuncDelegate.setEditorData(editor, index)
        elif index.column() in [self.READ_ITERABLE_COLUMN, self.WRITE_ITERABLE_COLUMN, self.DEFAULT_COLUMN]:
            return self.checkBoxDelegate.setEditorData(editor, index)
        else:
            return super().setEditorData(editor, index)

# Widget for updating the list of queries inside a TableViewer
class QueryListEditor(TableEditor):
    HEADER_LABELS     = ['Query Text']
    QUERY_TEXT_COLUMN = 0
    def __init__(self, 
                 model     : QStandardItemModel, 
                 completer : QCompleter,
                 parent    : QWidget = None):
        self.model            = model
        super().__init__(header=self.HEADER_LABELS, parent=parent)
        self.lineEditDelegate = LineEditDelegate(completer, self)
        self.ui.tableWidget.setItemDelegate(self.lineEditDelegate)
        self.setWindowTitle(f'Query Editor')
        self.resize(700, 500)

    # Update the internal Table Widget from the model's queries
    def updateTable(self):
        self.clear()
        for row in range(self.model.rowCount()):
            table_items = []
            for col in range(len(self.HEADER_LABELS)):
                item = self.model.item(row, col)
                if isinstance(item, QStandardItem):
                    table_item = QTableWidgetItem(item.data(Qt.DisplayRole))
                    table_item.setFlags(item.flags())
                    table_item.setCheckState(item.checkState())
                    table_items.append(table_item)
            self.addRow(items=table_items)
    
    # Update the model's queries from the internal Table Widget
    def updateData(self):
        self.model.clear()
        self.model.setRowCount(0)
        self.model.setColumnCount(len(self.HEADER_LABELS))
        items = self.getAllItems()
        for itemList in items:
            if len(itemList) == len(self.HEADER_LABELS):
                if isinstance(itemList[self.QUERY_TEXT_COLUMN], QTableWidgetItem):
                    enabled    = itemList[self.QUERY_TEXT_COLUMN].data(Qt.CheckStateRole) 
                    query_text = itemList[self.QUERY_TEXT_COLUMN].data(Qt.DisplayRole) 
                    item       = QStandardItem(query_text)
                    item.setFlags(Qt.ItemIsUserCheckable | item.flags())
                    item.setCheckState(Qt.Checked if enabled else Qt.Unchecked)
                    self.model.appendRow(item)

# Widget for updating the color rules of a DataFrameModel
class ColorRuleEditor(TableEditor):
    def __init__(self, model : DataFrameModel, parent: QWidget = None):
        self.df_model = model
        super().__init__(header=ColorRulesModel.HEADER_LABELS, parent=parent)

        self.colorRuleEditorDelegate = ColorRuleEditorDelegate(model)
        self.ui.tableWidget.setItemDelegate(self.colorRuleEditorDelegate)
        self.setWindowTitle(f'Color Rule Editor: {model.filename}')
        self.resize(700, 500)
    
    # Update the internal Table Widget from the model's ColorRulesModel
    def updateTable(self):
        self.clear()
        for i in range(self.df_model.color_rules_model.rowCount()):
            items = []
            for j in range(self.df_model.color_rules_model.columnCount()):
                index = self.df_model.color_rules_model.index(i, j)
                if index.isValid():
                    item = QTableWidgetItem(index.data(Qt.DisplayRole))
                    for role in self.df_model.color_rules_model.validRoles():
                        item.setData(role, index.data(role))
                    items.append(item)
            self.addRow(items=items)
    
    # Update the model's ColorRulesModel from the internal Table Widget
    def updateData(self):
        self.df_model.clearColorRules()
        items = self.getAllItems()
        for itemList in items:
            if len(itemList) == len(self.colHeaderLabels) and all([isinstance(i, QTableWidgetItem) for i in itemList]):
                enabled   = itemList[ColorRulesModel.COLUMN_NAME_COLUMN].data(Qt.CheckStateRole) 
                column    = itemList[ColorRulesModel.COLUMN_NAME_COLUMN].data(Qt.DisplayRole) 
                condition = itemList[ColorRulesModel.CONDITION_COLUMN].data(Qt.DisplayRole) 
                color     = itemList[ColorRulesModel.COLOR_COLUMN].data(Qt.DisplayRole) 
                rule      = ColorRule(condition=condition, color=QColor(color), enabled=enabled)
                self.df_model.addColorRule(column, rule)

# Widget for updating the list of queries inside a TableViewer
class SavedPlotsEditor(TableEditor):
    HEADER_LABELS     = ['Saved Plots']
    def __init__(self, 
                 saved_plots_model : PlotInfoListModel, 
                 column_model      : QStandardItemModel, 
                 parent            : QWidget = None):
        self.saved_plots_model = saved_plots_model
        self.column_model      = column_model
        super().__init__(header=self.HEADER_LABELS, parent=parent)
        self.setWindowTitle(f'Saved Plots Editor')
        self.resize(700, 500)
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableWidget.itemActivated.connect(self.onItemActivated)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    # Update the internal Table Widget from the saved plots model
    def updateTable(self):
        self.clear()
        for i in range(self.saved_plots_model.rowCount()):
            table_items = []
            for j in range(self.saved_plots_model.columnCount()):
                index = self.saved_plots_model.index(i, j)
                table_item = QTableWidgetItem(index.data(Qt.DisplayRole))
                table_item.setData(Qt.UserRole, index.data(Qt.UserRole))
                table_item.setData(Qt.ToolTipRole, index.data(Qt.ToolTipRole))
                table_items.append(table_item)
            self.addRow(items=table_items)
    
    # Update the saved plots model from the internal Table Widget
    def updateData(self):
        self.saved_plots_model.clear()
        items = self.getAllItems()
        for itemList in items:
            if len(itemList) == len(self.HEADER_LABELS):
                info = itemList[0].data(Qt.UserRole)
                if isinstance(info, PlotInfo) and not info in self.saved_plots_model:
                    self.saved_plots_model.append(info)
    
    @pyqtSlot(QTableWidgetItem)
    def onItemActivated(self, item : QTableWidgetItem):
        if isinstance(item, QTableWidgetItem):
            info = item.data(Qt.UserRole)
            if isinstance(info, PlotInfo):
                chart_dialog = CustomChartDialog(self.column_model, info.x, info.y, info.options)
                ans = chart_dialog.exec()
                if ans == QDialog.Accepted:
                    new_info = PlotInfo(chart_dialog.x, chart_dialog.y, **chart_dialog.options)
                    item.setData(Qt.UserRole, new_info)
                    item.setData(Qt.DisplayRole, new_info.name())
                    item.setData(Qt.ToolTipRole, new_info.name())
            else:
                logging.getLogger(__name__).error(f"Invalid Plot Info: {info}")

# Widget for updating the parsers inside the DataFrameFactory
class DataFrameParserEditor(TableEditor):
    HEADER_LABELS = ['Name',
                     'Pattern',
                     'Read Function',
                     'Write Function',
                     'Iterable (Read)',
                     'Iterable (Write)',
                     'Suffix',
                     'Default',
                     'Keyword Arguments (Read)',
                     'Keyword Arguments (Write)']
    def __init__(self, parent: QWidget = None):
        self.factory              = DataFrameFactory.getInstance()
        self.logger               = logging.getLogger(__name__)
        self.parserEditorDelegate = DataFrameParserEditorDelegate()
        super().__init__(header=DataFrameParserEditor.HEADER_LABELS, parent=parent)

        self.parserEditorDelegate.setParent(self)
        self.ui.tableWidget.setItemDelegate(self.parserEditorDelegate)
        self.ui.defaultsButton.show()
        self.setWindowTitle(f'DataFrame Parser Editor')
    
    @pyqtSlot()
    def addRow(self, row : int = None, items : typing.List[QTableWidgetItem] = None) -> int:
        row                    = super().addRow(row, items)
        pattern_tooltip        = 'Regular expression of filenames to match'
        read_tooltip           = 'Name of function to read an input file into a pandas DataFrame'
        write_tooltip          = 'Name of function to write a pandas DataFrame to a file'
        iterable_tooltip       = 'Flag to indicate if the read function supports reading files in chunks'
        write_iterable_tooltip = 'Flag to indicate if the read function supports reading files in chunks'
        suffix_tooltip         = 'Suffix to append when exporting models to files'
        default_tooltip        = 'Flag to use this parser if no other matching parsers are found'
        read_kwargs_tooltip    = 'Keyword arguments to pass to the read function'
        write_kwargs_tooltip   = 'Keyword arguments to pass to the write function'
        if isinstance(row, int) and row < self.ui.tableWidget.rowCount():
            model = self.ui.tableWidget.model()
            model.setData(model.index(row, DataFrameParserEditorDelegate.PATTERN_COLUMN)       , pattern_tooltip       , Qt.ToolTipRole)
            model.setData(model.index(row, DataFrameParserEditorDelegate.READ_FUNC_COLUMN)     , read_tooltip          , Qt.ToolTipRole)
            model.setData(model.index(row, DataFrameParserEditorDelegate.WRITE_FUNC_COLUMN)    , write_tooltip         , Qt.ToolTipRole)
            model.setData(model.index(row, DataFrameParserEditorDelegate.READ_ITERABLE_COLUMN) , iterable_tooltip      , Qt.ToolTipRole)
            model.setData(model.index(row, DataFrameParserEditorDelegate.WRITE_ITERABLE_COLUMN), write_iterable_tooltip, Qt.ToolTipRole)
            model.setData(model.index(row, DataFrameParserEditorDelegate.SUFFIX_COLUMN)        , suffix_tooltip        , Qt.ToolTipRole)
            model.setData(model.index(row, DataFrameParserEditorDelegate.DEFAULT_COLUMN)       , default_tooltip       , Qt.ToolTipRole)
            model.setData(model.index(row, DataFrameParserEditorDelegate.READ_KWARGS_COLUMN)   , read_kwargs_tooltip   , Qt.ToolTipRole)
            model.setData(model.index(row, DataFrameParserEditorDelegate.WRITE_KWARGS_COLUMN)  , write_kwargs_tooltip  , Qt.ToolTipRole)
        return row

    def updateTable(self):
        self.clear()
        TWI = QTableWidgetItem
        for p in self.factory.parsers.values():
            d       = p.toDict()
            default = bool(p == self.factory.default_parser)
            try:
                items = [TWI(d['name']),
                         TWI(d['pattern']),
                         TWI(d['read_func']),
                         TWI(d['write_func']),
                         TWI(str(d['iterable'])),
                         TWI(str(d['write_iterable'])),
                         TWI(str(d['suffix'])),
                         TWI(str(default)),
                         TWI(str(d['kwargs'])),
                         TWI(str(d['write_kwargs']))]
                items[DataFrameParserEditorDelegate.NAME_COLUMN].setData(Qt.EditRole, d['name'])
                items[DataFrameParserEditorDelegate.PATTERN_COLUMN].setData(Qt.EditRole, d['pattern'])
                items[DataFrameParserEditorDelegate.READ_FUNC_COLUMN].setData(Qt.EditRole, d['read_func'])
                items[DataFrameParserEditorDelegate.WRITE_FUNC_COLUMN].setData(Qt.EditRole, d['write_func'])
                items[DataFrameParserEditorDelegate.READ_ITERABLE_COLUMN].setData(Qt.EditRole, d['iterable'])
                items[DataFrameParserEditorDelegate.WRITE_ITERABLE_COLUMN].setData(Qt.EditRole, d['write_iterable'])
                items[DataFrameParserEditorDelegate.SUFFIX_COLUMN].setData(Qt.EditRole, d['suffix'])
                items[DataFrameParserEditorDelegate.DEFAULT_COLUMN].setData(Qt.EditRole, default)
                items[DataFrameParserEditorDelegate.READ_KWARGS_COLUMN].setData(Qt.EditRole, str(d['kwargs']))
                items[DataFrameParserEditorDelegate.WRITE_KWARGS_COLUMN].setData(Qt.EditRole, str(d['write_kwargs']))
                self.addRow(row=self.ui.tableWidget.rowCount(), items=items)
            except:
                self.logger.error(f'Unable to add row from parser: {d}')
        self.ui.tableWidget.setHorizontalHeaderLabels(self.HEADER_LABELS)
    
    def updateData(self):
        self.factory.parsers.clear()
        items = self.getAllItems()
        for itemList in items:
            if len(itemList) == DataFrameParserEditorDelegate.COLUMN_COUNT and all([isinstance(i, QTableWidgetItem) for i in itemList]):
                d : typing.Dict[str, typing.Any] = {}
                d['name']           = itemList[DataFrameParserEditorDelegate.NAME_COLUMN].data(Qt.DisplayRole)
                d['pattern']        = itemList[DataFrameParserEditorDelegate.PATTERN_COLUMN].data(Qt.DisplayRole)
                d['read_func']      = itemList[DataFrameParserEditorDelegate.READ_FUNC_COLUMN].data(Qt.DisplayRole)
                d['write_func']     = itemList[DataFrameParserEditorDelegate.WRITE_FUNC_COLUMN].data(Qt.DisplayRole)
                d['iterable']       = itemList[DataFrameParserEditorDelegate.READ_ITERABLE_COLUMN].data(Qt.EditRole)
                d['write_iterable'] = itemList[DataFrameParserEditorDelegate.WRITE_ITERABLE_COLUMN].data(Qt.EditRole)
                d['suffix']         = itemList[DataFrameParserEditorDelegate.SUFFIX_COLUMN].data(Qt.EditRole)
                d['kwargs']         = itemList[DataFrameParserEditorDelegate.READ_KWARGS_COLUMN].data(Qt.DisplayRole)
                d['write_kwargs']   = itemList[DataFrameParserEditorDelegate.WRITE_KWARGS_COLUMN].data(Qt.DisplayRole)
                default             = itemList[DataFrameParserEditorDelegate.DEFAULT_COLUMN].data(Qt.EditRole)
                if isinstance(default, str):
                    default = bool(default.lower() == 'true')

                parser = DataFrameParser.fromDict(d)
                if isinstance(parser, DataFrameParser):
                    self.factory.registerParser(parser=parser, default=default)

    # Reset the contents of the table to the defaults
    def resetToDefaults(self) -> None:
        self.factory.parsers.clear()
        self.factory.setDefaultParsers()
        self.updateTable()

if __name__ == "__main__":

    
    # Test the stand-alone table viewer
    app     = QApplication(sys.argv)
    factory = DataFrameFactory.getInstance()

    # Display an example model
    x     = numpy.arange(-numpy.pi * 2 , numpy.pi * 2, numpy.pi / 16)
    df    = pandas.DataFrame({"X" : x, "Sin(x)" : numpy.sin(x), "Cos(x)" : numpy.cos(x)})
    model = factory.createModel('Example.csv', df) 

    # Create an Table Editor with some example color rules
    color_rule_model = ColorRulesModel()
    color_rule_model.append('Sin(x)', ColorRule(condition='-0.5 < x < 0.5', color=QColor('lime')))
    color_rule_model.append('Sin(x)', ColorRule(condition='abs(x) > 0.7'  , color=QColor('yellow')))
    color_rule_model.append('Sin(x)', ColorRule(condition='abs(x) > 0.9'  , color=QColor('red')))
    color_rule_model.append('Cos(x)', ColorRule(condition='-0.7 < x < 0.7', color=QColor('cyan')))
    color_rule_model.append('Cos(x)', ColorRule(condition='abs(x) > 0.8'  , color=QColor('purple')))
    color_rule_model.append('Cos(x)', ColorRule(condition='abs(x) > 0.9'  , color=QColor('#ff0000')))
    model.setColorRules(color_rule_model)

    editor = ColorRuleEditor(model)
    editor.show()

    # Show the DataFrameParserEditor 
    parserEditor = DataFrameParserEditor()
    parserEditor.show()

    app.exec()