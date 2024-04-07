#!/usr/bin/env python

# MIT License

# Copyright (c) 2023 Rafael Arvelo

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

from PyQt5.QtCore    import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QDialog

# Update PYTHONPATH
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from ui.ui_axisrangedialog import Ui_AxisRangeDialog

class AxisRangeDialog(QDialog):

    axisSettingsChanged = pyqtSignal(str, dict)

    def __init__(self, 
                 name     : str,
                 settings : typing.Dict[str, typing.Any] = None,
                 parent   : typing.Optional[QWidget]     = None) -> None:
        super().__init__(parent)
        self.ui   : Ui_AxisRangeDialog = Ui_AxisRangeDialog()
        self.name : str                = name
        self.settings = settings if isinstance(settings, dict) else {}
        self.initUi(settings)

    # Initialize the widget's user interface
    def initUi(self, settings : typing.Dict[str, typing.Any]):
        self.ui.setupUi(self)

        self.setWindowTitle(self.windowTitle().replace("%s", self.name))

        if settings.get("type", "Automatic") == "Custom":
            self.ui.customButton.setChecked(True)
        else:
            self.ui.automaticButton.setChecked(True)

        self.ui.minSpinBox.setValue(settings.get("min", self.ui.minSpinBox.value()))
        self.ui.maxSpinBox.setValue(settings.get("max", self.ui.maxSpinBox.value()))
   
    @pyqtSlot()
    def accept(self) -> None:
        
        # Update settings from user interface
        self.settings["type"] = "Custom" if self.ui.customButton.isChecked() else "Automatic"
        self.settings["min"]  = self.ui.minSpinBox.value()
        self.settings["max"]  = self.ui.maxSpinBox.value()

        # Signal that the axis settings have changed
        self.axisSettingsChanged.emit(self.name, self.settings)

        return super().accept()