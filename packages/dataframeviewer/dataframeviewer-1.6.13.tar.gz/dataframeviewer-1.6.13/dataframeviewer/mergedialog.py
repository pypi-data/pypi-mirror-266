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
# Class to encapsulate a QDialog used for merging two pandas DataFrames
#

import os
import sys
import typing
import logging

import pandas

from PyQt5.QtCore    import Qt, QFileInfo, QUrl, pyqtSignal, pyqtSlot
from PyQt5.QtGui     import QDesktopServices
from PyQt5.QtWidgets import QWidget, QDialog

# Update PYTHONPATH
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from ui.ui_mergedialog import Ui_MergeDialog
from dataframemodel    import DataFrameFactory

class MergeDialog(QDialog):

    # Emit a signal to request a merge operation
    mergeTablesRequested = pyqtSignal(str)
    operationRequested   = pyqtSignal(str, str, dict)

    def __init__(self, 
                 parent  : typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.ui          : Ui_MergeDialog   = Ui_MergeDialog()
        self.factory     : DataFrameFactory = DataFrameFactory.getInstance()
        self.logger      : logging.Logger   = logging.getLogger(__name__)
        self.initUi()

        # Connect this objects' signals to factory methods
        self.operationRequested.connect(self.factory.performMergeOperation)

    # Initialize the widget's user interface
    def initUi(self):
        self.ui.setupUi(self)

        # Initialize the left and right table combo boxes
        model_file_paths = list(self.factory.models.keys())
        if len(model_file_paths) > 1:
            i = 0
            for i in range(len(model_file_paths)):
                name      = QFileInfo(model_file_paths[i]).fileName()
                file_path = model_file_paths[i]

                self.ui.leftTableComboBox.addItem(name)
                self.ui.leftTableComboBox.setItemData(i, file_path, Qt.ToolTipRole)
                self.ui.leftTableComboBox.setItemData(i, file_path, Qt.UserRole)

                self.ui.rightTableComboBox.addItem(name)
                self.ui.rightTableComboBox.setItemData(i, file_path, Qt.ToolTipRole)
                self.ui.rightTableComboBox.setItemData(i, file_path, Qt.UserRole)
            # Initialize the combo boxes with the first and last tables
            self.ui.leftTableComboBox.setCurrentIndex(0)
            self.ui.rightTableComboBox.setCurrentIndex(self.ui.rightTableComboBox.count()-1)

        # Connect signals / slots
        self.ui.leftTableComboBox.currentIndexChanged.connect(self.onTableSelectionChanged)
        self.ui.rightTableComboBox.currentIndexChanged.connect(self.onTableSelectionChanged)
        self.ui.titleLineEdit.textChanged.connect(self.updateUI)
        self.ui.leftOnComboBox.currentIndexChanged.connect(self.updateUI)
        self.ui.rightOnComboBox.currentIndexChanged.connect(self.updateUI)
        self.ui.leftSuffixLineEdit.textChanged.connect(self.updateUI)
        self.ui.rightSuffixLineEdit.textChanged.connect(self.updateUI)
        self.ui.concatenateButtonGroup.buttonToggled.connect(self.updateUI)
        self.ui.operationButtonGroup.buttonToggled.connect(self.updateUI)
        self.ui.okButton.clicked.connect(self.accept)
        self.ui.cancelButton.clicked.connect(self.reject)
        self.ui.helpButton.clicked.connect(self.showHelp)

        # Ensure the UI is updated based on the current state
        self.updateUI(update_combo_boxes=True, reset_title=True)

    def __get_dataframes(self, update_combo_boxes : bool = False, reset_title : bool = False) -> typing.Tuple[str, str, pandas.DataFrame, pandas.DataFrame]:
        """
        Return the filepaths and dataframes corresponding to the current left and right table
        selection in the UI
        """

        # Get the current left and right files
        left_filename  = self.ui.leftTableComboBox.currentData(Qt.UserRole)
        right_filename = self.ui.rightTableComboBox.currentData(Qt.UserRole)

        if left_filename in self.factory.models.keys() and right_filename in self.factory.models.keys():

            # Get the left and right models
            left_model = self.factory.models[left_filename]
            right_model = self.factory.models[right_filename]

            if reset_title:
                left_basename  = QFileInfo(left_filename).baseName()
                right_basename = QFileInfo(right_filename).baseName()

                self.ui.titleLineEdit.setText(f"{left_basename}+{right_basename}")
                self.ui.leftSuffixLineEdit.setText(f"_{left_basename}")
                self.ui.rightSuffixLineEdit.setText(f"_{right_basename}")

            # Populate the left_on and right_on combo boxes
            if update_combo_boxes:
                self.ui.leftOnComboBox.clear()
                self.ui.leftOnComboBox.addItems(left_model.df.columns)
                self.ui.leftOnComboBox.setCurrentIndex(0)
                self.ui.rightOnComboBox.clear()
                self.ui.rightOnComboBox.addItems(right_model.df.columns)
                self.ui.rightOnComboBox.setCurrentIndex(0)

            return left_filename, right_filename, left_model.df, right_model.df
        
        return None, None, None, None
        
    @pyqtSlot()
    def onTableSelectionChanged(self) -> None:
        self.updateUI(update_combo_boxes=True, reset_title=True)

    @pyqtSlot()
    def updateUI(self, update_combo_boxes : bool = False, reset_title : bool = False) -> None:
        """
        Check for errors with the user inputs and update the UI accordingly
        """

        # Update the UI based on the current selection
        concat_mode  = self.ui.concatenateRadioButton.isChecked()
        ordered_mode = self.ui.mergeOrderedRadioButton.isChecked()
        merge_mode   = self.ui.mergeRadioButton.isChecked() or ordered_mode
        self.ui.leftOnComboBox.setEnabled(merge_mode)
        self.ui.leftSuffixLineEdit.setEnabled(merge_mode)
        self.ui.rightOnComboBox.setEnabled(merge_mode)
        self.ui.rightSuffixLineEdit.setEnabled(merge_mode)
        self.ui.howComboBox.setEnabled(merge_mode)
        self.ui.forwardFillCheckBox.setEnabled(ordered_mode)
        self.ui.concatRowsRadioButton.setEnabled(concat_mode)
        self.ui.concatColumnsRadioButton.setEnabled(concat_mode)

        # Retrieve the left and right dataframes from the current selection
        left_filename, right_filename, left_df, right_df = self.__get_dataframes(update_combo_boxes, reset_title)

        # Get the left_on  and right_on column names
        left_on  = self.ui.leftOnComboBox.currentText()
        right_on = self.ui.rightOnComboBox.currentText()

        # Check for all possible errors
        if self.ui.leftTableComboBox.count() < 2 or self.ui.rightTableComboBox.count() < 2:
            error_string = "At least 2 tables are required for merging"
        elif self.ui.leftTableComboBox.currentIndex() == self.ui.rightTableComboBox.currentIndex():
            error_string = "Select a different left and right table to proceed"
        elif len(self.ui.titleLineEdit.text()) < 1:
            error_string = "Enter a title for the new table"
        elif len(self.ui.leftSuffixLineEdit.text()) < 1:
            error_string = "Enter a suffix for the left table"
        elif len(self.ui.rightSuffixLineEdit.text()) < 1:
            error_string = "Enter a suffix for the right table"
        elif left_filename not in self.factory.models.keys():
            error_string = f"Left table is not valid: ({left_filename})"
        elif right_filename not in self.factory.models.keys():
            error_string = f"Right table is not valid ({right_filename})"
        elif not(isinstance(left_df, pandas.DataFrame)) or len(left_df.columns) < 1:
            error_string = f"Left table has no valid columns: ({right_filename})"
        elif not(isinstance(right_df, pandas.DataFrame)) or len(right_df.columns) < 1:
            error_string = f"Right table has no valid columns: ({right_filename})"
        elif left_on not in left_df.columns:
            error_string = f"Left on column selection not in left table: ({left_filename})"
        elif right_on not in right_df.columns:
            error_string = f"Right on column selection not in right table: ({right_filename})"
        elif left_df[left_on].dtype != right_df[right_on].dtype:
            error_string = f"left_on dtype ({left_df[left_on].dtype}) != right_on dtype: ({right_df[right_on].dtype})"
        else:
            # Form is valid, indicate no errors
            error_string = ""
        
        # Update the UI based on the error status
        if len(error_string) > 0:
            error_template = '<p><span style=" font-weight:600; color:#ff0000;">{text}</span></p>'
            self.ui.okButton.setText("OK*")
            self.ui.statusLabel.setText(error_template.format(text=error_string))
            self.ui.statusLabel.show()
            self.ui.okButton.setEnabled(False)
        else: 
            # No Errors detected, Enable the OK button
            self.ui.okButton.setText("OK")
            self.ui.statusLabel.hide()
            self.ui.okButton.setEnabled(True)
    
    @pyqtSlot()
    def showHelp(self):
        if self.ui.mergeRadioButton.isChecked():
            help_url = QUrl("https://pandas.pydata.org/docs/reference/api/pandas.merge.html")
        elif self.ui.concatenateRadioButton.isChecked():
            help_url = QUrl("https://pandas.pydata.org/docs/reference/api/pandas.concat.html")
        else:
            help_url = QUrl("https://pandas.pydata.org/docs/reference/api/pandas.merge_ordered.html")
        QDesktopServices.openUrl(help_url)

    @pyqtSlot()
    def accept(self) -> None:
        # Retrieve the left and right dataframes from the current selection
        left_name, right_name, left_df, right_df = self.__get_dataframes(update_combo_boxes=False)

        # Setup the operation and keyword arguments
        if self.ui.concatenateRadioButton.isChecked():
            operation = "concat"
            kwargs    = {
                "objs"  : (left_df, right_df),
                "axis"  : 0 if self.ui.concatRowsRadioButton.isChecked() else 1
            }
        elif self.ui.mergeRadioButton.isChecked():
            operation = "merge"
            kwargs    = {
                "left"        : left_df,
                "right"       : right_df,
                "left_on"     : self.ui.leftOnComboBox.currentText(),
                "right_on"    : self.ui.rightOnComboBox.currentText(),
                "suffixes"    : (self.ui.leftSuffixLineEdit.text(), self.ui.rightSuffixLineEdit.text()),
                "how"         : self.ui.howComboBox.currentText()
            }
        else:
            operation = "merge_ordered"
            kwargs    = {
                "left"        : left_df,
                "right"       : right_df,
                "left_on"     : self.ui.leftOnComboBox.currentText(),
                "right_on"    : self.ui.rightOnComboBox.currentText(),
                "fill_method" : "ffill" if self.ui.forwardFillCheckBox.isChecked() else None,
                "suffixes"    : (self.ui.leftSuffixLineEdit.text(), self.ui.rightSuffixLineEdit.text()),
                "how"         : self.ui.howComboBox.currentText()
            }
        
        # Notify listeners of the requested operation
        if isinstance(left_df, pandas.DataFrame) and isinstance(right_df, pandas.DataFrame):
            self.mergeTablesRequested.emit(self.ui.titleLineEdit.text())
            self.operationRequested.emit(self.ui.titleLineEdit.text(), operation, kwargs)
        else:
            self.logger.error(f"Unable to merge tables {left_name}, {right_name}")
            self.logger.debug(f"Merge operation {operation}, kwargs {kwargs}")

        return super().accept()