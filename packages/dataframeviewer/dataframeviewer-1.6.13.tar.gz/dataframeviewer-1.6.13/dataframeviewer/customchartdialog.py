#!/usr/bin/env python

# MIT License

# Copyright (c) 2022 Rafael Arvelo

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
# Class to encapsulate a QDialog used for creating a custom chart
#

import os
import sys
import typing
import logging
from   collections.abc import Iterable
from   functools       import update_wrapper

from PyQt5.QtCore    import Qt, QAbstractItemModel, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QDialog, QListWidget

# Update PYTHONPATH
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from ui.ui_customchartdialog import Ui_CustomChartDialog
from searchdialog            import SearchDialog
from axisrangedialog         import AxisRangeDialog

class CustomChartDialog(QDialog):

    # Emit a signal to request a new custom chart be created
    customChartRequested = pyqtSignal(str, list, dict)

    def __init__(self, 
                 column_model  : QAbstractItemModel,
                 x             : typing.Optional[str]                          = None,
                 y             : typing.Optional[typing.List[str]]             = None,
                 options       : typing.Optional[typing.Dict[str, typing.Any]] = None,
                 axis_settings : typing.Optional[typing.Dict[str, typing.Any]] = None,
                 parent        : typing.Optional[QWidget]                      = None) -> None:
        super().__init__(parent)
        self.ui                 : Ui_CustomChartDialog = Ui_CustomChartDialog()
        self.column_model       : QAbstractItemModel   = column_model
        self.x             = x
        self.y             = y
        self.options       = options       if isinstance(options      , dict) else {}
        self.axis_settings = axis_settings if isinstance(axis_settings, dict) else {}
        self.logger        = logging.getLogger(__name__)
        
        # Set default settings
        default_axis_settings = { "type" : "Automatic", "min" : 0.0, "max" : 0.0 }
        self.options.setdefault("subplots"      , True)
        self.options.setdefault("secondary_y"   , False)
        self.axis_settings.setdefault("X-Axis"  , default_axis_settings.copy())
        self.axis_settings.setdefault("Y-Axis"  , default_axis_settings.copy())
        self.axis_settings.setdefault("Y-Axis 2", default_axis_settings.copy())

        self.initUi()
    
    def showAxisRangeDialog(self, name):
        self.axisRangeDialog = AxisRangeDialog(name, self.axis_settings.get(name, {}))
        self.axisRangeDialog.axisSettingsChanged.connect(self.onAxisSettingsChanged)
        self.axisRangeDialog.exec()

    @pyqtSlot()
    def showXAxisRangeDialog(self):
        self.showAxisRangeDialog("X-Axis")

    @pyqtSlot()
    def showYAxisRangeDialog(self):
        self.showAxisRangeDialog("Y-Axis")

    @pyqtSlot()
    def showYAxis2RangeDialog(self):
        self.showAxisRangeDialog("Y-Axis 2")
    
    @pyqtSlot(str, dict)
    def onAxisSettingsChanged(self, axis_name : str, settings : typing.Dict[str, typing.Any]):
        if axis_name in ["X-Axis", "Y-Axis", "Y-Axis 2"]:
            self.axis_settings[axis_name] = settings
        else:
            self.logger.warning("Unknown axis name: %s", axis_name)

    # Initialize the widget's user interface
    def initUi(self): 
        self.ui.setupUi(self)

        # Keep track of the current widget
        self.currentListWidget = self.ui.yColumnsListWidget

        # Hide the unused columns
        self.ui.yColumnsLabel_2.hide()
        self.ui.editYAxisButton_2.hide()
        self.ui.yColumnsListWidget_2.hide()
        
        # Initialize the x column combo box
        for i in range(self.column_model.rowCount()):
            index = self.column_model.index(i, 0)
            if self.column_model.data(index, Qt.CheckStateRole) != Qt.Unchecked:
                self.ui.xColumnComboBox.addItem(self.column_model.data(index, Qt.DisplayRole))

        # Initialize the x column selection
        x_index = -1
        if isinstance(self.x, str):
            for i in range(self.ui.xColumnComboBox.count()):
                index = self.column_model.index(i, 0)
                if self.ui.xColumnComboBox.itemText(i) == self.x:
                    x_index = i
                    break
        self.ui.xColumnComboBox.setCurrentIndex(x_index)

        # Initialize the y column selection
        y2 = self.options.get("secondary_y", [])
        if isinstance(y2, list) and len(y2) > 0:
            y = [i for i in self.y if i not in y2]
            self.selectYColumns(y, listWidget=self.ui.yColumnsListWidget)
            self.selectYColumns(y2, listWidget=self.ui.yColumnsListWidget_2)
        else:
            self.selectYColumns(self.y)

        # Initialize the rest of the UI from the plot options
        if isinstance(self.options, dict):
            self.ui.legendCheckBox.setChecked(self.options.get("legend", self.ui.legendCheckBox.isChecked()) == True)

            if self.options.get("subplots", self.ui.subPlotsButton.isChecked()):
                self.ui.subPlotsButton.setChecked(True)
            elif self.options.get("secondary_y", False):
                self.ui.twoYAxesButton.setChecked(True)
            else:
                self.ui.oneYAxisButton.setChecked(True)
            
            kind = self.options.get("kind", self.ui.typeComboBox.currentText())
            if isinstance(kind, str):
                index = self.ui.typeComboBox.findText(kind)
                if index >= 0 and index < self.ui.typeComboBox.count():
                    self.ui.typeComboBox.setCurrentIndex(index)

            title = self.options.get("title")
            if isinstance(title, str):
                self.ui.titleLineEdit.setText(title)
        
        # Open the corresponding column select dialog when the y columns list widget is clicked. 
        self.ui.yColumnsListWidget.mouseDoubleClickEvent   = self.wrapDoubleClickEvent(self.ui.yColumnsListWidget)
        self.ui.yColumnsListWidget_2.mouseDoubleClickEvent = self.wrapDoubleClickEvent(self.ui.yColumnsListWidget_2)

        # Connect UI signals
        self.ui.editXAxisButton.clicked.connect(self.showXAxisRangeDialog)
        self.ui.editYAxisButton.clicked.connect(self.showYAxisRangeDialog)
        self.ui.editYAxisButton_2.clicked.connect(self.showYAxis2RangeDialog)
        self.ui.typeComboBox.currentTextChanged.connect(self.onChartTypeChanged)
    
    # Function to wrap the "mouseDoubleClickEvent" of a widget
    # The double click event must be wrapped to handle a double click when the
    # list widget is empty
    def wrapDoubleClickEvent(self, listWidget : QListWidget):
        orig_event = listWidget.mouseDoubleClickEvent
        def wrappedDoubleClickEvent(*args, **kwargs):
            self.showColumnSearchDialog(listWidget)
            orig_event(*args, **kwargs)
        update_wrapper(wrappedDoubleClickEvent, listWidget.mouseDoubleClickEvent)
        return wrappedDoubleClickEvent
    
    @pyqtSlot()
    def accept(self) -> None:
        # Collect the custom chart settings from the UI
        if self.ui.xColumnComboBox.currentIndex() >= 0:
            x = self.ui.xColumnComboBox.currentText()
        else:
            x = None
        
        y  = []
        y2 = []
        for i in range(self.ui.yColumnsListWidget.count()):
            y.append(self.ui.yColumnsListWidget.item(i).text())
        for i in range(self.ui.yColumnsListWidget_2.count()):
            y2.append(self.ui.yColumnsListWidget_2.item(i).text())
        
        options = {}
        if len(self.ui.titleLineEdit.text()) > 0:
            options["title"] = self.ui.titleLineEdit.text()
        options["kind"]        = self.ui.typeComboBox.currentText()
        options["subplots"]    = self.ui.subPlotsButton.isChecked()
        options["legend"]      = self.ui.legendCheckBox.isChecked()

        x_axis_settings = self.axis_settings.get("X-Axis", {})
        if x_axis_settings.get("type", "") == "Custom":
            options["xlim"] = (x_axis_settings.get("min", 0.0), x_axis_settings.get("max", 0.0))
        
        y_axis_settings = self.axis_settings.get("Y-Axis", {})
        if y_axis_settings.get("type", "") == "Custom":
            options["ylim"] = (y_axis_settings.get("min", 0.0), y_axis_settings.get("max", 0.0))

        y_axis_settings_2 = self.axis_settings.get("Y-Axis 2", {})
        if y_axis_settings_2.get("type", "") == "Custom":
            options["ylim2"] = (y_axis_settings_2.get("min", 0.0), y_axis_settings_2.get("max", 0.0))

        if len(y2) > 0:
            options["secondary_y"] = y2

        # Emit a signal requesting the custom chart
        if len(y) > 0:
            self.customChartRequested.emit(x, y + y2, options)
        else:
            self.logger.warning("Error: One or more Y Columns is required to creart a chart")

        # Update the local copies of the chart properties for when
        # this class is used as a modal dialog
        self.x       = x
        self.y       = y + y2
        self.options = options

        return super().accept()
    
    @pyqtSlot(QListWidget)
    def showColumnSearchDialog(self, listWidget : QListWidget):
        # Search available column names
        self.currentListWidget = listWidget
        current_y_columns = [listWidget.item(i).text() for i in range(listWidget.count())]
        self.column_search_dialog = SearchDialog(model=self.column_model,
                                                 model_column=0,
                                                 search_mode=SearchDialog.ChartYAxisSearchMode,
                                                 selected=current_y_columns)
        self.column_search_dialog.searchActionRequested.connect(self.onSearchActionRequested)
        self.column_search_dialog.exec()
        
        # Return to the original y columns list widget
        self.currentListWidget = self.ui.yColumnsListWidget_2

    # Attempt to execute a requested action from a search dialog
    @pyqtSlot(str, dict)
    def onSearchActionRequested(self, name : str, kwargs : dict):
        if hasattr(self, name):
            func = getattr(self, name)
            if callable(func):
                func(**kwargs)

    # Handle whent the chart type changes
    @pyqtSlot(str)
    def onChartTypeChanged(self, type : str):
        visible = self.ui.twoYAxesButton.isChecked() and bool(type in ['line', 'bar', 'barh'])
        self.ui.yColumnsLabel_2.setVisible(visible)
        self.ui.editYAxisButton_2.setVisible(visible)
        self.ui.yColumnsListWidget_2.setVisible(visible)

    # Add one or more y columns to the y column table
    def selectYColumns(self, columns : typing.List[str], listWidget : QListWidget = None):
        if not(isinstance(listWidget, QListWidget)):
            listWidget = self.currentListWidget
        listWidget.clear()
        while listWidget.count() > 0:
            listWidget.takeItem(0)
        if isinstance(columns, Iterable):
            listWidget.addItems(columns)