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
# This file contains the classes "backend" and Qt Model classes of the DataViewer application
#
# pylint: disable-all

import os
import re
import sys
import math
import pathlib
import typing
import logging
import traceback
import numpy
from   collections.abc import Iterable

import pandas
import matplotlib.pyplot as plt
from   PyQt5.QtCore      import QFileInfo, QObject, QAbstractTableModel, QSettings, Qt, QModelIndex, \
                                QRunnable, QThreadPool, pyqtSignal, pyqtSlot
from   PyQt5.QtGui       import QColor
from   collections       import OrderedDict, namedtuple
from   pandas.io.parsers import TextFileReader
from   pandas.api.types  import is_numeric_dtype, is_float_dtype

######################################
# Module Global Functions / Variables
######################################

SETTINGS_FILENAME = os.path.join(pathlib.Path().home(), "data_viewer.ini")
PLOT_COLORS       = ['blue', 'orange', 'green', 'black', 'brown', 'purple', 'red', 'magenta', 'yellow', 'cyan']
MIN_PROGRESS_SIZE = 10 * 1024 * 1024 # 10 MB

# Function to read plain text into pandas dataframe
def read_text(filename : str, **kwargs) -> pandas.DataFrame:
    df = pandas.DataFrame()
    if isinstance(filename, str) and os.path.exists(filename):
        with open(filename, 'r') as file:
            lines = [line.strip() for line in file]
            df    = pandas.DataFrame({'Line Content' : lines})
    return df

# List of Default File Parser Arguments
DEFAULT_PARSERS = [
    # Name             , File Pattern               , Read Function (Callable)  , Write Function (Callable / str) , Suffix (on file write), Iterable (for reading), Keyword Arguments (Read), Keyword Arguments (Write)
    { "name" : "CSV"   , "pattern" : ".csv$|.xls$"  , "read_func" : pandas.read_csv   , "write_func" : 'to_csv'   , "suffix"   : ".csv"   , "read_iterable" : True , "write_iterable" : True, "low_memory" : False, "encoding" : "latin1", "write_kwargs" : {"index" : False, "encoding" : "latin1"}},
    { "name" : "Tab"   , "pattern" : "_tab.txt$"    , "read_func" : pandas.read_csv   , "write_func" : 'to_csv'   , "suffix"   : ".txt"   , "read_iterable" : True , "write_iterable" : True, "low_memory" : False, "encoding" : "latin1", "sep" : '\t', "write_kwargs" : {"index" : False, "encoding" : "latin1", "sep" : '\t'}},
    { "name" : "JSON"  , "pattern" : ".json$"       , "read_func" : pandas.read_json  , "write_func" : 'to_json'  , "suffix"   : ".json"  , "read_iterable" : False, "write_iterable" : False, "orient" : "records", "write_kwargs" : {"indent" : 2, "orient" : "records"}},
    { "name" : "Excel" , "pattern" : ".xlsx$|.odf$" , "read_func" : pandas.read_excel , "write_func" : 'to_excel' , "suffix"   : ".xlsx"  , "read_iterable" : False, "write_iterable" : False, "write_kwargs" : {"index" : False}},
    { "name" : "Pickle", "pattern" : ".pickle$"     , "read_func" : pandas.read_pickle, "write_func" : 'to_pickle', "suffix"   : ".pickle", "read_iterable" : False, "write_iterable" : False},
    { "name" : "HDF"   , "pattern" : ".hdf$|.h5"    , "read_func" : pandas.read_hdf   , "write_func" : 'to_hdf'   , "suffix"   : ".h5"    , "read_iterable" : False, "write_iterable" : False, "key" : "df", "write_kwargs" : {"key" : "df"}},
    
    # The default parser should always be listed last
    { "name" : "Text"  , "pattern" : ".log$"        , "read_func" : read_text         , "write_func" : 'to_csv'   , "suffix"   : ".txt"   , "read_iterable" : False, "write_iterable" : True, "default" : True, "write_kwargs" : {"index" : False, "sep" : ' '}},
]

#################################
# Classes
#################################

class Item(object):
    """ Abstract base class for a container whose contents can be validated """
    def __init__(self):
        super().__init__()
    
    def name(self) -> bool:
        raise NotImplementedError("This function must be implemented in subclasses")

    def isValid(self, **kwargs) -> bool:
        raise NotImplementedError("This function must be implemented in subclasses")

class ItemListModel(QAbstractTableModel):
    """ A qt based table model for a list of Item objects """

    def __init__(self, 
                 header_labels : typing.List[str],
                 item_list     : typing.Optional[typing.Iterable[Item]] = None, 
                 parent        : typing.Optional[QObject]               = None) -> None:
        super().__init__(parent=parent)
        self.header_labels : typing.List[str]  = header_labels
        self.item_list     : typing.List[Item] = []
        if isinstance(item_list, Iterable):
            self.item_list.extend(item_list)
    
    def __contains__(self, obj : typing.Any) -> bool:
        return self.item_list.__contains__(obj)

    def __len__(self) -> int:
        return self.item_list.__len__()
    
    # Notify views when the internal list is cleared
    def clear(self) -> None:
        if self.rowCount() > 0:
            super().beginRemoveRows(QModelIndex(), 0, self.rowCount() - 1)
            self.item_list.clear()
            super().endRemoveRows()
        return None

    # Notify views when items are appended to the internal list
    def append(self, obj : typing.Any) -> None:
        super().beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.item_list.append(obj)
        super().endInsertRows()
        return None
    
    def rowCount(self, parent : QModelIndex = QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self.item_list)
        return 0
    
    def columnCount(self, parent : QModelIndex = QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self.header_labels)
        return 0
    
    def index(self,
              row : int,
              column : int,
              parent : QModelIndex = QModelIndex()) -> QModelIndex:
        """Return the QModelIndex for a given cell in the model"""
        if parent == QModelIndex() and (self.rowCount() > row >= 0) and (self.columnCount() > column >= 0):
            return super().index(row, column, parent)
        return QModelIndex()
    
    def headerData(self, section : int, orientation: Qt.Orientation, role : int = ...) -> typing.Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal and self.columnCount() > section >= 0:
            return self.header_labels[section]
        return super().headerData(section, orientation, role)
    
    # Default valid roles with data stored in this model
    def validRoles(self) -> typing.List[Qt.ItemDataRole]:
        return [Qt.DisplayRole, Qt.ToolTipRole, Qt.UserRole, Qt.EditRole]
    
    def data(self, index : QModelIndex, role : int = ...) -> typing.Any:
        if index.isValid():
            if role in self.validRoles():
                item = self.item_list[index.row()]
                if isinstance(item, Item) and item.isValid():
                    if role == Qt.UserRole or role == Qt.DecorationRole:
                        return item
                    else:
                        return item.name()
        return None
    
    def setData(self, index : QModelIndex, value : typing.Any, role: int = ...) -> bool:
        if index.isValid() and role == Qt.UserRole and isinstance(value, Item):
            self.item_list[index.row()] = value
            self.dataChanged(index, index, self.validRoles())
            return True
        return super().setData(index, value, role)
    
    def flags(self, index : QModelIndex) -> Qt.ItemFlags:
        if index.isValid():
            return super().flags(index) | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEditable
        else:
            return super().flags(index)

# Container to hold a single conditional formatting rule
class ColorRule(Item):
    def __init__(self,
                 condition : str,
                 color     : typing.Union[str, QColor], 
                 enabled   : bool = True) -> None:
        super().__init__()
        self.condition = condition
        self.color     = QColor(color)
        self.enabled   = enabled

    # Check if two color rules are equal
    def __eq__(self, obj : object) -> bool:
        required_attributes = ["condition", "color", "enabled"]
        if all([hasattr(obj, att) for att in required_attributes]):
            return all([getattr(self, att) == getattr(obj, att) for att in required_attributes])
        return False
    
    def name(self):
        if isinstance(self.color, QColor):
            return self.color.name()
        elif isinstance(self.color, str):
            return self.color
        else:
            return "<Invalid_Color_Rule>"

    def isEnabled(self):
        return self.enabled

    def isValid(self, **kwargs) -> bool:
        kwargs      = kwargs # Unused
        valid_color = isinstance(self.color, QColor) or isinstance(self.color, str)
        return isinstance(self.condition, str) and len(self.condition) > 0 and \
               valid_color and QColor(self.color).isValid()

# Simple container to hold a column and color rule
ColumnColorRule = namedtuple("ColumnColorRule", ["column", "rule"])

# Dictionary of dataframe column names to a list of color rules
class ColorRulesModel(ItemListModel):
    COLUMN_NAME_COLUMN = 0
    CONDITION_COLUMN   = 1
    COLOR_COLUMN       = 2
    HEADER_LABELS      = ['Column', 'Condition', 'Color']
    CONDITION_TOOLTIP  = \
"""
A Python statement where "x" will be replaced with cell values.
Examples: 
  x == 1
  x % 2 == 0
  0 < x < 5,
  math.floor(abs(x)) % 2 == 0,
  "PASS" in str(x),
  ...
"""
    colorRulesChanged = pyqtSignal()

    def __init__(self,
                 item_list : typing.Optional[typing.Iterable[ColumnColorRule]] = None,
                 parent    : typing.Optional[QObject] = None) -> None:
        super().__init__(header_labels=self.HEADER_LABELS, item_list=item_list, parent=parent)

        # Additionally store rules in map for fast access from model
        self.rule_map : typing.Dict[str, typing.List[ColorRule]] = {}
        self.__update_rule_map()
    
    # Update the internal rule map when the item list is updated
    def __update_rule_map(self):
        self.rule_map.clear()
        for column_rule in self.item_list:
            if column_rule.column in self.rule_map.keys():
                self.rule_map[column_rule.column].append(column_rule.rule)
            else:
                self.rule_map[column_rule.column] = [column_rule.rule]
    
    def append(self, rule : ColumnColorRule) -> None:
        if isinstance(rule, ColumnColorRule):
            if rule.column in self.rule_map:
                self.rule_map[rule.column].append(rule.rule)
            else:
                self.rule_map[rule.column] = [rule.rule]
            self.colorRulesChanged.emit()
            return super().append(rule)
    
    def clear(self) -> None:
        self.rule_map.clear()
        self.colorRulesChanged.emit()
        return super().clear()
    
    # Default valid roles with data stored in this model
    def validRoles(self) -> typing.List[Qt.ItemDataRole]:
        return super().validRoles() + [Qt.DecorationRole, Qt.CheckStateRole]
    
    def data(self, index : QModelIndex, role : int = ...) -> typing.Any:
        if index.isValid():
            item = self.item_list[index.row()]
            if isinstance(item, ColumnColorRule) and item.rule.isValid():
                if role == Qt.CheckStateRole:
                    if index.column() == self.COLUMN_NAME_COLUMN:
                        return Qt.Checked if item.rule.isEnabled() else Qt.Unchecked
                elif role in [Qt.DisplayRole, Qt.ToolTipRole, Qt.EditRole]:
                    if index.column() == self.COLUMN_NAME_COLUMN:
                        return item.column
                    elif index.column() == self.CONDITION_COLUMN:
                        return self.CONDITION_TOOLTIP if role == Qt.ToolTipRole else item.rule.condition
                    elif index.column() == self.COLOR_COLUMN:
                        return QColor(item.rule.color).name()
                elif role in [Qt.UserRole, Qt.DecorationRole] and index.column() == self.COLOR_COLUMN:
                    return QColor(item.rule.color)
        return None
    
    def setData(self, index : QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if index.isValid():
            item     = self.item_list[index.row()]
            new_item = item
            if isinstance(item, ColumnColorRule) and item.rule.isValid():
                if role == Qt.CheckStateRole:
                    if index.column() == self.COLUMN_NAME_COLUMN:
                        new_item = ColumnColorRule(item.column, ColorRule(item.rule.condition, QColor(item.rule.color), value))
                elif role == Qt.EditRole:
                    if index.column() == self.COLUMN_NAME_COLUMN:
                        new_item = ColumnColorRule(value, ColorRule(item.rule.condition, QColor(item.rule.color), item.rule.enabled))
                    elif index.column() == self.CONDITION_COLUMN:
                        new_item = ColumnColorRule(item.column, ColorRule(value, QColor(item.rule.color), item.rule.enabled))
                    elif index.column() == self.COLOR_COLUMN:
                        new_item = ColumnColorRule(item.column, ColorRule(item.rule.condition, QColor(value), item.rule.enabled))
                else:
                    return False
            
            # Update the item in the internal list if it changed
            if not(new_item is item):
                self.item_list[index.row()] = new_item
                self.__update_rule_map()
                self.dataChanged.emit(index, index, self.validRoles())
                self.colorRulesChanged.emit()
                return True

        return False
    
    @staticmethod
    def fromJson(d : dict):
        result = ColorRulesModel()
        for column, rule_list in d.items():
            try:
                for rule_dict in rule_list:
                    enabled = rule_dict.get("enabled", True)
                    result.append(ColumnColorRule(column, ColorRule(condition=rule_dict['condition'], color=QColor(rule_dict['color']), enabled=enabled)))
            except:
                logging.getLogger(__name__).debug(f"Invalid Color Rules: {rule_dict}")
        return result
    
    def toJson(self) -> typing.Dict[str, typing.List[typing.Dict[str, str]]]:
        result = {}
        for key, value_list in self.rule_map.items():
            try:
                values = [v.__dict__ for v in value_list]
                for value in values:
                    value['color'] = QColor(value['color']).name()
                result[key] = values
            except:
                logging.getLogger(__name__).debug(f"Invalid Color Rules: {value_list}")
        return result

# Disable matplotlib debug logging
loggers = [logging.getLogger('matplotlib.font_manager'), logging.getLogger('_base')]
for l in loggers:
    if isinstance(l, logging.Logger):
        l.disabled = True

def get_unique_column_name(name : str, columns : list):
    # Adjust the name if needed to ensure its unique
    i           = 1
    format_str  = '%s %d'
    col_name    = name
    while col_name in columns:
        i        += 1
        col_name  = format_str % (name, i)
    return col_name

# Function to compute the delta of a series
def delta(series : pandas.Series):
    x        = series.diff()
    x.loc[0] = 0
    return x

# Simple container to hold options for plotting
class PlotInfo(Item):
    def __init__(self, 
                 x : typing.Union[str, pandas.Series, None],
                 y : typing.List[typing.Union[str, pandas.Series]],
                 **options) -> None:
        self.x       = x
        self.y       = y
        self.options = options
        self.options.setdefault("kind"       , "line")
        self.options.setdefault("sharex"     , True)
        self.options.setdefault("secondary_y", False)
    
    def __eq__(self, o : object) -> bool:
        x_equal       = hasattr(o, "x")       and getattr(o, "x")       == self.x
        y_equal       = hasattr(o, "y")       and getattr(o, "y")       == self.y
        options_equal = hasattr(o, "options") and getattr(o, "options") == self.options
        return x_equal and y_equal and options_equal
    
    def name(self, short = False) -> str:
        plot_title = self.options.get("title", ", ".join(self.y))
        if short:
            plot_name = plot_title
        elif self.x is None or "title" in self.options.keys():
            plot_name = f'{self.options.get("kind", "line").capitalize()}: {plot_title}'
        else:
            plot_name = f'{self.options.get("kind", "line").capitalize()}: {plot_title} vs {self.x}'
        return plot_name
    
    # Validate the minimum required plotting information
    def isValid(self, **kwargs) -> bool:
        df      = kwargs.get("df", None)
        x_valid = self.x is None or isinstance(self.x, str) or isinstance(self.x, pandas.Series)
        if isinstance(self.y, list) and len(self.y) > 0:
            # Y columns can be string column names or explicit pandas.Series objects
            if isinstance(df, pandas.DataFrame):
                y_valid = all([(isinstance(i, str) and i in df.columns) or isinstance(i, pandas.Series) for i in self.y])
            else:
                y_valid = all([(isinstance(i, str)) or isinstance(i, pandas.Series) for i in self.y])
        else:
            y_valid = False
        return x_valid and y_valid and isinstance(self.options, dict)
    
    def to_dict(self) -> typing.Dict[str, typing.Any]:
        new_dict = {}
        new_dict["x"]       = self.x
        new_dict["y"]       = self.y
        new_dict["options"] = self.options
        return new_dict
    
    @staticmethod
    def from_dict(d : typing.Dict[str, typing.Any]):
        info = PlotInfo(x=d.get("x", None), y=d.get("y", []), **d.get("options", {}))
        return info

class PlotInfoListModel(ItemListModel):
    """ A qt based table model for a list of PlotInfo objects"""
    HEADER_LABELS = ["Saved Plots"]

    def __init__(self,
                 info_list : typing.Optional[typing.Iterable[PlotInfo]] = None, 
                 parent    : typing.Optional[QObject] = None) -> None:
        super().__init__(header_labels=self.HEADER_LABELS, item_list=info_list, parent=parent)
    
    @staticmethod
    def fromJson(df : pandas.DataFrame, json_obj : typing.List[typing.Dict[str, typing.Any]]):
        result = PlotInfoListModel()
        if isinstance(json_obj, Iterable):
            for dict_obj in json_obj:
                if isinstance(dict_obj, dict) and all([k in dict_obj.keys() for k in ["x", "y", "options"]]):
                    info = PlotInfo.from_dict(dict_obj)
                    if info.isValid(df=df):
                        result.append(info)
        return result

    def toJson(self) -> typing.List[typing.Dict[str, typing.Any]]:
        result = []
        for info in self.item_list:
            if isinstance(info, PlotInfo):
                result.append(info.to_dict())
        return result
    
class DataFrameModel(QAbstractTableModel):
    """ A qt based table model for a pandas dataframe """

    cellChanged       = pyqtSignal(QModelIndex, str, int)
    plotCreated       = pyqtSignal(PlotInfo)
    colorRulesChanged = pyqtSignal(ColorRulesModel)

    def __init__(self, dataframe : pandas.DataFrame, filename : str = "", parent : QObject = None):
        QAbstractTableModel.__init__(self, parent)
        self.df        = dataframe
        self.filename  = filename
        self.ref_count = 1
        self.logger    = logging.getLogger(__name__)

        self.color_rules_model : ColorRulesModel = ColorRulesModel(parent=self)
    
    # Clear all color rules in this mode
    def clearColorRules(self):
        self.color_rules_model.clear()
        self.colorRulesChanged.emit(self.color_rules_model)

    # Add a new color rule to this model
    def addColorRule(self, column : str, rule : ColorRule):
        self.color_rules_model.append(ColumnColorRule(column, rule))
        self.colorRulesChanged.emit(self.color_rules_model)

    # Setter for Color Rules Model
    def setColorRules(self, rules_model : ColorRulesModel):
        self.color_rules_model = rules_model
        self.colorRulesChanged.emit(self.color_rules_model)

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self.df)

        return 0

    def columnCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self.df.columns)
        return 0

    def getBackgroundColor(self, index : QModelIndex) -> QColor:
        color = None
        col   = self.df.columns[index.column()]
        x     = str(index.data(Qt.DisplayRole))
        if col in self.color_rules_model.rule_map.keys():
            rules = [rule for rule in self.color_rules_model.rule_map[col] if rule.isValid() and rule.isEnabled()]
            for rule in rules:
                try: 
                    condition = rule.condition.replace('str(x)', f"'{x}'").replace('x', x)
                    result = eval(condition)
                except:
                    result = False
                if result:
                    color = QColor(rule.color)
        return color

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        value = None
        if not index.isValid():
            return value

        if role == Qt.BackgroundColorRole:
            return self.getBackgroundColor(index)
        elif role == Qt.CheckStateRole:
            value = None
        else:
            value = self.df.iloc[index.row(), index.column()]
            if role == Qt.DisplayRole or role == Qt.ToolTipRole:
                try:
                    dtype = self.df[self.df.columns[index.column()]].dtype
                    if dtype == float:
                        return '%6.5f' % value
                except:
                    return str(value)
                return str(value)

        return value
    
    def flags(self, index : QModelIndex) -> Qt.ItemFlags:
        flags = super(self.__class__,self).flags(index)
        if index.isValid():
            flags |= Qt.ItemIsEditable
            flags |= Qt.ItemIsSelectable
            flags |= Qt.ItemIsEnabled
            flags |= Qt.ItemIsDragEnabled
            flags |= Qt.ItemIsDropEnabled
        return flags
    
    def setData(self, index : QModelIndex, value : typing.Any, role : int = Qt.EditRole) -> bool:
        if index.isValid():
            if role == Qt.EditRole:
                dtype = self.df[self.df.columns[index.column()]].dtype
                try:
                    if type(value) == str and not(dtype == str):
                        if 'float' in dtype.name:
                            casted_value = float(value)
                        elif 'int' in dtype.name:
                            casted_value = int(value)
                        else:
                            casted_value = value
                    elif dtype == 'O':
                        casted_value = str(value)
                    else:
                        casted_value = value
                except:
                    casted_value = value
                self.df.iloc[index.row(), index.column()] = casted_value
                self.cellChanged.emit(index, str(casted_value), role)
                return True

        return super().setData(index, value, role=role)
    
    def setHeaderData(self, section : int, orientation : Qt.Orientation, value : typing.Any, role: int = Qt.EditRole)-> bool:
        if role == Qt.EditRole or role == Qt.DisplayRole and orientation == Qt.Horizontal and section < self.columnCount() and isinstance(value, str) and len(value) > 0:
            new_df  = self.df.rename(columns={self.df.columns[section] : get_unique_column_name(value, self.df.columns) })
            self.df = new_df
            return True

        return super().setHeaderData(section, orientation, value, role=role)

    def headerData(self, section : int, orientation : Qt.Orientation, role : Qt.ItemDataRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.df.columns[section])

            if orientation == Qt.Vertical:
                return str(self.df.index[section])

        return None
    
    def addColumn(self, name : str, column : typing.Any = "", index : int = None) -> bool:
        if index is None:
            index = self.columnCount()
        if isinstance(name, str) and len(name) > 0:
            unique_name = get_unique_column_name(name, self.df.columns)
            self.beginInsertColumns(QModelIndex(), index, index)
            if index >= 0 and index < self.columnCount():
                self.df.insert(index+1, unique_name, column)
            else:
                self.df[unique_name] = column
            self.endInsertColumns()
            return True
        return False
    
    def setColumn(self, index : int = None, column : typing.Any = "") -> bool:
        if isinstance(index, int) and index >= 0 and index < self.columnCount():
            colName          = self.df.columns[index]
            topLeft          = self.index(0, index)
            bottomRight      = self.index(len(self.df[colName])-1, index)
            self.df[colName] = column
            self.dataChanged.emit(topLeft, bottomRight)
            return True
        return False
    
    def dropColumns(self, indexes : list) -> bool:
        if isinstance(indexes, list) and len(indexes) > 0 and all([i >= 0 and i < self.columnCount() for i in indexes]):
            columns = [self.df.columns[i] for i in indexes]
            for col in columns:
                idx = self.df.columns.get_loc(col)
                self.beginRemoveColumns(QModelIndex(), idx, idx)
                self.df = self.df.drop(self.df.columns[idx], axis=1)
                self.endRemoveColumns()
            return True
        return False
    
    def sortByColumn(self, column : int) -> bool:
        if isinstance(column, int) and column < len(self.df.columns):
            self.df.sort_values(self.df.columns[column], inplace=True)
            return True
        return False

    def findColumn(self, name : str) -> int:
        if isinstance(name, str) and len(name) > 0:
            try:
                index = list(self.df.columns).index(name)
            except:
                index = -1
        else:
            index = -1
        return index

    def findColumns(self, regex_str : str) -> list:
        if isinstance(regex_str, str) and len(regex_str) > 0:
            try:
                matches = [col for col in self.df.columns if re.search(regex_str, col, re.IGNORECASE)]
            except:
                matches = []
        else:
            matches = []
        return matches
    
    def findAllColumns(self, regex_list : list) -> list:
        matches = []
        if isinstance(regex_list, list):
            for regex in regex_list:
                matches += self.findColumns(regex)
        return matches
    
    # Simple utility function to attempt to plot a column from a dataframe
    def tryPlot(self, df : pandas.DataFrame, **kwargs) -> typing.Any:
        try:
            return df.plot(**kwargs)
        except Exception as e:
            y = kwargs.get("y", "")
            self.logger.error(f"Error Creating plot {y}")
            self.logger.debug(f"Exception raised: {e}")
            self.logger.debug(f"Keyword arguments {kwargs}")
            return None

    def plotColumns(self, x           : typing.Union[str, pandas.Series, None], 
                          y           : typing.List[typing.Union[str, pandas.Series]], 
                          interactive : bool = True,
                          **options) -> bool:

        # Get plot information and set defaults
        num_cols    = len(y) if isinstance(y, list) else 0
        kind        = options.setdefault("kind", "line")
        subplots    = options.setdefault("subplots", True)
        secondary_y = options.setdefault("secondary_y", False) 
        options.setdefault("legend", True)

        if num_cols < 1 or any([col_name not in self.df.columns for col_name in y]):
            self.logger.error(f"Invalid Plotting Arguments: {x}, {y}, {options}")
            return False

        # Correct the X-Axis if needed
        if isinstance(x, str) and len(x) < 1:
            # Setting x to None defaults to use dataframe index
            x = None
        if x is None and kind in ['scatter', 'hexbin'] and len(self.df.columns) > 0:
            # Some plot types require an explicit X-axis
            x = self.df.columns[0]
        
        # Extract the ylim2 argument since it is not supported by DataFrame.plot()
        ylim2 = options.pop("ylim2", None)

        # Raise the plots interactively if requested
        if interactive:
            plt.ion()
        else:
            plt.ioff()

        # Setup the canvas for the plots
        fig, axes = plt.subplots(num_cols if subplots else 1, sharex=options.get("sharex", True))
        if not(isinstance(axes, Iterable)):
            axes = [axes] 
        if kind == 'pie':
            # Add percentages to pie charts by default
            options.setdefault('autopct', '%1.0f%%')
        
        # Generate the plot one column at a time
        success = True
        for i in range(num_cols):
            col   = self.df[y[i]]
            color = PLOT_COLORS[i % len(PLOT_COLORS)]
            ax    = axes[i] if subplots else axes[0]
            if is_numeric_dtype(col):
                # Plot the column normally
                if kind == "pie":
                    value_counts = col.value_counts()
                    success &= bool(self.tryPlot(df=value_counts, ax=ax, **options))
                else:
                    ax2 = self.tryPlot(df=self.df, x=x, y=col.name, ax=ax, color=color, **options)
                    if isinstance(secondary_y, list) and col.name in secondary_y and isinstance(ylim2, tuple):
                        ax2.set_ylim(ylim2)
                    success &= bool(ax2)
            else:
                if kind == "pie":
                    value_counts = col.value_counts()
                    self.tryPlot(df=value_counts, ax=ax, **options)
                else:
                    # Temporarily replace string values for plotting
                    tmp_col = f" {col.name} "
                    tmp_options = { **options }
                    if isinstance(secondary_y, list):
                        tmp_options["secondary_y"] = [i for i in secondary_y if i != col.name]
                        if col.name in secondary_y:
                            tmp_options["secondary_y"] += [tmp_col]
                    tmp_secondary_y = tmp_options.get("secondary_y", False)
                    try:
                        labels           = set(col.astype(str))
                        enum_map         = dict(zip(labels, range(len(labels))))
                        self.df[tmp_col] = col.map(enum_map)
                        if success:
                            if kind == 'hist':
                                ax.set_xticklabels(labels)
                                success &= bool(self.tryPlot(df=self.df, x=x, y=tmp_col, xticks=range(len(labels)), ax=ax, color=color, **tmp_options))
                            else:
                                ax2 = self.tryPlot(df=self.df, x=x, y=tmp_col, ax=ax, color=color, **tmp_options)
                                if isinstance(tmp_secondary_y, list) and tmp_col in tmp_secondary_y:
                                    if isinstance(ax2, Iterable):
                                        for tmp_ax in ax2:
                                            tmp_ax.set_yticks(range(len(labels)))
                                            tmp_ax.set_yticklabels(labels)
                                            if isinstance(ylim2, tuple):
                                                tmp_ax.set_ylim(ylim2)
                                    else:
                                        ax2.set_yticks(range(len(labels)))
                                        ax2.set_yticklabels(labels)
                                        if isinstance(ylim2, tuple):
                                            ax2.set_ylim(ylim2)
                                else:
                                   ax.set_yticks(range(len(labels)))
                                   ax.set_yticklabels(labels)
                                success &= bool(ax2)
                            self.df.drop(tmp_col, axis=1, inplace=True)
                    except Exception as e:
                        self.logger.error(f"Unable to enumerate {col.name}. Error: {e}")
                        success = False
            
        # Add the plot title and signal creation if no errors occured
        info  = PlotInfo(x, y, **options)
        title = f"{fig.canvas.manager.get_window_title()}: {info.name(short=True)}"
        fig.canvas.manager.set_window_title(title)

        if success:
            self.plotCreated.emit(info)
        else:
            return False

        return True
    
    # Return the maximum length (in pixels) of all items in a column
    def columnMaxPixelLen(self, column : int) -> int:
        if self.columnCount() > column >= 0:
            header_len   = len(self.df.columns[column])
            series       = self.df[self.df.columns[column]]
            if is_float_dtype(series.dtype):
                max_item_len = series.apply(lambda x : len("%.6f" % x)).max()
            else:
                max_item_len = series.astype(str).apply(len).max()

            # Set the column width based on the number of characters
            character_len = max(header_len, max_item_len)

            # Slightly decrease the pixel scale as the character length increases
            # to avoid very large column pixel widths
            min_pixel_ratio = 2
            max_pixel_ratio = 12
            pixel_scale = max(min_pixel_ratio, max_pixel_ratio - (2 * int(character_len / max_pixel_ratio)))
            margin      = pixel_scale if character_len > max_pixel_ratio else 2 * max_pixel_ratio
            return (character_len * pixel_scale) + margin
        return 0
    
    def saveToCSV(self, filename : str, columns : typing.List[str] = None) -> bool:
        
        # Write the internal dataframe to a CSV
        try:
            if isinstance(columns, list):
                self.df[columns].to_csv(filename, index_label="__index__")
            else:
                self.df.to_csv(filename, index_label="__index__")
        except Exception as e:
            self.logger.error(f"Unable to save to {filename}. Exception: {e}")
            return False

        return os.path.exists(filename)

# Convenience wrapper class to encapsulate dataframe read/write functions
class DataFrameParser():
    def __init__(self, name           : str,
                       pattern        : str, 
                       read_func      : typing.Callable = None, 
                       write_func     : str             = '',
                       read_iterable  : bool            = False,
                       write_iterable : bool            = False,
                       suffix         : str             = ".csv",
                       write_kwargs   : dict            = None,
                       **read_kwargs) -> None:
        self.name           = name
        self.pattern        = pattern
        self.read_func      = read_func
        self.write_func     = write_func 
        self.read_iterable  = read_iterable
        self.write_iterable = write_iterable
        self.suffix         = suffix
        self.write_kwargs   = write_kwargs
        self.read_kwargs    = read_kwargs
        self.logger         = logging.getLogger(__name__)
    
    def __str__(self) -> str:
        return f"DataFrameParser({self.name}, pattern={self.pattern})"
    
    def read(self, filename : str, **kwargs) -> typing.Union[pandas.DataFrame, TextFileReader]:
        try:
            result = self.read_func(filename, **kwargs)
        except Exception as e:
            self.logger.error(f"Unable to read {filename}. Error: {e} ")
            result = pandas.DataFrame()
        return result

    def write(self, df : pandas.DataFrame, file_or_buf : typing.Union[str, object], **kwargs) -> bool:
        success = False
        if callable(self.write_func):
            try:
                self.write_func(df, file_or_buf, **kwargs)
                success = True
            except Exception as e:
                self.logger.error(f"Write function '{self.name}' failed for {file_or_buf} with args {kwargs}. Error: {e}")
        elif isinstance(self.write_func, str) and hasattr(df, self.write_func):
            write_func = getattr(df, self.write_func)
            try:
                write_func(file_or_buf, **kwargs)
                success = True
            except Exception as e:
                self.logger.error(f"Write function '{self.name}' failed for {file_or_buf} with args {kwargs}. Error: {e}")
        else:
            self.logger.exception(f"Unsupported write type ({self.write_func, type(self.write_func)}. Args = {df, file_or_buf, kwargs}")
        
        return success

    # Determine the number of rows from the size of a file
    def inferRowCount(self, filename : str) -> int:
        info = QFileInfo(filename)
        if self.read_iterable and info.exists() and info.isFile():
            try:
                with open(info.absoluteFilePath()) as file:
                    file.readline() # Skip header
                    first_row = file.readline()
                    row_len   = len(first_row)
                row_count = int(info.size() / row_len)
                return row_count
            except:
                self.logger.debug(f"Failed to infer row count for {info.fileName()}")

        return 1
    
    @staticmethod
    def fromDict(d : typing.Dict[str, typing.Any]) -> typing.Any:
        parser = None
        try:
            symbols        = globals()
            write_func     = symbols[d['write_func']]              if d['write_func'] in symbols.keys() else d['write_func']
            read_func      = eval(d['read_func'])                  if isinstance(d['read_func'], str)   else d['read_func']
            read_kwargs    = eval(d['kwargs'])                     if isinstance(d['kwargs']   , str)   else d['kwargs']
            read_iterable  = bool(d['iterable'].lower() == 'true') if isinstance(d['iterable'] , str)   else d['iterable']
            write_iterable = d.get("write_iterable", False)
            write_kwargs   = eval(d.get("write_kwargs", {}))       if isinstance(d.get("write_kwargs", {}), str) else {}
            kwargs = {}
            if "suffix" in d.keys():
                kwargs["suffix"] = d["suffix"]
            parser = DataFrameParser(name=d['name'],
                                     pattern=d['pattern'],
                                     read_func=read_func,
                                     write_func=write_func,
                                     read_iterable=read_iterable,
                                     write_iterable=write_iterable,
                                     write_kwargs=write_kwargs,
                                     **kwargs, 
                                     **read_kwargs)
        except:
            logging.getLogger(__name__).error(f"Unable to convert parser from dictionary: {d}")
        return parser

    def toDict(self) -> typing.Dict[str, typing.Any]:
        data = {}
        read_func  = f'{self.read_func.__module__}.{self.read_func.__name__}' if 'pandas' in self.read_func.__module__ else self.read_func.__name__
        write_func = f'{self.write_func.__name__}' if callable(self.write_func) else self.write_func
        data['name']           = self.name
        data['pattern']        = self.pattern
        data['read_func']      = read_func
        data['write_func']     = write_func
        data['suffix']         = self.suffix
        data['iterable']       = self.read_iterable
        data['write_iterable'] = self.write_iterable
        data['write_kwargs']   = self.write_kwargs
        data['kwargs']         = self.read_kwargs
        return data

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    started
        int for worker id, int indicating total steps

    progress
        int for worker id, int indicating % progress

    finished
        int for worker id

    error
        int for worker id, tuple (exctype, value, traceback.format_exc() )

    result
        int for worker id, object data returned from processing, anything

    '''
    started  = pyqtSignal(int, int)
    progress = pyqtSignal(int, int, int)
    error    = pyqtSignal(int, tuple)
    result   = pyqtSignal(int, str, object)
    finished = pyqtSignal(int, str)

# Convenience class to carry worker information
WorkerInfo = namedtuple("WorkerInfo", ["id", "filename", "steps"])

# QRunnable subclass for parsing dataframes in background threads
class DataFrameWorker(QRunnable):
    def __init__(self,
                 id        : int, 
                 steps     : int              = 1,
                 parser    : DataFrameParser  = None,
                 filename  : str              = None,
                 df        : pandas.DataFrame = None,
                 operation : str              = None,
                 **kwargs):
        super(DataFrameWorker, self).__init__()
        self.id        = id
        self.steps     = steps
        self.parser    = parser
        self.filename  = filename
        self.df        = df
        self.operation = operation
        self.kwargs    = kwargs
        self.signals   = WorkerSignals() 
        self.logger    = logging.getLogger(__name__)
        self.setAutoDelete(False)
    
    @pyqtSlot()
    def run(self):
        '''
        Initialize the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            if self.operation == "write":
                result = self.write_task()
            elif self.operation == "read":
                result = self.read_task()
            else: 
                result = self.merge_task()
        except:
            # An error occured, notify of the error
            self.logger.error(f"{self.operation} failed for {self.filename} (kwargs = {self.kwargs})")
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit(self.id, (exctype, value, traceback.format_exc()))
        else:
            if isinstance(result, pandas.DataFrame) or isinstance(result, bool):
                self.signals.result.emit(self.id, self.filename, result)  # Return the result of the processing
            elif not(result is None):
                logging.debug(f"Unexpected result ({result}) from worker thread {self.id}")

        finally:
            self.signals.finished.emit(self.id, self.filename)  # Done
    
    def info(self) -> WorkerInfo:
        return WorkerInfo(self.id, self.filename, self.steps)
        
    def read_task(self):
        result = None

        # Read the data into a dataframe
        self.logger.debug(f"Reading {self.filename}...")
        self.signals.started.emit(self.id, self.steps)

        # Setup the arguments
        self.kwargs = {**self.kwargs, **self.parser.read_kwargs}

        if self.parser.read_iterable and self.steps > 1 and 'chunksize' in self.kwargs.keys():
            iterator = self.parser.read(self.filename, **self.kwargs)
            if isinstance(iterator, pandas.DataFrame):
                result = iterator
                self.logger.debug(f"Unable to obtain iterator for {self.filename} with kwargs {self.kwargs}")
            else:
                chunks = []
                for i, chunk in enumerate(iterator):
                    chunks.append(chunk)
                    self.signals.progress.emit(self.id, i, self.steps)
                result = pandas.concat(chunks)
        else:
            result = self.parser.read(self.filename, **self.kwargs)

        self.logger.debug(f"Successfully read {self.filename}...")
        return result

    def write_task(self):
        result = False
        kwargs = self.parser.write_kwargs if isinstance(self.parser.write_kwargs, dict) else {}

        # Write the dataframe to a file
        self.logger.debug(f"Writing dataframe to {self.filename}... parser {self.parser}, kwargs {kwargs}")
        self.signals.started.emit(self.id, self.steps)
        if self.steps > 1 and isinstance(self.df, pandas.DataFrame) and self.df.shape[0] > self.steps:
            # Write the file in chunks
            chunks = numpy.array_split(self.df, self.steps)
            result = True
            if os.path.exists(self.filename):
                try:
                    os.remove(self.filename)
                except:
                    self.logger.error(f"Unable to delete {self.filename}")
                    result = False
            if result:
                with open(self.filename, mode="a") as file_handle:
                    for i, chunk in enumerate(chunks):
                        self.signals.progress.emit(self.id, i, self.steps)
                        if self.parser.suffix in [".csv", ".txt"]:
                            kwargs["header"] = bool(i == 0)
                        result &= self.parser.write(chunk, file_handle, **kwargs)
        else:
            # Call the write function once in a single thread
            if self.parser.write(self.df, self.filename, **kwargs):
                self.logger.debug(f"Single pass write successful for {self.filename}")
                result = True
            else:
                self.logger.error(f"Unable to write {self.filename}")
        
        return result
    
    def merge_task(self):
        result = None
        if hasattr(pandas, self.operation):
            
            if "title" in self.kwargs.keys():
                title = self.kwargs.pop("title")
            else:
                title = "New_Merged_Table"

            # Try to perform the merge operation
            func = getattr(pandas, self.operation)
            try:
                result = func(**self.kwargs)
            except Exception as e:
                self.logger.error(f"Merge Failed. Exception: {e}")
            
            if isinstance(result, pandas.DataFrame):
                self.logger.info(f"Successfully created merged table {title}")
            else:
                self.logger.error(f"Merge Failed. Invalid result type: {result}")
        else:
            self.logger.error(f'Merge operation "{self.operation}" not available')
        
        return result

class DataFrameFactory(QObject):

    # Singleton instance of factory object
    instance = None

    # Progress Signals
    progressStarted  = pyqtSignal(int)      # Number of Steps
    progressUpdate   = pyqtSignal(int, int) # Step, Max Steps
    progressMessage  = pyqtSignal(str)      # Message
    progressFinished = pyqtSignal()

    # Factory Signals
    modelCreated = pyqtSignal(DataFrameModel)

    # Keep a count of all the workers created to maintain a unique ID for each worker
    numWorkersCreated = 0

    def __init__(self, parent : QObject = None) -> None:
        super().__init__(parent=parent)
        self.logger          : logging.Logger                    = logging.getLogger(__name__)
        self.parsers         : typing.Dict[str, DataFrameParser] = OrderedDict()
        self.default_parser  : DataFrameParser                   = None
        self.threadpool      : QThreadPool                       = QThreadPool.globalInstance()
        self.active_workers  : typing.Dict[int, DataFrameWorker] = OrderedDict()
        self.active_msg_id   : int                               = -1
        self.progress_step   : int                               = 0
        self.progress_steps  : int                               = 0
        self.models          : typing.Dict[str, DataFrameModel]  = {}

        # Register the model parsers
        settings  = QSettings(SETTINGS_FILENAME, QSettings.IniFormat)
        keys      = settings.allKeys()
        anyParser = False
        if 'parsers' in keys:
            itemList = settings.value('parsers')
            if isinstance(itemList, list):
                for item in itemList:
                    if isinstance(item, dict):
                        parser = DataFrameParser.fromDict(item)
                        if isinstance(parser, DataFrameParser):
                            default = item['default'] if 'default' in item.keys() else False
                            self.registerParser(parser, default=default)
                            anyParser = True
        if not(anyParser):
            self.setDefaultParsers()
        elif self.default_parser is None:
            self.createParser(**DEFAULT_PARSERS[-1])
    @staticmethod
    def getInstance(parent : QObject = None):
        if DataFrameFactory.instance is None:
            DataFrameFactory.instance = DataFrameFactory(parent)
        return DataFrameFactory.instance
    
    def registerParser(self, parser : DataFrameParser, default : bool = False) -> DataFrameParser:
        # Install the parser to the factory
        self.parsers[parser.pattern] = parser
        if default:
            self.default_parser = parser
        return parser

    def createParser(self, default : bool = False, **kwargs) -> DataFrameParser:
        # Create the parser object
        parser = DataFrameParser(**kwargs)
        return self.registerParser(parser, default=default)

    def setDefaultParsers(self):
        self.parsers.clear()
        for kwargs in DEFAULT_PARSERS:
            self.createParser(**kwargs)
    
    def getParser(self, filename : str) -> DataFrameParser:
        parser = None
        for pattern, df_parser in self.parsers.items():
            if re.search(pattern, filename, re.IGNORECASE):
                parser = df_parser
                self.logger.debug(f"File {filename} matched pattern ({pattern}), selecting parser: {parser}")
                break
        if parser is None:
            parser = self.default_parser
            self.logger.debug(f"Selecting default parser for {filename}, parser: {parser}")
        return parser

    # Factory creation of dataframes
    def createDataFrame(self, filename : str, **kwargs):
        df = None
        if os.path.exists(filename):
            parser = self.getParser(filename)
            if isinstance(parser, DataFrameParser):
                df = parser.read(filename, **kwargs)
            else:
                self.logger.error(f"Unable to find supported parser for {filename}")
        else:
            self.logger.warning(f"The filename {filename} does not exist")

        if not(isinstance(df, pandas.DataFrame)):
            self.logger.debug(f"Defaulting to empty dataframe for {filename}")
            df = pandas.DataFrame()
        return df
    
    def createModel(self, filename : str, df : pandas.DataFrame = None, **kwargs) -> DataFrameModel:
        notify = True
        if isinstance(df, pandas.DataFrame):
            if not(isinstance(filename, str)) or len(filename) < 1:
                # Give a unique identfier to dataframes created from memory
                filename = f"<local_dataframe_{len(self.models)}>"
            model = DataFrameModel(df, filename)
            if filename in self.models.keys():
                notify = False
            else:
                self.models[filename] = model
        elif isinstance(filename, str):
            if filename in self.models.keys():
                model            = self.models[filename]
                model.ref_count += 1
            else:
                dataframe = self.createDataFrame(filename, **kwargs)
                model     = DataFrameModel(dataframe, filename)
                self.models[filename] = model
        else:
            self.logger.error(f"Invalid arguments in createModel(); filename={filename}, df={df}. Defaulting to empty model")
            model = DataFrameModel(pandas.DataFrame())

        # Notify listeners that a new model is ready
        if notify:
            self.modelCreated.emit(model)

        return model

    @pyqtSlot(int, int)
    def onWorkerStarted(self, worker_id : int, num_steps : int):
        self.logger.debug(f"Started worker thread {worker_id} with {num_steps} steps")

    @pyqtSlot(int, int, int)
    def onWorkerProgress(self, worker_id : int, progress_step : int, total_steps : int):
        if isinstance(worker_id, int):
            if total_steps == self.progress_steps:
                self.progress_step = progress_step
            else:
                self.progress_step += 1
            if self.progress_step < self.progress_steps:
                self.progressUpdate.emit(self.progress_step, self.progress_steps)

    @pyqtSlot(int, tuple)
    def onWorkerError(self, worker_id : int, error_info : typing.Tuple[BaseException, typing.Any, str]):
        self.logger.error(f"Worker Thread {worker_id}. Error: {error_info}")

    @pyqtSlot(int, str, object)
    def onWorkerResultReady(self, worker_id : int, filename : str, result : typing.Any):
        if isinstance(result, pandas.DataFrame):
            self.createModel(filename, result)
        elif isinstance(result, bool):
            if result and QFileInfo(filename).exists():
                self.logger.info(f"Successfully wrote {filename}")
            else:
                self.logger.info(f"Unable to write {filename}")
        else:
            self.logger.debug(f"Unexpected result from worker thread {worker_id}: {result}")
    
    @pyqtSlot(int, str)
    def onWorkerFinished(self, worker_id : int, filename : str):

        if len(filename) > 0:
            message = QFileInfo(filename).fileName()
            self.progressMessage.emit(message)
            
        # Remove this worker thread
        if worker_id in self.active_workers.keys():
            self.active_workers.pop(worker_id)

        if len(self.active_workers) < 1:
            self.progressFinished.emit()
    
    @pyqtSlot()
    def onCancel(self):
        if len(self.active_workers) > 0:
            self.logger.debug(f"Trying to cancel {len(self.active_workers)} threads...")
            for id, worker in self.active_workers.items():
                if self.threadpool.tryTake(worker):
                    self.logger.debug(f"Successfully cancelled worker {id}. Filename = {worker.filename}")
                    self.active_workers.pop(id)
                else:
                    self.logger.debug(f"Unable to cancel worker {id}")
        else:
            self.logger.debug(f"Cancel ignored, no active threads")
    
    # Create a worker object and connect it to this factory
    def createWorker(self,
                     id        : int,
                     filename  : str              = None,
                     parser    : DataFrameParser  = None,
                     df        : pandas.DataFrame = None,
                     operation : str = "read",
                     **kwargs):
        info = QFileInfo(filename) if isinstance(filename, str) else QFileInfo()
        if isinstance(parser, DataFrameParser):
            iterable = (parser.read_iterable and operation == "read") or (parser.write_iterable and operation == "write")
        else:
            iterable = False
        if iterable:
            steps = 20 # Optimal progress amount
            if operation == "read" and info.exists() and info.size() > MIN_PROGRESS_SIZE:
                rowCount  = parser.inferRowCount(filename)
                chunksize = int(rowCount / steps) if rowCount > steps else 1
                kwargs['chunksize'] = chunksize
        elif operation not in ["read", "write"]:
            steps = 2 # 2 steps for merge operations
        else:
            steps = 1
        worker = DataFrameWorker(id=id, parser=parser, operation=operation, filename=filename, steps=steps, df=df, **kwargs)
        worker.signals.started.connect(self.onWorkerStarted)
        worker.signals.progress.connect(self.onWorkerProgress)
        worker.signals.error.connect(self.onWorkerError)
        worker.signals.result.connect(self.onWorkerResultReady)
        worker.signals.finished.connect(self.onWorkerFinished)
        return worker
    
    # Preferred Method for model creation. Uses background threads as needed
    def createModels(self, filenames : typing.List[str], **kwargs) -> bool:
        if isinstance(filenames, list) and len(filenames) > 0 and all(type(f) is str for f in filenames):
            fileInfoList    = [QFileInfo(f) for f in filenames]
            current_workers = list(self.active_workers.keys())
            new_workers     = []
            for i in range(len(fileInfoList)):
                info = fileInfoList[i]
                if info.absoluteFilePath() in self.models.keys():
                    model            = self.models[info.absoluteFilePath()]
                    model.ref_count += 1
                    self.modelCreated.emit(model)
                elif info.exists() and info.isFile():
                    parser                  = self.getParser(info.fileName())
                    id                      = self.numWorkersCreated
                    worker                  = self.createWorker(id=id, parser=parser, filename=info.absoluteFilePath(), **kwargs)
                    self.active_workers[id] = worker
                    new_workers.append(worker)
                    self.numWorkersCreated += 1
                else:
                    self.logger.debug(f"Skipping invalid file: {info.absoluteFilePath()}")

            if len(new_workers) > 0:
                total_steps = sum([w.steps for w in new_workers])
                if len(current_workers) > 0:
                    self.progress_steps += total_steps
                    self.progressUpdate.emit(self.progress_step, self.progress_steps)
                else:
                    self.progress_step  = 0
                    self.progress_steps = total_steps
                    self.active_msg_id  = new_workers[0].id
                    self.progressStarted.emit(self.progress_steps)
                    self.progressMessage.emit(QFileInfo(new_workers[0].filename).fileName())

                for worker in new_workers:
                    self.threadpool.start(worker)
        else:
            self.logger.error(f"Invalid filenames: {filenames}")
        return False
    
    @pyqtSlot(str)
    def onModelClosed(self, filename : str):
        if filename in self.models.keys():
            model            = self.models[filename]
            model.ref_count -= 1
            if (model.ref_count < 1):
                self.models.pop(filename)
                self.logger.debug(f"Freeing memory associated with model: {filename}")
                del model # Free the memory associated with the model
        else:
            self.logger.debug(f"Closed model not present in local storage: {filename}")
    
    def saveModelToFile(self, df : pandas.DataFrame, filename : str, parser : DataFrameParser = None) -> bool:
        if not(isinstance(parser, DataFrameParser)):
            parser = self.getParser(filename)
        if isinstance(parser, DataFrameParser):
            # Create a new DataFrameWorker
            id                      = self.numWorkersCreated
            current_workers         = list(self.active_workers.keys())
            worker                  = self.createWorker(id=id, filename=filename, parser=parser, df=df, operation="write")
            self.active_workers[id] = worker
            self.numWorkersCreated += 1

            # Update the progress bar
            if len(current_workers) > 0:
                self.progress_steps += worker.steps
                self.progressUpdate.emit(self.progress_step, self.progress_steps)
            else:
                self.progress_step  = 1
                self.progress_steps = worker.steps
                self.active_msg_id  = worker.id
                self.progressStarted.emit(self.progress_steps)
                self.progressMessage.emit(f"Writing file {filename}...")

            self.threadpool.start(worker)
            return True
        else:
            self.logger.error(f"Invalid Parser: {parser}")
            return False

    @pyqtSlot(str, str, dict)
    def performMergeOperation(self, title : str, operation : str, kwargs : typing.Dict[str, typing.Any]):
        if isinstance(title, str) and isinstance(operation, str) and isinstance(kwargs, dict) and len(kwargs) > 0:
            
            # Create a new DataFrameWorker
            current_workers         = list(self.active_workers.keys())
            id                      = self.numWorkersCreated
            worker                  = self.createWorker(id=id, filename=title, operation=operation, **kwargs)
            self.active_workers[id] = worker
            self.numWorkersCreated += 1

            # Update the progress bar
            if len(current_workers) > 0:
                self.progress_steps += worker.steps
                self.progressUpdate.emit(self.progress_step, self.progress_steps)
            else:
                self.progress_step  = 1
                self.progress_steps = worker.steps
                self.active_msg_id  = worker.id
                self.progressStarted.emit(self.progress_steps)
                self.progressMessage.emit(f"Creating merged table {title}...")

            self.threadpool.start(worker)
        else:
            self.logger.error(f"Invalid Merge Operation: {title}, {operation}, {kwargs}")

if __name__ == "__main__":

    factory = DataFrameFactory.getInstance()
    if len(sys.argv) > 1:
        # Read in a test file and display the contents
        model = factory.createModel(sys.argv[1])
    else:
        # Display an example model
        x     = numpy.arange(-numpy.pi * 2 , numpy.pi * 2, numpy.pi / 16)
        df    = pandas.DataFrame({"X" : x, "Sin(x)" : numpy.sin(x), "Cos(x)" : numpy.cos(x)})
        model = DataFrameFactory.getInstance().createModel('Example.csv', df) 
    print(model.df)