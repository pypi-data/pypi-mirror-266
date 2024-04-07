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
# This file contains the top level classes for the Data Viewer application
#
# pylint: disable-all

import os
import sys
import re

# Application paths
DATAVIEWER_BASE_PATH = os.path.dirname(os.path.realpath(__file__))

# Update PYTHONPATH
sys.path.append(DATAVIEWER_BASE_PATH)

from   PyQt5.QtWidgets   import QWidget, QMenu, QDockWidget
from   PyQt5.QtGui       import QCloseEvent, QIcon
from   PyQt5.QtCore      import Qt, pyqtSignal, pyqtSlot, QPoint, qsrand, qrand, QDateTime

class ViewerWindow(QDockWidget):
    aboutToClose        = pyqtSignal(QDockWidget)
    requestArea         = pyqtSignal(QDockWidget, Qt.DockWidgetArea)
    requestCloseOthers  = pyqtSignal(QDockWidget)
    requestCloseAll     = pyqtSignal()

    def __init__(self, 
                 title      : str,
                 widget     : QWidget,
                 parent     : QWidget = None):
        super().__init__(title, parent)
        self.initialize(title, widget)

    def initialize(self, title : str, widget : QWidget) -> None:
        # Create members
        self.contextMenu = QMenu(f"Menu: {title}", self)

        # Set Dock Widget attributes
        self.setWindowTitle(title)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setFeatures(self.AllDockWidgetFeatures)
        self.setAcceptDrops(True)
        self.setWidget(widget)

        qsrand(QDateTime.currentDateTime().toMSecsSinceEpoch() % 4294967295)
        self.window_id = qrand()
        self.setObjectName(re.sub("[\s\./]", "_", f"{title}_{self.window_id}"))


        # Add context menu actions
        self.closeMenu = self.contextMenu.addMenu("Close Window(s)")
        self.closeMenu.addAction(QIcon(":/x-logo.png"), "Close This Window", self.close)
        self.closeMenu.addAction(QIcon(":/x-logo.png"), "Close Other Windows", self.closeOthers)
        self.closeMenu.addAction(QIcon(":/x-logo.png"), "Close All Windows", self.requestCloseAll)
        
        self.moveMenu = self.contextMenu.addMenu("Move Window")
        self.moveMenu.addAction(QIcon(":/arrow-left.png") , "Dock Left"   , self.dockLeft)
        self.moveMenu.addAction(QIcon(":/arrow-right.png"), "Dock Right"  , self.dockRight)
        self.moveMenu.addAction(QIcon(":/arrow-up.png")   , "Dock Top"    , self.dockTop)
        self.moveMenu.addAction(QIcon(":/arrow-down.png") , "Dock Bottom" , self.dockBottom)
        self.moveMenu.addAction(QIcon(":/paste.png")      , "Float Window", self.floatWindow)

        self.customContextMenuRequested.connect(self.showContextMenu)
    
    def closeEvent(self, event: QCloseEvent) -> None:
        super().closeEvent(event)
        self.aboutToClose.emit(self)
        self.deleteLater()
  
    @pyqtSlot(QPoint)
    def showContextMenu(self, pos : QPoint) -> None:
        widget     = self.sender()
        global_pos = widget.mapToGlobal(pos) if widget else self.mapToGlobal(pos)

        self.contextMenu.popup(global_pos)
        return self.contextMenu

    @pyqtSlot()
    def dockRight(self) -> None:
        self.requestArea.emit(self, Qt.RightDockWidgetArea)
    
    @pyqtSlot()
    def dockLeft(self) -> None:
        self.requestArea.emit(self, Qt.LeftDockWidgetArea)
    
    @pyqtSlot()
    def dockTop(self) -> None:
        self.requestArea.emit(self, Qt.TopDockWidgetArea)
    
    @pyqtSlot()
    def dockBottom(self) -> None:
        self.requestArea.emit(self, Qt.BottomDockWidgetArea)

    @pyqtSlot()
    def floatWindow(self) -> None:
        self.requestArea.emit(self, Qt.NoDockWidgetArea)

    @pyqtSlot()
    def closeOthers(self) -> None:
        self.requestCloseOthers.emit(self)
