#!/usr/bin/env python

# MIT License

# Copyright (c) 2021 Rafael Arvelo

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
# Class to encapsulate a QDialog used for searching available columns in a dataframe
#

import os
import sys
import typing
import logging

from PyQt5.QtCore    import Qt, QModelIndex, QItemSelection, QSortFilterProxyModel, \
                            pyqtSignal, pyqtSlot, QRegExp, QAbstractItemModel
from PyQt5.QtWidgets import QWidget, QDialog, QListWidgetItem, QHeaderView, QAbstractItemView
from PyQt5.QtGui     import QKeyEvent, QKeySequence

# Update PYTHONPATH
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from ui.ui_searchdialog import Ui_SearchDialog

class SearchDialog(QDialog):
    searchActionRequested = pyqtSignal(str, dict)
    ColumnSearchMode      = 0
    RowSearchMode         = 1
    ChartYAxisSearchMode  = 2

    def __init__(self, 
                 model        : QAbstractItemModel,
                 model_column : int = 0,
                 search_mode  : int = ColumnSearchMode,
                 selected     : typing.Optional[typing.List[str]] = None,
                 parent       : typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.ui                 : Ui_SearchDialog          = Ui_SearchDialog()
        self.model              : QAbstractItemModel       = model
        self.model_column       : int                      = model_column
        self.initial_selection  : typing.List[str]         = selected
        self.proxy_model        : QSortFilterProxyModel    = QSortFilterProxyModel(self)
        self.selected_lookup    : typing.Set[str]          = set()
        self.original_selection : typing.List[QModelIndex] = []
        self.logger             : logging.Logger           = logging.getLogger(__name__)
        self.initUi(search_mode)
    
    # Initialize the widget's user interface
    def initUi(self, search_mode : int):
        self.ui.setupUi(self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterKeyColumn(self.model_column)
        self.ui.availableView.setModel(self.proxy_model)
        for i in range(self.model.columnCount()):
           self.ui.availableView.setColumnHidden(i, i != self.model_column)
        self.ui.availableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.availableView.horizontalHeader().resizeSections(QHeaderView.Stretch)
        self.ui.availableView.horizontalHeader().setVisible(False)

        # Modify the UI based on the search mode
        self.setSearchMode(search_mode)

        # Connect Button signals
        self.ui.cancelButton.pressed.connect(self.reject)
        self.ui.resetButton.pressed.connect(self.reset)
        self.ui.rightButton.pressed.connect(self.onRightPressed)
        self.ui.leftButton.pressed.connect(self.onLeftPressed)
        self.ui.plotButton.pressed.connect(self.onPlotPressed)
        self.ui.showButton.pressed.connect(self.onShowPressed)
        self.ui.hideButton.pressed.connect(self.onHidePressed)
        self.ui.selectButton.pressed.connect(self.onSelectPressed)
        self.ui.unselectAllButton.pressed.connect(self.onUnselectAllPressed)
        self.ui.findPrevButton.pressed.connect(self.onFindPrevPressed)
        self.ui.findNextButton.pressed.connect(self.onFindNextPressed)
        self.ui.caseCheckbox.toggled.connect(self.onCaseSensitivityChanged)

        # Connect other UI Signals
        self.ui.lineEdit.textChanged.connect(self.onSearchTextChanged)
        self.ui.availableView.activated.connect(self.onIndexActivated)
        self.ui.selectedListWidget.activated.connect(self.onIndexActivated)
        self.ui.availableView.selectionModel().selectionChanged.connect(self.onSelectionChanged)
        self.ui.selectedListWidget.selectionModel().selectionChanged.connect(self.onSelectionChanged)

        # Setup initial column selection (if all columns are visible, default to no selection)
        if self.search_mode == self.ColumnSearchMode:
            indexes = [self.model.index(i, 0) for i in range(self.model.rowCount())]
            if any([self.model.data(i, Qt.CheckStateRole) == Qt.Unchecked for i in indexes]):
                for i in indexes:
                    if self.model.data(i, Qt.CheckStateRole) != Qt.Unchecked:
                        self.select(i)
                        self.original_selection.append(i)
                self.ui.resetButton.setEnabled(True)
        elif self.search_mode == self.ChartYAxisSearchMode:
            # Start with the provided column selection
            if isinstance(self.initial_selection, list) and len(self.initial_selection) > 0:
                indexes = [self.model.index(i, 0) for i in range(self.model.rowCount())]
                names   = [index.data(Qt.DisplayRole) for index in indexes]
                for name in self.initial_selection:
                    if name in names:
                        i = names.index(name)
                        self.select(indexes[i])
        
        # Ensure the correct widgets are enabled
        self.updateControls()

        # Return focus to the search line edit
        self.ui.lineEdit.setFocus()
        
        # Initialize the filter
        self.updateFilter("", True, QRegExp.RegExp)

    # Modify the UI based on the search mode
    def setSearchMode(self, search_mode : int) -> None:
        self.search_mode = search_mode
        if self.search_mode == self.RowSearchMode:
            # Only the find next and find prev button should be visible
            self.ui.plotButton.hide()
            self.ui.showButton.hide()
            self.ui.hideButton.hide()
            self.ui.selectButton.hide()
            self.ui.selectedFrame.hide()
            self.ui.leftRightFrame.hide()
            self.ui.availableView.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.ui.availableView.setSelectionMode(QAbstractItemView.SingleSelection)
            new_controls_text  = self.ui.controlsLabel.text().replace("Column", "Row")
            new_available_text = self.ui.availableLabel.text().replace("Available Columns", "Matched Rows")
            self.ui.availableLabel.setText(new_available_text)
            self.ui.controlsLabel.setText(new_controls_text)
            column_name = self.model.headerData(self.model_column, Qt.Horizontal, Qt.DisplayRole)
            self.setWindowTitle(f'Search rows of "{column_name}"')
            self.resize(int(self.width() * 0.75), int(self.height() / 2))
        elif self.search_mode == self.ChartYAxisSearchMode:
            # Only the select button should be visible
            self.ui.plotButton.hide()
            self.ui.showButton.hide()
            self.ui.hideButton.hide()
            self.ui.findPrevButton.hide()
            self.ui.findNextButton.hide()
            self.setWindowTitle("Select 1 or more Y-Axis columns to plot")
        else:
            # Default to ColumnSearchMode
            self.ui.findPrevButton.hide()
            self.ui.findNextButton.hide()
            self.ui.selectButton.hide()

    # Return the currently selected columns
    def currentSelection(self) -> typing.List[QModelIndex]:
        indexes = [] 
        for i in range(self.ui.selectedListWidget.count()):
            index = self.ui.selectedListWidget.item(i).data(Qt.UserRole)
            indexes.append(index)
        return indexes

    # Update the internal column filter
    def updateFilter(self, text : str, caseSensitive : bool , syntax : int):
        case_sensitivity = Qt.CaseSensitive if caseSensitive else Qt.CaseInsensitive
        self.proxy_model.setFilterRegExp(QRegExp(text, case_sensitivity, syntax))
        self.ui.availableView.clearSelection()
        self.ui.availableView.setModel(self.proxy_model)
        self.ui.rowCount.setText(str(self.proxy_model.rowCount()))

    # Enable / Disable UI Buttons based on user actions
    def updateControls(self) -> None:
        left_count           = self.ui.availableView.model().rowCount()
        right_count          = self.ui.selectedListWidget.count()
        left_selected_count  = len(self.ui.availableView.selectionModel().selection())
        right_selected_count = len(self.ui.selectedListWidget.selectedItems())
        any_left             = bool(left_count > 0)
        any_right            = bool(right_count > 0)

        # Update the UI based on the selection
        self.ui.rightButton.setEnabled(left_selected_count > 0)
        self.ui.leftButton.setEnabled(right_selected_count > 0)
        self.ui.plotButton.setEnabled(any_right)
        self.ui.showButton.setEnabled(any_right)
        self.ui.hideButton.setEnabled(any_right)
        self.ui.selectButton.setEnabled(any_right)
        self.ui.unselectAllButton.setEnabled(any_right)
        self.ui.findPrevButton.setEnabled(any_left)
        self.ui.findNextButton.setEnabled(any_left)

    # Resets the state of the entire user interface
    @pyqtSlot()
    def reset(self, restore_original_selection : bool = True):
        self.ui.lineEdit.clear()
        self.ui.availableView.clearSelection()
        self.ui.selectedListWidget.clear()
        for i in range(self.proxy_model.rowCount()):
            self.ui.availableView.setRowHidden(i, False)
        self.selected_lookup.clear()

        # Reset back to the originally selected list
        if restore_original_selection:
            self.selectList(self.original_selection)

        # Enable / Disable controls based on selection
        self.updateControls()

        # Return focus to the search line edit
        self.ui.lineEdit.setFocus()

    # Handler for when the search line edit text changes
    @pyqtSlot(str)
    def onSearchTextChanged(self, text : str):
        self.updateFilter(text, self.ui.caseCheckbox.isChecked(), self.ui.syntaxComboBox.currentIndex())

    # Handler for when the case sensitivity check box changes
    @pyqtSlot(bool)
    def onCaseSensitivityChanged(self, caseSensitive : bool):
        self.updateFilter(self.ui.lineEdit.text(), caseSensitive, self.ui.syntaxComboBox.currentIndex())

    # Handler for when the pattern syntax combo box changes
    @pyqtSlot(int)
    def onPatternSyntaxChanged(self, syntax : int):
        self.updateFilter(self.ui.lineEdit.text(), self.ui.caseCheckbox.isChecked(), syntax)

    # Handler for when a key is pressed
    def keyPressEvent(self, e : QKeyEvent) -> None:
        if e.matches(QKeySequence.SelectAll) or (e.key() == Qt.Key_A and e.modifiers() == Qt.ControlModifier):
            if self.ui.availableView.hasFocus():
                self.ui.availableView.selectAll()
            elif self.ui.selectedListWidget.hasFocus():
                self.ui.selectedListWidget.selectAll()
            elif self.ui.lineEdit.hasFocus():
                self.ui.lineEdit.selectAll()
        super().keyPressEvent(e)

    # Handler for when the plot button is pressed
    @pyqtSlot()
    def onPlotPressed(self):
        selected_columns = self.currentSelection()
        if (len(selected_columns) > 0):
            column_names = [index.data(Qt.DisplayRole) for index in selected_columns]
            kwargs       = {"columns" : column_names}
            self.searchActionRequested.emit("plotColumns", kwargs)
        self.accept()

    # Handler for when the show button is pressed
    @pyqtSlot()
    def onShowPressed(self):
        selected_columns = self.currentSelection()
        if (len(selected_columns) > 0):
            column_indexes = [index.row() for index in selected_columns]
            kwargs         = {"columns" : column_indexes}
            self.searchActionRequested.emit("hideOtherColumns", kwargs)
        self.accept()

    # Handler for when the hide button is pressed
    @pyqtSlot()
    def onHidePressed(self):
        selected_columns = self.currentSelection()
        if (len(selected_columns) > 0):
            column_indexes = [index.row() for index in selected_columns]
            kwargs         = {"columns" : column_indexes}
            self.searchActionRequested.emit("hideColumns", kwargs)
        self.accept()

    # Handler for when the right button is pressed
    @pyqtSlot()
    def onRightPressed(self):
        for row in self.ui.availableView.selectionModel().selectedRows():
            self.select(row)
        self.ui.availableView.clearSelection()
        self.ui.selectedListWidget.clearSelection()

    # Handler for when the left button is pressed
    @pyqtSlot()
    def onLeftPressed(self):
        # Only contiguous selections are supported for deletion
        selection = self.ui.selectedListWidget.selectionModel().selectedRows()
        first_row = min([index.row() for index in selection])
        count     = len(selection)
        while count > 0:
            self.unselect(first_row)
            count -= 1
        self.ui.availableView.clearSelection()
        self.ui.selectedListWidget.clearSelection()

    # Handler for when the reset button is pressed
    @pyqtSlot()
    def onUnselectAllPressed(self):
        self.reset(restore_original_selection = False)

    # Handler for when the find previous button is pressed
    @pyqtSlot()
    def onFindPrevPressed(self):
        selection = self.ui.availableView.selectionModel().selectedRows()
        prev_row  = self.proxy_model.rowCount() - 1
        if isinstance(selection, list) and len(selection) > 0:
            prev_row = selection[0].row() - 1
        if prev_row < 0:
            prev_row = self.proxy_model.rowCount() - 1
        self.ui.availableView.selectRow(prev_row)

    # Handler for when the find next button is pressed
    @pyqtSlot()
    def onFindNextPressed(self):
        selection = self.ui.availableView.selectionModel().selectedRows()
        next_row  = 0
        if isinstance(selection, list) and len(selection) > 0:
            next_row = selection[0].row() + 1
        if next_row >= self.proxy_model.rowCount():
            next_row = 0
        self.ui.availableView.selectRow(next_row)

    # Handler for when the select button is pressed
    @pyqtSlot()
    def onSelectPressed(self):
        selected_columns = self.currentSelection()
        if (len(selected_columns) > 0):
            column_names = [index.data(Qt.DisplayRole) for index in selected_columns]
            kwargs       = {"columns" : column_names}
            self.searchActionRequested.emit("selectYColumns", kwargs)
        self.accept()

    # Update the UI when the column selection changes
    @pyqtSlot(QItemSelection, QItemSelection)
    def onSelectionChanged(self, selected : QItemSelection, deselected : QItemSelection):
        # Arguments are intentionlly unused here
        selected, deselected = selected, deselected
        self.updateControls()
        if self.search_mode == self.RowSearchMode:
            selection = self.ui.availableView.selectionModel().selectedRows()
            if len(selection) > 0:
                tmp_index    = self.proxy_model.mapToSource(selection[0])
                source_index = self.model.index(tmp_index.row(), self.model_column)
                kwargs = { "index" : source_index }
                self.searchActionRequested.emit("scrollTo", kwargs)

    # Update selection when the left or right list views are activated
    @pyqtSlot(QModelIndex)
    def onIndexActivated(self, index : QModelIndex):
        view = self.sender()
        if view == self.ui.availableView:
            self.select(index)
        elif view == self.ui.selectedListWidget:
            self.unselect(index.row())
        else:
            self.logger.warning(f"Invalid index activated {index}")

    # Select a single column
    @pyqtSlot(str)
    def select(self, index : QModelIndex):
        proxy_index = self.proxy_model.index(index.row(), self.proxy_model.filterKeyColumn())
        source_index = self.proxy_model.mapToSource(proxy_index)

        if source_index.isValid():
            text = source_index.data(Qt.DisplayRole)
            if not(text in self.selected_lookup):
                item = QListWidgetItem(text)
                item.setData(Qt.UserRole, source_index)
                self.selected_lookup.add(text)
                self.ui.selectedListWidget.addItem(item)

            self.updateControls()
            return True

        return False

    # Unselect a single column
    @pyqtSlot()
    def unselect(self, row : int) -> bool:
        if row < self.ui.selectedListWidget.count():
            item = self.ui.selectedListWidget.takeItem(row)
            if item and item.text() in self.selected_lookup:
                self.selected_lookup.remove(item.text())
            del item
            self.updateControls()
            return True
        
        return False

    # Convenience function to select mutliple columns at once
    def selectList(self, index_list : typing.List[QModelIndex]):
        for index in index_list:
            self.select(index)