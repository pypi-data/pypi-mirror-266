#!/usr/bin/env python

# MIT License

# Copyright (c) 2021-2024 Rafael Arvelo

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
# This file contains the classes for the main TableView UI of the DataViewer application
#
# pylint: disable-all

import os
import sys
import json
import typing
import pandas
import numpy
import logging
from   collections import namedtuple
from   pathlib     import Path

# Application paths
DATAVIEWER_BASE_PATH = os.path.dirname(os.path.realpath(__file__))
REPOSITORY_BASE_PATH = str(Path(DATAVIEWER_BASE_PATH).parent.absolute())
TABLE_SETTINGS_PATH  = os.path.join(DATAVIEWER_BASE_PATH, "table_settings")
IMAGES_PATH          = os.path.join(DATAVIEWER_BASE_PATH, "ui", "images")

# Update PYTHONPATH
sys.path.append(DATAVIEWER_BASE_PATH)
sys.path.append(IMAGES_PATH)

from   PyQt5.QtGui       import QKeyEvent, QKeySequence, QStandardItem, QStandardItemModel, QDesktopServices, QColor, QIcon, QPixmap
from   PyQt5.QtWidgets   import QApplication, QFileDialog, QInputDialog, QTableView, QWidget, QHeaderView, QDialog, QCompleter, \
                                QMenu, QAbstractItemView, QMessageBox, QAction
from   PyQt5.QtCore      import QPoint, Qt, QModelIndex, QSortFilterProxyModel, QDir, QUrl, QSettings, pyqtSlot

from   ui.ui_tableviewer import Ui_TableViewer
from   dataframemodel    import ColorRule, ColorRulesModel, PlotInfoListModel, DataFrameModel, DataFrameFactory, PlotInfo, delta, \
                                SETTINGS_FILENAME
from   dataviewerutils   import QueryListEditor, ColorRuleEditor, ColorRuleEditorDelegate, LineEditDelegate, SavedPlotsEditor
from   searchdialog      import SearchDialog
from   customchartdialog import CustomChartDialog

#####################
# Globals
#####################

# Symbols can be added here to be made available in column formulas
EVAL_SYMBOLS_DICT = {
  "pandas" : pandas,
  "delta"  : delta,
  **{ x : getattr(numpy, x) for x in ["sin", "cos", "tan", "pi", "e",
                                      "arcsin", "arccos", "arctan", 
                                      "arcsinh", "arccosh", "arctanh", 
                                      "min", "max", "abs", "exp", "absolute",
                                      "mean", "median", "average", "floor", "ceil",
                                      "cumsum", "cumprod", "square", "sqrt",
                                      "any", "all", "nonzero", "zeros", "alltrue", "allclose",
                                      "bitwise_and", "bitwise_or", "bitwise_xor", "bitwise_not",
                                      "diff", "diag", "array_equal", "cross", "dot",
                                      "deg2rad", "rad2deg", "radians", "degrees"]}
}

#####################
# Helper Functions
#####################
# Convenience function to set a value from settings
def setFromDict(key : str, map : dict, type, func, **kwargs):
    keys = map.keys()
    if key in keys:
        value = map[key]
        if value != None and isinstance(value, type):
            func(value, **kwargs)

def isStringValid(string : str) -> bool:
    """
    Validate the given string

    *Parameters:*

    string : str
        Any python string object

    *Returns:*

    True if string has valid characters
    """
    return isinstance(string, str) and len(string) > 0

def isIndexValid(index : int, numColumns : int) -> bool:
    """
    Validate the given column index

    *Parameters:*

    index : int
        Numeric index to be validated

    numColumns : int
        Number of columns

    *Returns:*

    True if index is valid
    """
    return isinstance(index, int) and index >= 0 and index < numColumns

# Convert a Query List Model to a list of dictionaries
def queryModelToList(model : QStandardItemModel) -> typing.List[typing.Dict[str, typing.Any]]:
    result = []
    for i in range(model.rowCount()):
        item = model.item(i, 0)
        if isinstance(item, QStandardItem):
            value_dict = {}
            value_dict["query"]   = item.data(Qt.DisplayRole)
            value_dict["enabled"] = bool(item.checkState() == Qt.Checked)
            result.append(value_dict)
    return result

# Convert a list of dictionaries to a Query List Model 
def listToQueryListModel(a_list : typing.List[typing.Dict[str, typing.Any]]) -> QStandardItemModel:
    result = QStandardItemModel()
    for dictionary in a_list:
        if isinstance(dictionary, dict) and all([k in dictionary.keys() for k in ["query", "enabled"]]):
            item = QStandardItem(dictionary["query"])
            item.setCheckState(Qt.Checked if dictionary["enabled"] else Qt.Unchecked)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsUserCheckable)
            result.appendRow(item)
    return result

#####################
# Classes
#####################

TABLE_OPERATIONS = ['applyFormula', 'copyColumns', 'insertColumn', 'editCell', 'deleteColumns', 'renameColumn', 'sortByColumn']
class TableOperation(namedtuple('TableOperaton', ['operation', 'data'])):
    def isValid(self) -> bool:
        return self.operation in TABLE_OPERATIONS and isinstance(self.data, dict)

# A simple QCompleter subclass to provide "IDE"-like code
# completion for column names in a table model
class ColumnCompleter(QCompleter):

    DELIMITER = " `"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
    
    def pathFromIndex(self, index : QModelIndex) -> str:
        
        # The default implementation will return the completion text
        # whenever the user activates the completion
        column_name    = super().pathFromIndex(index)
        completed_text = column_name

        # Obtain the current text from the internal widget
        widget = self.widget()
        if hasattr(widget, "text"):
            text_func = getattr(widget, "text")
            if callable(text_func):
                text       = str(text_func())
                split_text = text.split(self.DELIMITER)
                if len(split_text) > 1:
                    # Grab all of the text before the first delimeter
                    original_text = self.DELIMITER.join(split_text[:-1])

                    # Append the column name after the last delimiter
                    completed_text = f"{original_text} {column_name}"
            else:
                self.logger.debug(f"Invalid text function {text_func} from widget {widget}. Using default completion text")
        else:
            self.logger.debug(f"Invalid widget {widget}. Using default completion text")

        return completed_text
    
    def splitPath(self, path : str) -> typing.List[str]:
        # All column names should be encapsulated in ` characters. 
        # Return the text after the last delimiter to complete the code 
        # completion
        last_item = path.split(self.DELIMITER)[-1:]
        return last_item

class TableViewer(QWidget):
    settings_filter = 'JSON Files *.json;;All Files *'
    save_filter     = '{name} Files *{suffix};;All Files *'
    """ QTableView that works with DataFrameModel """
    def __init__(self,
                 model  : DataFrameModel,
                 parent : QWidget        = None):
        super().__init__(parent=parent)
        self.ui            = Ui_TableViewer()
        self.model         = model
        self.orig_model    = model
        self.column_model  = QStandardItemModel()
        self.query_model   = QStandardItemModel()
        self.column_proxy  = QSortFilterProxyModel()
        self.settings      = {}
        self.formulas          : typing.Dict[str, str]       = {}
        self.saved_plots_model : PlotInfoListModel             = PlotInfoListModel()
        self.operations        : typing.List[TableOperation] = []
        self.factory           : DataFrameFactory            = DataFrameFactory.getInstance()
        self.logger            : logging.Logger              = logging.getLogger(__name__)
        self.x_icon = QIcon()
        self.x_icon.addPixmap(QPixmap(":/x-logo.png"), QIcon.Normal, QIcon.Off)
        self.initUI()
        self.initContextMenu()
        self.updateSettings()
        self.setEditable(True)

        # Only freeze the first column for tables for many columns
        if self.model.columnCount() == 1:
            sizes = self.ui.horizontalSplitter.sizes()
            self.ui.freezeColCheckBox.setChecked(False)
            self.firstColumnView.hide()
            if len(sizes) == 2:
                sizes[0] = 0
                sizes[1] = self.width()
                self.ui.horizontalSplitter.setSizes(sizes)
        else:
            sizes = self.ui.horizontalSplitter.sizes()
            if len(sizes) == 2:
                self.ui.horizontalSplitter.setSizes([475, 1200])

        self.onSelectionChanged()
        
        # Re-apply queries when the query model is updated
        self.queries_enabled = True
        self.query_model.itemChanged.connect(self.applyAllQueries)

    def initUI(self):
        self.ui.setupUi(self)
        self.firstColumnView = QTableView(self.ui.tableView)
        self.setModel(self.model)
        self.initFirstColumnView()
        self.setEditable(False)
        self.column_model.itemChanged.connect(self.onItemChanged)
        self.column_proxy.setSourceModel(self.column_model)
        self.column_proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.column_proxy.dataChanged.connect(self.onDataChanged)
        self.ui.showUncheckedCheckBox.stateChanged.connect(self.onShowUncheckedChanged)
        self.ui.columnList.setModel(self.column_proxy)
        self.ui.queryListView.setModel(self.query_model)
        self.ui.columnSearch.textChanged.connect(self.column_proxy.setFilterRegExp)
        self.ui.resetButton.clicked.connect(self.reset)
        self.ui.plotButton.clicked.connect(self.plotColumns)
        self.ui.customPlotButton.clicked.connect(self.onCustomPlotClicked)
        self.ui.newPlotButton.clicked.connect(self.onCustomPlotClicked)
        self.ui.applyButton.clicked.connect(self.onApplyClicked)
        self.ui.columnList.activated.connect(self.onIndexActivated)
        self.ui.clearAllButton.clicked.connect(self.clearAllColumns)
        self.ui.selectAllButton.clicked.connect(self.selectAllColumns)
        self.ui.editableCheckBox.clicked.connect(self.setEditable)
        self.ui.showButton.clicked.connect(self.showColumns)
        self.ui.hideButton.clicked.connect(self.hideColumns)
        self.ui.hideOthersButton.clicked.connect(self.hideOtherColumns)
        self.ui.insertColumnButton.clicked.connect(self.insertColumn)
        self.ui.saveSettingsButton.clicked.connect(self.saveSettingsToFile)
        self.ui.loadSettingsButton.clicked.connect(self.readSettingsFromFile)
        self.ui.tableView.horizontalHeader().setSelectionBehavior(QAbstractItemView.SelectColumns)
        self.ui.tableView.horizontalHeader().selectionModel().selectionChanged.connect(self.onSelectionChanged)
        self.ui.tableView.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tableView.horizontalHeader().customContextMenuRequested.connect(self.onContextMenuRequested)
        self.ui.columnList.selectionModel().selectionChanged.connect(self.onListSelectionChanged)
        self.ui.tableView.customContextMenuRequested.connect(self.onContextMenuRequested)
        self.ui.formulaEdit.textChanged.connect(self.onFormulaChanged)
        self.ui.formulaEdit.returnPressed.connect(self.onApplyClicked)
        self.ui.formulaHelpButton.pressed.connect(self.onFormulaHelpPressed)
        self.ui.searchButton.pressed.connect(self.find)
        self.ui.queryLineEdit.textChanged.connect(self.onQueryTextChanged)
        self.ui.queryLineEdit.returnPressed.connect(self.onAddQueryButtonPressed)
        self.ui.addQueryButton.pressed.connect(self.onAddQueryButtonPressed)
        self.ui.editQueriesButton.pressed.connect(self.onEditQueriesButtonPressed)
        self.ui.queryHelpButton.pressed.connect(self.onQueryHelpPressed)
        self.ui.colorRuleLineEdit.textChanged.connect(self.onColorRuleTextChanged)
        self.ui.colorRuleLineEdit.returnPressed.connect(self.onAddColorRulePressed)
        self.ui.colorRuleLineEdit.setToolTip(ColorRulesModel.CONDITION_TOOLTIP)
        self.ui.colorRuleHelpButton.pressed.connect(self.onColorRulesHelpPressed)
        self.ui.addColorRuleButton.pressed.connect(self.onAddColorRulePressed)
        self.ui.editColorRulesButton.pressed.connect(self.showColorEditor)
        self.ui.editSavedPlotsButtons.pressed.connect(self.onEditSavedPlotsButtonPressed)
        self.ui.plotAllButton.pressed.connect(self.onPlotAllPressed)
        self.ui.savedPlotsTableView.activated.connect(self.onSavedPlotsTableIndexActivated)
        self.ui.savedPlotsTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.savedPlotsTableView.setModel(self.saved_plots_model)
        self.ui.filePathLabel.setText(self.model.filename)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        # Autofit the columns if the table is not too large
        settings = QSettings(SETTINGS_FILENAME, QSettings.IniFormat)
        autofitColumnMax = int(settings.value("autofitColumnMax", 100))
        if self.model.columnCount() < autofitColumnMax:
            self.autofitColumns()

        # Initialize the color combo box
        color_index = 0
        for color_name in QColor.colorNames():
            color = QColor(color_name)
            if color_name == "lime":
                color_index = self.ui.colorComboBox.count()
            self.ui.colorComboBox.addItem(color_name, color)
            self.ui.colorComboBox.setItemData(self.ui.colorComboBox.count()-1, color, Qt.DecorationRole)
        self.ui.colorComboBox.setCurrentIndex(color_index)

    def initContextMenu(self):
        self.context_menu = QMenu("Table Actions", self)
        
        # Actions to modify internal contents
        self.apply_formula_menu    = self.context_menu.addMenu("Apply Formula")
        self.apply_delta_action    = self.apply_formula_menu.addAction("Delta (diff row values)", self.insertColumnDelta)
        self.apply_min_action      = self.apply_formula_menu.addAction("Minimum"                , self.insertColumnMin)
        self.apply_max_action      = self.apply_formula_menu.addAction("Maximum"                , self.insertColumnMax)
        self.apply_cum_min_action  = self.apply_formula_menu.addAction("Cumulative Minimum"     , self.insertColumnCumMin)
        self.apply_cum_max_action  = self.apply_formula_menu.addAction("Cumulative Maximum"     , self.insertColumnCumMax)
        self.apply_sum_action      = self.apply_formula_menu.addAction("Sum of row values"      , self.insertColumnSum)
        self.apply_std_action      = self.apply_formula_menu.addAction("Standard deviation"     , self.insertColumnStd)
        self.apply_average_action  = self.apply_formula_menu.addAction("Mean (average)"         , self.insertColumnAvg)
        self.apply_median_action   = self.apply_formula_menu.addAction("Median"                 , self.insertColumnMedian)
        self.custom_formula_action = self.apply_formula_menu.addAction("Custom Formula"         , self.insertCustomFormula)

        self.add_column_action     = self.context_menu.addAction("Insert Column"    , self.insertColumn)
        self.rename_column_action  = self.context_menu.addAction("Rename Column"    , self.renameColumn)
        self.copy_column_action    = self.context_menu.addAction("Copy Column(s)"   , self.copyColumns)
        self.delete_column_action  = self.context_menu.addAction("Delete Column(s)" , self.deleteColumns)
        self.sort_action           = self.context_menu.addAction("Sort Column"      , self.sortByColumn)
        self.get_statistics_action = self.context_menu.addAction("Get Statistics"   , self.getStatistics)
        self.hide_columns_action  = self.context_menu.addAction("Hide Column(s)"      , self.hideColumns)
        self.hide_others_action   = self.context_menu.addAction("Hide Other Column(s)", self.hideOtherColumns)
        self.unhide_all_action    = self.context_menu.addAction("Unhide All Column(s)", self.selectAllColumns)
        self.autofit_cols_action  = self.context_menu.addAction("Autofit Column(s)"   , self.autofitColumns)
        self.color_format_action  = self.context_menu.addAction("Edit Color Rules"    , self.showColorEditor)
        self.load_settings_action = self.context_menu.addAction("Load Settings"       , self.readSettingsFromFile)
        self.save_settings_action = self.context_menu.addAction("Save Settings"       , self.saveSettingsToFile)
        self.save_to_file_action  = self.context_menu.addAction("Export Table to CSV" , self.saveModelToFile)
        self.save_to_file_menu    = self.context_menu.addMenu("Export Table to Other Format")
        for parser_key, parser in DataFrameFactory.getInstance().parsers.items():
            if parser.name == "CSV":
                action = self.save_to_file_action
            else:
                action = self.save_to_file_menu.addAction(parser.name, self.saveModelToFile)
            action.setData({"name" : parser.name, "suffix" : parser.suffix, "key" : parser_key})
    
    def initFirstColumnView(self):
        self.firstColumnView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.firstColumnView.setFocusPolicy(Qt.NoFocus)
        self.firstColumnView.verticalHeader().hide()
        self.firstColumnView.setAlternatingRowColors(self.ui.tableView.alternatingRowColors())
        self.firstColumnView.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.firstColumnView.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.firstColumnView.horizontalHeader().setSelectionBehavior(QAbstractItemView.SelectColumns)
        self.firstColumnView.horizontalHeader().customContextMenuRequested.connect(self.onContextMenuRequested)
        self.firstColumnView.horizontalHeader().selectionModel().selectionChanged.connect(self.onSelectionChanged)

        self.ui.tableView.viewport().stackUnder(self.firstColumnView)
        self.firstColumnView.setColumnHidden(0, False)
        for i in range(1, self.model.columnCount()):
            self.firstColumnView.setColumnHidden(i, True)

        self.firstColumnView.setColumnWidth(0, self.ui.tableView.columnWidth(0))
        self.firstColumnView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.firstColumnView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.firstColumnView.show()

        self.updateFirstColumnGeometry()

        self.ui.tableView.setHorizontalScrollMode(QTableView.ScrollPerPixel)
        self.ui.tableView.setVerticalScrollMode(QTableView.ScrollPerPixel)
        self.firstColumnView.setVerticalScrollMode(QTableView.ScrollPerPixel)
        self.ui.freezeColCheckBox.clicked.connect(self.firstColumnView.setVisible)

        self.ui.tableView.scrollTo            = self.scrollTo
        self.ui.tableView.moveCursor          = self.moveCursor
        self.ui.tableView.resizeEvent         = self.resizeEvent
        self.ui.tableView.updateSectionWidth  = self.updateSectionWidth
        self.ui.tableView.updateSectionHeight = self.updateSectionHeight

        self.ui.tableView.horizontalHeader().sectionResized.connect(self.updateSectionWidth)
        self.ui.tableView.verticalHeader().sectionResized.connect(self.updateSectionHeight)
        self.firstColumnView.verticalScrollBar().valueChanged.connect(self.ui.tableView.verticalScrollBar().setValue)
        self.ui.tableView.verticalScrollBar().valueChanged.connect(self.firstColumnView.verticalScrollBar().setValue)
    
    def updateFirstColumnGeometry(self):
        if self.ui.tableView.verticalHeader().isVisible():
            self.firstColumnView.setGeometry(self.ui.tableView.verticalHeader().width() + self.ui.tableView.frameWidth(),
                                             self.ui.tableView.frameWidth(), self.ui.tableView.columnWidth(0),
                                             self.ui.tableView.viewport().height() + self.ui.tableView.horizontalHeader().height())
        else:
            self.firstColumnView.setGeometry(self.ui.tableView.frameWidth(),
                                             self.ui.tableView.frameWidth(), self.ui.tableView.columnWidth(0),
                                             self.ui.tableView.viewport().height() + self.ui.tableView.horizontalHeader().height() * 2)

    def updateSectionWidth(self, logicalIndex, oldSize, newSize):
        if logicalIndex == 0 or logicalIndex == 1:
            self.firstColumnView.setColumnWidth(logicalIndex, newSize)
            self.updateFirstColumnGeometry()

    def updateSectionHeight(self, logicalIndex, oldSize, newSize):
        self.firstColumnView.setRowHeight(logicalIndex, newSize)

    def resizeEvent(self, event):
        QTableView.resizeEvent(self.ui.tableView, event)
        self.updateFirstColumnGeometry()

    def scrollTo(self, index : QModelIndex, hint : QAbstractItemView.ScrollHint = QAbstractItemView.PositionAtTop):
        if index.column() >= 0:
            QTableView.scrollTo(self.ui.tableView, index, hint)

    def moveCursor(self, cursorAction, modifiers):
        current = QTableView.moveCursor(self.ui.tableView, cursorAction, modifiers)
        x = self.ui.tableView.visualRect(current).topLeft().x()
        frozen_width = self.firstColumnView.columnWidth(0) + self.firstColumnView.columnWidth(1)
        if cursorAction == self.ui.tableView.MoveLeft and current.column() > 1 and x < frozen_width:
            new_value = self.ui.tableView.horizontalScrollBar().value() + x - frozen_width
            self.ui.tableView.horizontalScrollBar().setValue(new_value)
        return current

    def dictToColumnList(self, columnMap : dict, fillValue : typing.Any ) -> list:
        items = []
        if not(isinstance(columnMap, dict)) or len(columnMap.keys()) < 1:
            items = [fillValue] * self.model.columnCount()
        else:
            for i in range(self.model.columnCount()):
                col = self.model.df.columns[i]
                if col in columnMap.keys():
                    items.append(columnMap[col])
                else:
                    items.append(fillValue)
        return items
    
    def columnListToDict(self, items : list, fillValue : typing.Any) -> dict:
        itemMap = {}
        if len(items) == self.model.columnCount():
            for i in range(len(items)):
                col = self.model.df.columns[i]
                if items[i] != fillValue:
                    itemMap[col] = items[i]
        
        return itemMap
    
    def getInsertionIndex(self, index : int = None) -> int:
        """
        Return a valid index to insert a new table column

        *Parameters:*
    
        index : int
            Valid column index (0 to num_columns -1) or None

        *Returns:*
    
        Given index if valid, otherwise end of columns
        """
        if not(isIndexValid(index, self.model.columnCount())):
            columns = self.getSelectedColumns()
            if len(columns) > 0:
                index = columns[-1]
            elif self.model.columnCount() < 1:
                index = 0
            else:
                index = self.model.columnCount()-1
        return index
    
    # Update the Query Model from a settings list
    def setQueryModel(self, dict_list : typing.List[typing.Dict[str, any]]):
        self.query_model = listToQueryListModel(dict_list)
        self.query_model.itemChanged.connect(self.applyAllQueries)
        self.ui.queryListView.setModel(self.query_model)
        self.applyAllQueries()

    # Update the Saved Plots Model from a settings list
    def setSavedPlotsModel(self, dict_list : typing.List[typing.Dict[str, any]]):
        self.saved_plots_model = PlotInfoListModel.fromJson(self.model.df, dict_list)
        self.ui.savedPlotsTableView.setModel(self.saved_plots_model)
        self.onSavedPlotsChanged()

    def updateSettings(self):
        self.settings['formulas']             = self.formulas
        self.settings['customXAxis']          = self.ui.xAxisCheckBox.isChecked()
        self.settings['editable']             = self.ui.editableCheckBox.isChecked()
        self.settings['freezeFirstColumn']    = self.ui.freezeColCheckBox.isChecked()
        self.settings['showUncheckedColumns'] = self.ui.showUncheckedCheckBox.isChecked()
        self.settings['colorRules']           = self.model.color_rules_model.toJson()
        self.settings['queryList']            = queryModelToList(self.query_model)
        self.settings['columnFilter']         = self.ui.columnSearch.text()
        self.settings['currentPage']          = self.ui.tabWidget.currentIndex()
        self.settings['savedPlots']           = self.saved_plots_model.toJson()
        selectedColumns = []
        for i in range(self.column_model.rowCount()):
            index = self.column_model.index(i, 0)
            selectedColumns.append(bool(self.column_model.data(index, Qt.CheckStateRole)))
        if any([sel == False for sel in selectedColumns]):
            self.settings['selectedColumns'] = self.columnListToDict(selectedColumns, fillValue=False)
        else:
            self.settings['selectedColumns'] = {}
        self.settings['operations']      = [op._asdict() for op in self.operations]
    
    def setSettings(self, settings : dict) -> bool:
        success = True
        if isinstance(settings, dict):
            self.settings = settings

            # Must perform operations first to ensure the table is valid
            if 'operations' in settings.keys():
                operations = [TableOperation(**d) for d in settings['operations']]
                if len(operations) > 0:
                    self.setEditable(True) # Allow edits to perform operations
                for op in operations:
                    try:
                        if not(self.performOperation(op)):
                            success = False
                            break
                    except:
                        self.logger.error(f"Error occured during operation {op}")
                        success = False
                        break

            # Now apply table settings
            setFromDict('editable'            , settings, int , self.setEditable)
            setFromDict('freezeFirstColumn'   , settings, int , self.firstColumnView.setVisible)
            setFromDict('customXAxis'         , settings, bool, self.ui.xAxisCheckBox.setChecked)
            setFromDict('queryList'           , settings, list, self.setQueryModel)
            setFromDict('savedPlots'          , settings, list, self.setSavedPlotsModel)
            setFromDict('columnFilter'        , settings, str , self.ui.columnSearch.setText)
            setFromDict('currentPage'         , settings, int , self.ui.tabWidget.setCurrentIndex)
            setFromDict('showUncheckedColumns', settings, bool, self.ui.showUncheckedCheckBox.setChecked)

            selectedColumns = [True] * self.model.columnCount()
            if 'selectedColumns' in settings.keys():
                selectedColumns = self.dictToColumnList(settings['selectedColumns'], fillValue=False)
                if all([sel == False for sel in selectedColumns]):
                    selectedColumns = [True] * self.model.columnCount()
            self.setSelectedColumns(selectedColumns)

            if 'formulas' in settings.keys():
                self.formulas = settings['formulas']

            if 'colorRules' in settings.keys():
                rules_model = ColorRulesModel.fromJson(settings['colorRules'])
                self.model.setColorRules(rules_model)
                self.ui.colorRulesTableView.setModel(self.model.color_rules_model)
                self.model.colorRulesChanged.connect(self.onColorRulesChanged)
                self.model.color_rules_model.colorRulesChanged.connect(self.onColorRulesChanged)

        return success
    
    def saveSettingsToFile(self, filename : str = None):
        self.context_menu.hide()
        if not(isinstance(filename, str)) or len(filename) < 1:
            filename = QFileDialog.getSaveFileName(self, "Input Save Filename", TABLE_SETTINGS_PATH, self.settings_filter)[0]
        if isinstance(filename, str) and len(filename) > 0:
            if not(filename.endswith('.json')):
                filename += '.json'
            self.updateSettings()
            with open(filename, 'w') as file:
                json.dump(self.settings, file, indent=2)
        else:
            self.logger.error(f"Unable to save to file \"{filename}\"")
    
    def readSettingsFromFile(self, filename : str = None):
        self.context_menu.hide()
        base_path = TABLE_SETTINGS_PATH if os.path.exists(TABLE_SETTINGS_PATH) else os.path.expanduser("~")
        if not(isinstance(filename, str)) or len(filename) < 1:
            filename = QFileDialog.getOpenFileName(self, "Select Settings File", base_path, self.settings_filter)[0]
        if isinstance(filename, str) and len(filename) > 0:
            if not(filename.endswith('.json')):
                filename += '.json'
            with open(filename, 'r') as file:
                settings = json.load(file)
                self.setSettings(settings)
    
    def performOperation(self, op : TableOperation) -> bool:
        if op.isValid():
            func = getattr(self, op.operation)
            self.logger.debug(f"Performing operation: {func} with arguments {op.data}")
            if func(**op.data):
                return True
            else:
                self.logger.error(f"Failed to perform operation: {op}")
        else:
            self.logger.warning(f"The operation is invalid: {op}")
        return False
    
    def logOperation(self, operation : str, **data):
        self.operations.append(TableOperation(operation=operation, data=data))

    def showColorEditor(self):
        self.colorRuleEditor = ColorRuleEditor(model=self.model)
        self.colorRuleEditor.show()
    
    # Save the given file to a custom format
    def saveModelToFile(self, filename : str = None):
        self.context_menu.hide()
        factory = DataFrameFactory.getInstance()

        # Open a file dialog if this function is triggered from an action
        action = self.sender()
        if isinstance(action, QAction):
            info = action.data()
            if isinstance(info, dict) and all([k in info.keys() for k in ("name", "suffix", "key")]):
                file_filter = self.save_filter.format(**info)
                filename    = QFileDialog.getSaveFileName(self, "Input Save Filename", QDir.currentPath(), file_filter)[0]
                if not(filename.endswith(info["suffix"])):
                    filename += info["suffix"]
                parser = factory.parsers.get(info["key"], factory.getParser(filename))
            else:
                self.logger.debug(f"Invalid Action Data {info} in action {action}")
        else:
            parser = factory.getParser(filename)
        
        if len(filename) > 0:
            success = factory.saveModelToFile(self.model.df, filename, parser=parser)
        else:
            success = False

        if not(success):
            self.logger.error(f"Unable to save content to file: \"{filename}\"")

        return success
    
    def sortByColumn(self, column : int = None) -> bool:
        if not(self.ui.editableCheckBox.isChecked()):
            self.logger.debug(f"Operation (sortByColumn) failed, table not editable")
            return False
        if not(isinstance(column, int)) or column < 0 or column >= self.column_model.rowCount():
            indexes = self.getSelectedColumns()
            if len(indexes) > 0:
                column = indexes[0]
        if isinstance(column, int) and column >= 0 and column < self.column_model.rowCount():
            if self.model.sortByColumn(column):
                self.logOperation('sortByColumn', column=column)
                self.setModel(self.model)
                return True
        return False

    def getStatistics(self, columns : typing.List[str] = None) -> bool:
        if not(isinstance(columns, list)) or len(columns) < 1 or any([type(col) != str for col in columns]):
            columns = self.getSelectedColumns(names=True)
        if isinstance(columns, list) and len(columns) > 0 and all([type(col) == str for col in columns]):
            try:
                description = self.model.df[columns].describe().to_string()
            except Exception as e:
                description = f"Error generating stats: {e}"
            
            QMessageBox.information(self, "Column Statistics", description)
            return True
            
        return False

    def deleteColumns(self, columns : typing.List[str] = None, ask : bool = True) -> bool:
        if not(self.ui.editableCheckBox.isChecked()):
            self.logger.debug(f"Operation (deleteColumns) failed, table not editable")
            return False
        if isinstance(columns, list) and len(columns) > 0:
            tmp     = [self.model.findColumn(col) for col in columns]
            indexes = [i for i in tmp if i > -1]
        else:
            indexes = self.getSelectedColumns()
            columns = [self.model.df.columns[i] for i in indexes]
        if isinstance(indexes, list) and len(indexes) > 0:
            prompt = f"Are you sure you want to delete {len(indexes)} columns? This cannot be undone."
            ans = QMessageBox.question(self, "Confirm Deletion", prompt) if ask else QMessageBox.Yes
            if QMessageBox.Yes == ans:
                column_names = [self.model.df.columns[i] for i in indexes]
                if self.model.dropColumns(indexes):
                    for name in column_names:
                        # Remove any locally stored column information
                        if name in self.formulas.keys():
                            self.formulas.pop(name)

                    self.logOperation('deleteColumns', columns=columns, ask=False)
                    
                    self.setModel(self.model)
                    return True
        return False

    def copyColumns(self, columns : typing.List[str] = [], index : int = None) -> bool:
        if not(self.ui.editableCheckBox.isChecked()):
            self.logger.debug(f"Operation (copyColumns) failed, table not editable")
            return False

        if not(isinstance(columns, list)) or len(columns) < 1:
            selected_cols = self.getSelectedColumns()
            columns      = [self.model.df.columns[col] for col in selected_cols]
            index        = selected_cols[-1] if len(columns) > 0 else self.model.columnCount()

        if index is None:
            index = self.model.columnCount()

        if isinstance(columns, list):
            for col in columns:
                self.insertColumn(name=f"{col}_copy", column=self.model.df[col], index=index)
                index+=1
            self.logOperation('copyColumns', columns=columns, index=index)
            return True
        return False

    def insertColumn(self,
                     name   : str = "",
                     column : typing.Any = "",
                     index  : int = None) -> typing.Union[int, None]:
        """
        Insert a new column into the table.

        *Parameters:*
    
        name : str
            Column name of new column to be added

        column : typing.Any
            Value to initialize column with. Can be scalar value or pandas.Series

        index : int
            Valid column index (0 to num_columns -1) or None

        *Returns:*
    
        New column index if new column was added, or None if insertion failed
        """
        if not(self.ui.editableCheckBox.isChecked()):
            self.logger.debug(f"Operation (insertColumn) failed, table not editable")
            return None
        self.context_menu.hide()
        if not(isStringValid(name)):
            name = QInputDialog.getText(self, "Insert Column", "Enter column name", text='New Column')[0]

        if isStringValid(name):
            index = self.getInsertionIndex(index)

            # Get a list of visible columns
            visibleCols = [i for i in range(self.model.columnCount()) if not(self.ui.tableView.isColumnHidden(i))]

            # Add the column to the model
            if self.model.addColumn(name=name, column=column, index=index):

                # Adjust the indexes to account for the new column
                for i in range(len(visibleCols)):
                    if visibleCols[i] > index:
                        visibleCols[i] = visibleCols[i] + 1
                
                # Only log the operation as successful if this is a simple column insertion
                if isinstance(column, str):
                    self.logOperation('insertColumn', name=name, column=column, index=index)

                # Update the table view with the new model
                self.setModel(self.model)
                if len(visibleCols) > 0:
                    self.hideOtherColumns(visibleCols)
                    self.showColumns([index + 1])
                self.ui.tableView.scrollTo(self.model.index(0, index+1), hint=QAbstractItemView.PositionAtCenter)
                self.ui.tableView.selectColumn(index+1)
                return index+1
        return None
    
    def editCell(self, row : int, col_name : str, value : typing.Any, role : Qt.ItemDataRole) -> bool:
        if not(self.ui.editableCheckBox.isChecked()):
            self.logger.debug(f"Operation (editCell) failed, table not editable")
            return False
        column = self.model.findColumn(col_name)
        if column > -1:
            index = self.model.index(row, column)
            return self.model.setData(index, value, role)
        else:
            return False
    
    def insertNewFormula(self, name : str = "", index : int = None, formula : str = "") -> bool:
        """
        Insert a new column into the table with a custom formula.

        *Parameters:*
    
        name : str
            Column name of new column to be added

        index : int
            Valid column index (0 to num_columns -1) or None

        formula : str
            A valid string formula to pass to pandas.DataFrame.eval()

        *Returns:*
    
        True if the new column was added
        """
        if not(self.ui.editableCheckBox.isChecked()):
            self.logger.debug(f"Operation (insertNewFormula) failed, table not editable")
            return False
   
        new_column_index = self.insertColumn(name=name, index=index)
        if isIndexValid(new_column_index, self.model.columnCount()):
            src_column_index = new_column_index - 1
            if isStringValid(formula):
                return self.applyFormula(index=new_column_index, formula=formula)
            else:
                if isIndexValid(src_column_index, self.model.columnCount()):
                    # Set the formula text to the source column
                    column_name = self.model.df.columns[src_column_index]
                    self.applyFormula(index=new_column_index, formula=f"`{column_name}`")
                self.ui.formulaEdit.setFocus()
                return True
        
        return False

    def insertColumnDelta(self, src_column : int = None, index : int = None) -> bool:
        """
        Insert a new column into the table with a delta of the source column.

        *Parameters:*
    
        name : str
            Column name of new column to be added

        src_column : int
            The index of the column to apply the delta to

        index : int
            Valid column index (0 to num_columns -1) to insert column or None

        *Returns:*
    
        True if the new column was added
        """
        return self.insertPresetColumnFormula(operation_name="insertColumnDelta",
                                              column_format_str="{column}_DELTA",
                                              formula_format_str="@delta(`{column}`)",
                                              src_column=src_column,
                                              index=index)

    def insertColumnMin(self, src_column : int = None, index : int = None) -> bool:
        """
        Insert a new column into the table with the minimum of the source column.

        *Parameters:*
    
        name : str
            Name of new column to be added

        src_column : int
            The index of the column to apply the minimum to

        index : int
            Valid column index (0 to num_columns -1) to insert column or None

        *Returns:*
    
        True if the new column was added
        """
        return self.insertPresetColumnFormula(operation_name="insertColumnMin",
                                              column_format_str="{column}_MIN",
                                              formula_format_str="`{column}`.min()",
                                              src_column=src_column,
                                              index=index)

    def insertColumnMax(self, src_column : int = None, index : int = None) -> bool:
        """
        Insert a new column into the table with the maximum of the source column.

        *Parameters:*
    
        name : str
            Name of new column to be added

        src_column : int
            The index of the column to apply the maximum to

        index : int
            Valid column index (0 to num_columns -1) to insert column or None

        *Returns:*
    
        True if the new column was added
        """
        return self.insertPresetColumnFormula(operation_name="insertColumnMax",
                                              column_format_str="{column}_MAX",
                                              formula_format_str="`{column}`.max()",
                                              src_column=src_column,
                                              index=index)

    def insertColumnCumMin(self, src_column : int = None, index : int = None) -> bool:
        """
        Insert a new column into the table with the cumulative minimum of the source column.

        *Parameters:*
    
        name : str
            Name of new column to be added

        src_column : int
            The index of the column to apply the cumulative minimum to

        index : int
            Valid column index (0 to num_columns -1) to insert column or None

        *Returns:*
    
        True if the new column was added
        """
        return self.insertPresetColumnFormula(operation_name="insertColumnCumMin",
                                              column_format_str="{column}_CUMULATIVE_MIN",
                                              formula_format_str="`{column}`.cummin()",
                                              src_column=src_column,
                                              index=index)

    def insertColumnCumMax(self, src_column : int = None, index : int = None) -> bool:
        """
        Insert a new column into the table with the cumulative maximum of the source column.

        *Parameters:*
    
        name : str
            Name of new column to be added

        src_column : int
            The index of the column to apply the cumulative maximum to

        index : int
            Valid column index (0 to num_columns -1) to insert column or None

        *Returns:*
    
        True if the new column was added
        """
        return self.insertPresetColumnFormula(operation_name="insertColumnCumMax",
                                              column_format_str="{column}_CUMULATIVE_MAX",
                                              formula_format_str="`{column}`.cummax()",
                                              src_column=src_column,
                                              index=index)

    def insertColumnSum(self, src_column : int = None, index : int = None) -> bool:
        """
        Insert a new column into the table with the sum of the source column.

        *Parameters:*
    
        name : str
            Name of new column to be added

        src_column : int
            The index of the column to apply the sum to

        index : int
            Valid column index (0 to num_columns -1) to insert column or None

        *Returns:*
    
        True if the new column was added
        """
        return self.insertPresetColumnFormula(operation_name="insertColumnSum",
                                              column_format_str="{column}_SUM",
                                              formula_format_str="`{column}`.sum()",
                                              src_column=src_column,
                                              index=index)

    def insertColumnStd(self, src_column : int = None, index : int = None) -> bool:
        """
        Insert a new column into the table with the standard deviation of the source column.

        *Parameters:*
    
        name : str
            Name of new column to be added

        src_column : int
            The index of the column to apply the standard deviation to

        index : int
            Valid column index (0 to num_columns -1) to insert column or None

        *Returns:*
    
        True if the new column was added
        """
        return self.insertPresetColumnFormula(operation_name="insertColumnStd",
                                              column_format_str="{column}_STD",
                                              formula_format_str="`{column}`.std()",
                                              src_column=src_column,
                                              index=index)

    def insertColumnAvg(self, src_column : int = None, index : int = None) -> bool:
        """
        Insert a new column into the table with the mean (average) of the source column.

        *Parameters:*
    
        name : str
            Name of new column to be added

        src_column : int
            The index of the column to apply the average to

        index : int
            Valid column index (0 to num_columns -1) to insert column or None

        *Returns:*
    
        True if the new column was added
        """
        return self.insertPresetColumnFormula(operation_name="insertColumnAvg",
                                              column_format_str="{column}_MEAN",
                                              formula_format_str="`{column}`.mean()",
                                              src_column=src_column,
                                              index=index)

    def insertColumnMedian(self, src_column : int = None, index : int = None) -> bool:
        """
        Insert a new column into the table with the median of the source column.

        *Parameters:*
    
        name : str
            Name of new column to be added

        src_column : int
            The index of the column to apply the median to

        index : int
            Valid column index (0 to num_columns -1) to insert column or None

        *Returns:*
    
        True if the new column was added
        """
        return self.insertPresetColumnFormula(operation_name="insertColumnMedian",
                                              column_format_str="{column}_MEDIAN",
                                              formula_format_str="`{column}`.median()",
                                              src_column=src_column,
                                              index=index)
    
    def insertCustomFormula(self, src_column : int = None, index : int = None) -> bool:
        """
        Insert a new column into the table with the same value of the source column.

        *Parameters:*
    
        name : str
            Name of new column to be added

        src_column : int
            The index of the column to apply the median to

        index : int
            Valid column index (0 to num_columns -1) to insert column or None

        *Returns:*
    
        True if the new column was added
        """
        return self.insertPresetColumnFormula(operation_name="insertCustomFormula",
                                              column_format_str="",
                                              formula_format_str="`{column}`",
                                              src_column=src_column,
                                              index=index)

    def insertPresetColumnFormula(self,
                                  operation_name     : str,
                                  column_format_str  : str,
                                  formula_format_str : str,
                                  src_column         : int = None,
                                  index              : int = None) -> bool:
        """
        Insert a new column into the table with a delta of the source column.

        *Parameters:*
    
        operation_name : str
            Name of the operation being performed

        column_format_str : str
            Format string of new column name of new column to be added with 
            "column" as the format format parameter.

        formula_format_str : str
            Format string of formula for new column to be added with "column"
            as format parameter. See pandas.eval for syntax

        src_column : int
            The index of the column to apply the formula to

        index : int
            Valid column index (0 to num_columns -1) or None

        *Returns:*
    
        True if the new column was added
        """
        if not(self.ui.editableCheckBox.isChecked()):
            self.logger.debug(f"Operation ({operation_name}) failed, table not editable")
            return False

        # Get the column to apply the formula to
        if not(isIndexValid(src_column, self.model.columnCount())):
            columns    = self.getSelectedColumns()
            src_column = columns[-1] if len(columns) > 0 else -1

        # Create the new column
        if isIndexValid(src_column, self.model.columnCount()):
            column = self.model.df.columns[src_column]
            return self.insertNewFormula(name=column_format_str.format(column=column),
                                         index=src_column,
                                         formula=formula_format_str.format(column=column))
        else:
            self.logger.debug(f"Operation ({operation_name}) failed, Invalid Index: {index}")

        return False

    def keyPressEvent(self, e : QKeyEvent) -> None:
        if e.matches(QKeySequence.Open):
            self.load_settings_action.trigger()
        elif e.matches(QKeySequence.New):
            self.add_column_action.trigger()
        elif e.matches(QKeySequence.Save):
            self.save_settings_action.trigger()
        elif e.matches(QKeySequence.Print):
            self.plotColumns()
        elif e.matches(QKeySequence.Find):
            self.find()
        super().keyPressEvent(e)
    
    def setSelectedColumns(self, selectedColumns : typing.List[bool]):
        for i in range(len(selectedColumns)):
            if i < self.column_model.rowCount():
                index = self.column_model.index(i, 0)
                self.column_model.setData(index, Qt.Checked if selectedColumns[i] else Qt.Unchecked, Qt.CheckStateRole)

    def onCellChanged(self, index : QModelIndex, value : typing.Any, role : Qt.ItemDataRole):
        try:
            self.logOperation('editCell', row=index.row(), col_name=self.model.df.columns[index.column()], value=value, role=int(role))
        except:
            self.logger.debug(f'Failed to log operation: editCell({index}, {value}, {role})')
    
    def onListSelectionChanged(self):
        selected = self.ui.columnList.selectionModel().selectedRows()
        indexes  = [self.column_proxy.mapToSource(i).row() for i in selected]
        if len(indexes) > 0:

            # Force selection mode to allow multi-selection
            orig = self.ui.tableView.selectionMode()
            self.ui.tableView.clearSelection()
            self.ui.tableView.setSelectionMode(QAbstractItemView.MultiSelection)
            for i in indexes:
                self.ui.tableView.selectColumn(i)
            self.ui.tableView.setSelectionMode(orig)
            self.ui.tableView.scrollTo(self.model.index(0, indexes[-1]), hint=QAbstractItemView.PositionAtCenter)

    def onSelectionChanged(self):
        selected_cols = self.getSelectedColumns()
        single_column = len(selected_cols) == 1 
        any_columns   = len(selected_cols)  > 0
        editable      = self.ui.editableCheckBox.isChecked()
        self.ui.plotButton.setEnabled(any_columns)
        self.add_column_action.setVisible(editable)
        self.hide_columns_action.setVisible(any_columns)
        self.hide_others_action.setVisible(any_columns)
        self.copy_column_action.setVisible(any_columns and editable)
        self.delete_column_action.setVisible(any_columns and editable)
        self.rename_column_action.setVisible(single_column and editable)
        self.sort_action.setVisible(single_column and editable)
        self.get_statistics_action.setVisible(any_columns)
        self.apply_formula_menu.menuAction().setVisible(editable and single_column)
        self.updateFormulaEdit(editable, selected_cols)
        if single_column:
            self.ui.colorRuleColumnComboBox.setCurrentIndex(selected_cols[0])

    # Update the state of the formula line edit based on the window state
    def updateFormulaEdit(self, editable : bool, selection : typing.List[int]):
        self.ui.formulaEdit.setEnabled(False)
        if len(selection) == 1:
            if editable:
                self.ui.formulaEdit.setEnabled(True)
                self.ui.formulaEdit.setPlaceholderText("Enter a formula for the column")
                index = selection[-1]
                col   = self.model.df.columns[index]
                if col in self.formulas.keys():
                    formula = self.formulas[col]
                    if isinstance(formula, str) and len(formula) > 0:
                        self.ui.formulaEdit.setText(formula)
                        self.ui.applyButton.setEnabled(False)
                    else:
                        self.ui.formulaEdit.clear()
                else:
                    self.ui.formulaEdit.clear()
            else:
                self.ui.formulaEdit.clear()
                self.ui.formulaEdit.setPlaceholderText('Check the "editable" checkbox to enable formula editing')
        else:
            self.ui.formulaEdit.setPlaceholderText("Select a single column to enter a formula for DataFrame.eval()")
            self.ui.formulaEdit.clear()

    def setEditable(self, editable : bool = False):
        self.ui.editableCheckBox.setChecked(editable)
        self.ui.insertColumnButton.setEnabled(editable)
        self.updateFormulaEdit(editable, self.getSelectedColumns())
        if editable:
            self.ui.tableView.setEditTriggers(QAbstractItemView.DoubleClicked)
        else:
            self.ui.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
    
    def onApplyClicked(self):
        columns = self.getSelectedColumns()
        if self.applyFormula(columns[-1]):
            self.ui.applyButton.setEnabled(False)
    
    def autofitColumns(self):
        columns = self.getSelectedColumns()
        if len(columns) == 0:
            # If not columns are selected, default to all columns
            columns = [i for i in range(self.column_model.rowCount()) if self.column_model.index(i, 0).data(Qt.CheckStateRole)]

        # Set the column width for the selected columns
        if len(columns) > 0:
            for column in columns:
                column_len = self.model.columnMaxPixelLen(column)
                self.ui.tableView.horizontalHeader().resizeSection(column, column_len)
    
    def applyFormula(self, index : int = None, formula : str = "") -> bool:
        if isIndexValid(index, self.model.columnCount()):
            if not(isStringValid(formula)):
                formula = self.ui.formulaEdit.text()
            if isStringValid(formula):
                try:
                    df = self.model.df # Exposing dataframe for use in expression if needed
                    result = df.eval(formula, engine='python', local_dict=EVAL_SYMBOLS_DICT)
                except:
                    result = None
                    self.logger.error(f"The formula is not valid: \"{formula}\"")

                if not(result is None):
                    try:
                        updated = self.model.setColumn(index, result)
                    except Exception as e:
                        updated = False
                        self.logger.error(f"Unable to set column. Error: {e}")

                    if updated:
                        self.ui.formulaEdit.setText(formula)
                        self.formulas[self.model.df.columns[index]] = formula
                        self.logOperation('applyFormula', index=index, formula=formula)
                    return True
        return False
    
    def filterRows(self, query : str):
        if query != '':
            self.logger.info(f"Applying Row Filter: \"{query}\" to {self.windowTitle()}")
            try:
                new_df = self.model.df.query(query, engine='python')
                new_model = self.factory.createModel(filename=self.model.filename, df=new_df)
                new_model.setColorRules(self.model.color_rules_model)
                self.setModel(new_model, resetColumns=False)
                return True
            except:
                self.logger.error(f"The query is not valid: {query}")
                return False
    
    def reset(self):
        self.clearFilter()
        self.ui.formulaEdit.clear()
        self.ui.columnSearch.clear()
        self.ui.queryLineEdit.clear()
    
    def find(self):
        columns = self.getSelectedColumns()
        if len(columns) == 1 or self.column_model.rowCount() <= 1:
            # Search the rows in the currently selected column
            selected_column = columns[0] if len(columns) == 1 else 0
            self.row_search_dialog = SearchDialog(model=self.model,
                                                  model_column=selected_column,
                                                  search_mode=SearchDialog.RowSearchMode)
            self.row_search_dialog.searchActionRequested.connect(self.onSearchActionRequested)
            self.row_search_dialog.show()
        else:
            # Search column names in the column list
            self.column_search_dialog = SearchDialog(model=self.column_model,
                                                     model_column=0,
                                                     search_mode=SearchDialog.ColumnSearchMode)
            self.column_search_dialog.searchActionRequested.connect(self.onSearchActionRequested)
            self.column_search_dialog.show()

    def clearFilter(self):
        self.setModel(self.orig_model, resetColumns=False)
    
    def renameColumn(self, orig_name : str = None, name : str = None) -> bool:
        index = self.model.findColumn(orig_name)
        if not(isinstance(index, int)) or index < 0 or index >= self.model.columnCount():
            columns = self.getSelectedColumns()
            if len(columns) == 1:
                index     = columns[-1]
                orig_name = self.model.df.columns[index]
                name      = QInputDialog.getText(self, "Rename Column", "Enter new column name", text=f"{orig_name}_new")[0]
        if isinstance(orig_name, str) and isinstance(index, int) and self.model.columnCount() > index >= 0:
            if self.model.setHeaderData(index, Qt.Horizontal, name):
                # Rename the keys for any existing formulas
                if orig_name in self.formulas.keys():
                    formula = self.formulas.pop(orig_name)
                    self.formulas[name] = formula
                self.logOperation('renameColumn', orig_name=orig_name, name=name)
                self.setModel(self.model)
                return True
        return False
    
    def selectAllColumns(self):
        for i in range(self.column_proxy.rowCount()):
            index = self.column_proxy.index(i, 0)
            self.column_proxy.setData(index, Qt.Checked, Qt.CheckStateRole)

    def getVisibleColumns(self) -> typing.List[str]:
        columns = []
        for i in range(self.column_model.rowCount()):
            item = self.column_model.item(i, 0)
            if item.checkState() != Qt.Unchecked:
                columns.append(item.text())
        return columns

    def getSelectedColumns(self, names : bool = False) -> list:
        firstSelection = self.firstColumnView.horizontalHeader().selectionModel().selectedColumns()
        selectedCols   = firstSelection + self.ui.tableView.horizontalHeader().selectionModel().selectedColumns()
        if names:
            columns = [self.model.df.columns[index.column()] for index in selectedCols]
        else:
            columns = [index.column() for index in selectedCols]

        # Remove duplicates before returning column list
        new_list = []
        for col in columns:
            if not col in new_list:
                new_list.append(col)
        return new_list

    def showColumns(self, columns : typing.List[int] = None) -> bool:
        if not(isinstance(columns, list)) or len(columns) < 1:
            columns = self.getSelectedColumns()
        if isinstance(columns, list) and len(columns) > 0:
            for i in columns:
                index = self.column_model.index(i, 0)
                self.column_model.setData(index, Qt.Checked, Qt.CheckStateRole)
            return True
        return False
    
    def hideColumns(self, columns : typing.List[int] = None) -> bool:
        if not(isinstance(columns, list)) or len(columns) < 1:
            columns = self.getSelectedColumns()
        if isinstance(columns, list) and len(columns) > 0:
            for i in columns:
                index = self.column_model.index(i, 0)
                self.column_model.setData(index, Qt.Unchecked, Qt.CheckStateRole)
            return True
        return False

    def hideOtherColumns(self, columns : typing.List[int] = None) -> bool:
        if not(isinstance(columns, list)) or len(columns) < 1:
            columns = self.getSelectedColumns()
        if isinstance(columns, list) and len(columns) > 0:
            for i in range(self.column_model.rowCount()):
                index   = self.column_model.index(i, 0)
                checked = Qt.Checked if i in columns else Qt.Unchecked
                self.column_model.setData(index, checked, Qt.CheckStateRole)
            return True
        return False
    
    def clearAllColumns(self):
        self.ui.columnList.clearSelection()
        for i in range(self.column_proxy.rowCount()):
            index = self.column_proxy.index(i, 0)
            self.column_proxy.setData(index, Qt.Unchecked, Qt.CheckStateRole)
    
    def plotColumns(self, columns : typing.List[str] = None) -> bool:
        if not(isinstance(columns, list)) or len(columns) < 1:
            columns = self.getSelectedColumns(names=True)
        self.context_menu.hide()
        if len(columns) > 1 and self.ui.xAxisCheckBox.isChecked():
            x, y = columns[0], columns[1:]
        else:
            x, y = None, columns
        return self.createCustomPlot(x, y, options={})
    
    @pyqtSlot()
    def onCustomPlotClicked(self):
        columns = self.getSelectedColumns(names=True)
        if len(columns) > 1 and self.ui.xAxisCheckBox.isChecked():
            x, y = columns[0], columns[1:]
        else:
            x, y = None, columns
        self.custom_chart_dialog = CustomChartDialog(column_model=self.column_model, x=x, y=y)
        self.custom_chart_dialog.customChartRequested.connect(self.createCustomPlot)
        self.custom_chart_dialog.show()

    @pyqtSlot(str, list, dict)
    def createCustomPlot(self, x : str, y : typing.List[str], options : typing.Dict[str, typing.Any]):
        self.model.plotColumns(x, y, **options)

    def onIndexActivated(self, index : QModelIndex):
        if index.isValid():
            cs = index.data(Qt.CheckStateRole)
            if cs == Qt.Checked:
                self.column_proxy.setData(index, Qt.Unchecked, Qt.CheckStateRole)
            else:
                self.column_proxy.setData(index, Qt.Checked, Qt.CheckStateRole)
    
    def onDataChanged(self, topLeft : QModelIndex, bottomRight : QModelIndex):
        """
        Update the Column selection UI when the column selection changes
        """
        if topLeft.isValid() and topLeft == bottomRight:
            if self.ui.showUncheckedCheckBox.isChecked():
                self.ui.columnList.setRowHidden(topLeft.row(), False)
            else:
                self.ui.columnList.setRowHidden(topLeft.row(), bool(topLeft.data(Qt.CheckStateRole) == Qt.Unchecked))
    
    def onShowUncheckedChanged(self, checkState : Qt.CheckStateRole):
        """
        Update the Column selection UI when the show unchecked checkbox changes
        """
        self.ui.columnList.selectionModel().clearSelection()
        for i in range(self.column_proxy.rowCount()):
            if checkState == Qt.Unchecked:
                index = self.column_proxy.index(i, 0)
                self.ui.columnList.setRowHidden(i, index.data(Qt.CheckStateRole) == Qt.Unchecked)
            else:
                self.ui.columnList.setRowHidden(i, False)
    
    def onContextMenuRequested(self, pos : QPoint):
        
        # Ensure that the selection is up to date before the
        # context menu pops up
        self.onSelectionChanged()

        widget = self.sender()
        if not(widget in [self.ui.tableView, self.ui.tableView.horizontalHeader()]):
            widget = self.ui.tableView
        self.context_menu.popup(widget.mapToGlobal(pos))

    def onItemChanged(self, item : QStandardItem):
        i = item.row()
        if i == 0:
            if self.ui.freezeColCheckBox.isChecked():
                item.setData(Qt.Checked, Qt.CheckStateRole)
            else:
                self.ui.tableView.setColumnHidden(i, item.checkState() == Qt.Unchecked)
        elif i < self.model.columnCount():
            self.ui.tableView.setColumnHidden(i, item.checkState() == Qt.Unchecked)
    
    def onFormulaChanged(self, text : str):
        if isinstance(text, str) and len(text) > 0:
            self.ui.applyButton.setEnabled(True)
        else:
            self.ui.applyButton.setEnabled(False)
    
    # Attempt to execute a requested action from a search dialog
    @pyqtSlot(str, dict)
    def onSearchActionRequested(self, name : str, kwargs : dict):
        if hasattr(self, name):
            func = getattr(self, name)
            if callable(func):
                func(**kwargs)

    # Handle a user request for formula help
    @pyqtSlot()
    def onFormulaHelpPressed(self):
        query_url = QUrl("https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.eval.html")
        QDesktopServices.openUrl(query_url)

    # Handle when the query text is updated
    @pyqtSlot(str)
    def onQueryTextChanged(self, text : str):
        self.ui.addQueryButton.setEnabled(bool(len(text) > 0))

    # Handle a user request for query help
    @pyqtSlot()
    def onAddQueryButtonPressed(self):
        query_text = self.ui.queryLineEdit.text()
        if not(self.query_model.findItems(query_text)):
            item = QStandardItem(query_text)
            item.setFlags(Qt.ItemIsUserCheckable | item.flags())
            item.setCheckState(Qt.Checked)
            self.query_model.appendRow(item)
            if self.filterRows(query_text):
                self.ui.queryLineEdit.clear()
                # Temporarily disable queries to prevent infinite recursion when setting item data
                self.queries_enabled = False
                item.setData(None, Qt.DecorationRole)
                self.queries_enabled = True
            else:
                # Update failed filter rows with an "x" to indicate they didn't work
                item.setData(Qt.Unchecked, Qt.CheckStateRole)
                item.setData(self.x_icon, Qt.DecorationRole)

    # Re-Apply all available queries to the model
    @pyqtSlot()
    def applyAllQueries(self):
        if self.queries_enabled:
            self.reset()
            for row in range(self.query_model.rowCount()):
                item = self.query_model.item(row)
                if isinstance(item, QStandardItem) and item.checkState() == Qt.Checked:
                    query_text = item.data(Qt.DisplayRole)
                    if self.filterRows(query_text):
                        # Temporarily disable queries to prevent infinite recursion when setting item data
                        self.queries_enabled = False
                        item.setData(None, Qt.DecorationRole)
                        self.queries_enabled = True
                    else:
                        # Update failed filter rows with an "x" to indicate they didn't work
                        item.setData(Qt.Unchecked, Qt.CheckStateRole)
                        item.setData(self.x_icon, Qt.DecorationRole)

    @pyqtSlot()
    def onEditQueriesButtonPressed(self):
        self.queryEditor = QueryListEditor(self.query_model, completer=self.column_completer)
        self.queryEditor.show()

    # Handle a user request for query help
    @pyqtSlot()
    def onQueryHelpPressed(self):
        query_url = QUrl("https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html")
        QDesktopServices.openUrl(query_url)

    # Add a color rule from the main color rule interface
    @pyqtSlot(str)
    def onColorRuleTextChanged(self, text : str):
        self.ui.addColorRuleButton.setEnabled("x" in text)

    # Add a color rule from the main color rule interface
    @pyqtSlot()
    def onAddColorRulePressed(self):
        column    = self.ui.colorRuleColumnComboBox.currentText()
        color     = QColor(self.ui.colorComboBox.currentText())
        condition = self.ui.colorRuleLineEdit.text()
        rule      = ColorRule(condition=condition, color=color, enabled=True)
        self.model.addColorRule(column, rule)
        self.ui.colorRuleLineEdit.clear()

    # Handle a user request for Color Rules help
    @pyqtSlot()
    def onColorRulesHelpPressed(self):
        QMessageBox.information(self, "Color Rules Help", ColorRulesModel.CONDITION_TOOLTIP)

    # Handle when the plot all button is clicked
    @pyqtSlot()
    def onPlotAllPressed(self):
        for i in range(self.saved_plots_model.rowCount()):
            index = self.saved_plots_model.index(i, 0, QModelIndex())
            info  = self.saved_plots_model.data(index, Qt.UserRole)
            if isinstance(info, PlotInfo) and info.isValid(df=self.model.df):
                self.createCustomPlot(info.x, info.y, info.options)

    # Handle when color rules are updated inside the table widget
    @pyqtSlot()
    def onColorRulesChanged(self):
        # Make sure the latest color rules model is in use
        self.ui.colorRulesTableView.setModel(self.model.color_rules_model)

        # Scroll slightly so the ui is forced to update
        self.ui.tableView.scrollContentsBy(0, 10)
        self.ui.tableView.scrollContentsBy(0, -10)

    # Handle when Saved Plots are activated
    @pyqtSlot(QModelIndex)
    def onSavedPlotsTableIndexActivated(self, index : QModelIndex):
        if isinstance(index, QModelIndex) and index.isValid():
            info = index.data(Qt.UserRole)
            if isinstance(info, PlotInfo) and info.isValid(df=self.model.df):
                self.model.plotColumns(info.x, info.y, **info.options)

    # Handle when Saved Plots are activated
    @pyqtSlot()
    def onSavedPlotsChanged(self):
        self.ui.plotAllButton.setEnabled(self.saved_plots_model.rowCount() > 0)

    @pyqtSlot()
    def onEditSavedPlotsButtonPressed(self):
        self.savedPlotsEditor = SavedPlotsEditor(self.saved_plots_model, self.column_model)
        ans = self.savedPlotsEditor.exec()
        if ans == QDialog.Accepted:
            self.onSavedPlotsChanged()

    @pyqtSlot(PlotInfo)
    def onPlotCreated(self, info : PlotInfo) -> bool:
        if info.isValid(df=self.model.df) and not info in self.saved_plots_model:
            self.saved_plots_model.append(info)
            self.onSavedPlotsChanged()
            return True
        return False

    def setModel(self, model : DataFrameModel, resetColumns : bool = True):
        self.model = model
        if not(model is None):
            self.ui.tableView.setModel(model)
            self.firstColumnView.setModel(model)
            self.ui.tableView.scrollToTop()
            self.ui.tableView.horizontalHeader().selectionModel().selectionChanged.connect(self.onSelectionChanged)
            self.ui.numRowsLineEdit.setText(str(self.model.rowCount()))
            self.ui.numColsLineEdit.setText(str(self.model.columnCount()))
            if isinstance(model, DataFrameModel):
                model.plotCreated.connect(self.onPlotCreated)
                self.model.cellChanged.connect(self.onCellChanged)
                if resetColumns:
                    self.column_model.clear()
                    self.ui.colorRuleColumnComboBox.clear()
                    for col in model.df.columns:
                        item = QStandardItem(col)
                        item.setCheckState(Qt.Checked)
                        self.column_model.appendRow(item)
                        self.ui.colorRuleColumnComboBox.addItem(col)
                    self.ui.tableView.setColumnHidden(0, False)
                    self.firstColumnView.setColumnHidden(0, False)
                    for i in range(1, self.model.columnCount()):
                        self.ui.tableView.setColumnHidden(i, False)
                        self.firstColumnView.setColumnHidden(i, True)
                    completer_strings = ["`%s`" % s for s in model.df.columns]
                    self.column_completer = ColumnCompleter(completer_strings, self)
                    self.column_completer.setCaseSensitivity(Qt.CaseInsensitive)
                    self.column_completer.setFilterMode(Qt.MatchContains)
                    self.completer_delegate = LineEditDelegate(self.column_completer, self)
                    self.ui.queryListView.setItemDelegate(self.completer_delegate)
                    self.ui.formulaEdit.setCompleter(self.column_completer)
                    self.ui.queryLineEdit.setCompleter(self.column_completer)
                    self.color_rule_delegate = ColorRuleEditorDelegate(self.model, self)
                    self.ui.colorRulesTableView.setModel(self.model.color_rules_model)
                    self.ui.colorRulesTableView.setItemDelegate(self.color_rule_delegate)
                    self.ui.colorRulesTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                    self.model.colorRulesChanged.connect(self.onColorRulesChanged)
                    self.model.color_rules_model.colorRulesChanged.connect(self.onColorRulesChanged)

# Convenience method to create a table viewer
def create_table(file_or_model : typing.Union[str, DataFrameModel], **kwargs):
    logger = logging.getLogger(__name__)
    if isinstance(file_or_model, DataFrameModel):
        filename = file_or_model.filename
        view     = TableViewer(file_or_model)
    elif isinstance(file_or_model, str):
        factory  = DataFrameFactory.getInstance()
        model    = factory.createModel(filename=file_or_model, **kwargs)
        view     = TableViewer(model)
    elif isinstance(file_or_model, pandas.DataFrame):
        factory  = DataFrameFactory.getInstance()
        model    = factory.createModel(filename="", df=file_or_model, **kwargs)
        filename = model.filename
        view     = TableViewer(model)
    else:
        logger.error(f"Unable to create Table from type: {file_or_model}")
        view     = TableViewer(DataFrameModel(pandas.DataFrame()))
        filename = ""

    view.setToolTip(filename)
    view.setWindowTitle(os.path.basename(filename))
    logger.info(f"Created Table {view.windowTitle()}")
    return view

if __name__ == "__main__":

    # Test the stand-alone table viewer
    app = QApplication(sys.argv)

    if len(sys.argv) > 1:
        view = create_table(sys.argv[1])
    else:
        x     = numpy.arange(-numpy.pi * 2 , numpy.pi * 2, numpy.pi / 16)
        df    = pandas.DataFrame({"X" : x, "Sin(x)" : numpy.sin(x), "Cos(x)" : numpy.cos(x)})
        view  = create_table(df)
    view.show()

    app.exec()