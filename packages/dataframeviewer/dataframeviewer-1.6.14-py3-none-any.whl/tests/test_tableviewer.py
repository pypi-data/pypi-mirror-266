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

import sys
import numpy
import pandas
import warnings
import unittest
from   unittest.mock   import patch
from   pandas.testing  import assert_series_equal
from   dataframemodel  import DataFrameFactory
from   tableviewer     import TableViewer, create_table
from   PyQt5.QtWidgets import QApplication
from   PyQt5.QtCore    import Qt

# Must construct a QApplication instance before running any unit tests with QWidgets
app = QApplication(sys.argv)

# Ignore QTimer warnings during unit testing
warnings.filterwarnings(action='ignore', message='QBasicTimer::start: QBasicTimer can only be used with threads started with QThread')

class Test_TableViewer(unittest.TestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self.filename = f"unit_test_{self.__class__.__name__}.csv"
        self.df       = pandas.DataFrame({'Ints'    : list(range(4)), 
                                          'Floats'  : list(numpy.arange(-2 * numpy.pi , 2 * numpy.pi, numpy.pi)),
                                          'Strings' : ['Cat', 'Dog', 'Fish', 'Bird']})
        self.factory = DataFrameFactory.getInstance() 
        self.factory.setDefaultParsers()
        self.model = self.factory.createModel(self.filename, self.df)
    
    def test_create_table(self):
        table = create_table(self.model)
        assert(isinstance(table, TableViewer))
        assert(table.model is self.model)
        assert(table.ui.tableView.model() is self.model)
        assert(table.column_model.rowCount() == self.model.columnCount())
    
    def test_hideColumns(self):
        table = create_table(self.model)

        assert(table.ui.tableView.isColumnHidden(0) == False)
        assert(table.ui.tableView.isColumnHidden(1) == False)
        assert(table.ui.tableView.isColumnHidden(2) == False)
        assert(table.ui.columnList.isRowHidden(0) == False)
        assert(table.ui.columnList.isRowHidden(1) == False)
        assert(table.ui.columnList.isRowHidden(2) == False)

        table.hideColumns([1, 2])
        assert(table.ui.tableView.isColumnHidden(0) == False)
        assert(table.ui.tableView.isColumnHidden(1) == True)
        assert(table.ui.tableView.isColumnHidden(2) == True)
        assert(table.ui.columnList.isRowHidden(0) == False)
        assert(table.ui.columnList.isRowHidden(1) == False)
        assert(table.ui.columnList.isRowHidden(2) == False)

        # The "Show Unchecked Columns checkbox" should affect
        # the columnList rows but not the tableView columns 
        table.ui.showUncheckedCheckBox.setChecked(False)
        assert(table.ui.tableView.isColumnHidden(0) == False)
        assert(table.ui.tableView.isColumnHidden(1) == True)
        assert(table.ui.tableView.isColumnHidden(2) == True)
        assert(table.ui.columnList.isRowHidden(0) == False)
        assert(table.ui.columnList.isRowHidden(1) == True)
        assert(table.ui.columnList.isRowHidden(2) == True)

        table.showColumns([1])
        assert(table.ui.tableView.isColumnHidden(0) == False)
        assert(table.ui.tableView.isColumnHidden(1) == False)
        assert(table.ui.tableView.isColumnHidden(2) == True)
        assert(table.ui.columnList.isRowHidden(0) == False)
        assert(table.ui.columnList.isRowHidden(1) == False)
        assert(table.ui.columnList.isRowHidden(2) == True)

        table.hideColumns([0])
        assert(table.ui.tableView.isColumnHidden(0) == False)
        assert(table.ui.tableView.isColumnHidden(1) == False)
        assert(table.ui.tableView.isColumnHidden(2) == True)
        assert(table.ui.columnList.isRowHidden(0) == False)
        assert(table.ui.columnList.isRowHidden(1) == False)
        assert(table.ui.columnList.isRowHidden(2) == True)

        table.ui.showUncheckedCheckBox.setChecked(True)
        assert(table.ui.tableView.isColumnHidden(0) == False)
        assert(table.ui.tableView.isColumnHidden(1) == False)
        assert(table.ui.tableView.isColumnHidden(2) == True)
        assert(table.ui.columnList.isRowHidden(0) == False)
        assert(table.ui.columnList.isRowHidden(1) == False)
        assert(table.ui.columnList.isRowHidden(2) == False)

    def test_hideOtherColumns(self):
        table = create_table(self.model)

        assert(table.ui.tableView.isColumnHidden(0) == False)
        assert(table.ui.tableView.isColumnHidden(1) == False)
        assert(table.ui.tableView.isColumnHidden(2) == False)

        table.hideOtherColumns([0, 2])
        assert(table.ui.tableView.isColumnHidden(0) == False)
        assert(table.ui.tableView.isColumnHidden(1) == True)
        assert(table.ui.tableView.isColumnHidden(2) == False)

    # Test the plotColumns method
    def test_plotColumns(self):
        with patch.object(self.model, 'plotColumns') as plotColumns_mock:
            table = create_table(self.model)
            table.plotColumns()
            plotColumns_mock.assert_called_once_with(None, [])

            table.plotColumns(['Strings'])
            plotColumns_mock.assert_called_with(None, ['Strings'])

            table.ui.xAxisCheckBox.setChecked(True)
            table.plotColumns(['Floats', 'Strings'])
            plotColumns_mock.assert_called_with('Floats', ['Strings'])

            table.ui.tableView.selectColumn(0)
            table.plotColumns()
            plotColumns_mock.assert_called_with(None, ['Ints'])
            assert(plotColumns_mock.call_count == 4)

    # Test the applyFormula method
    def test_applyFormula(self):
        table = create_table(self.model)

        assert(table.model.df.loc[0, 'Strings'] == 'Cat' )
        assert(table.model.df.loc[1, 'Strings'] == 'Dog' )
        assert(table.model.df.loc[2, 'Strings'] == 'Fish')
        assert(table.model.df.loc[3, 'Strings'] == 'Bird')

        assert(table.applyFormula(2, 'Ints * 2 + 1') == True)
        assert(table.model.df.loc[0, 'Strings'] == 1)
        assert(table.model.df.loc[1, 'Strings'] == 3)
        assert(table.model.df.loc[2, 'Strings'] == 5)
        assert(table.model.df.loc[3, 'Strings'] == 7)

    # Test the copyColumns method
    def test_copyColumns(self):
        table = create_table(self.model)

        # Ensure copyColumns only allowed when editable
        assert(list(table.model.df.columns) == ['Ints', 'Floats', 'Strings'])
        assert(table.copyColumns(['Ints', 'Strings'], 1) == False)
        assert(list(table.model.df.columns) == ['Ints', 'Floats', 'Strings'])

        # Now actually copy the columns
        table.setEditable(True)
        assert(table.copyColumns(['Ints', 'Strings'], 1) == True)
        assert(list(table.model.df.columns) == ['Ints', 'Floats', 'Ints_copy', 'Strings_copy', 'Strings'])
        assert_series_equal(table.model.df['Ints']   , table.model.df['Ints_copy'], check_names=False)
        assert_series_equal(table.model.df['Strings'], table.model.df['Strings_copy'], check_names=False)

    # Test the insertColumn method
    def test_insertColumn(self):
        table = create_table(self.model)

        # Ensure insertColumn only allowed when editable
        assert(list(table.model.df.columns) == ['Ints', 'Floats', 'Strings'])
        assert(table.insertColumn("Test_Column", index=1) is None)
        assert(list(table.model.df.columns) == ['Ints', 'Floats', 'Strings'])

        # Now actually insert the column
        table.setEditable(True)
        assert(table.insertColumn("Test_Column") == 3)
        assert(list(table.model.df.columns) == ['Ints', 'Floats', 'Strings', 'Test_Column'])
        assert_series_equal(table.model.df['Test_Column'], pandas.Series([''] * 4), check_names=False)

    # Test the editCell method
    def test_editCell(self):
        table = create_table(self.model)

        # Ensure editCell only allowed when editable
        assert(table.model.df.loc[1, 'Strings'] == 'Dog')
        assert(table.editCell(1, 'Strings', 'Elephant', Qt.EditRole) == False)
        assert(table.model.df.loc[1, 'Strings'] == 'Dog')

        # Now actually edit the cell
        table.setEditable(True)
        assert(table.editCell(1, 'Strings', 'Elephant', Qt.EditRole) == True)
        assert(table.model.df.loc[1, 'Strings'] == 'Elephant')

    # Test the deleteColumns method
    def test_deleteColumns(self):
        table = create_table(self.model)

        # Ensure deleteColumns only allowed when editable
        assert(list(table.model.df.columns) == ['Ints', 'Floats', 'Strings'])
        assert(table.model.df.shape == (4, 3))
        assert(table.deleteColumns(['Floats', 'Strings'], ask=False) == False)
        assert(list(table.model.df.columns) == ['Ints', 'Floats', 'Strings'])
        assert(table.model.df.shape == (4, 3))

        # Now actually delete the columns
        table.setEditable(True)
        assert(table.deleteColumns(['Floats', 'Strings'], ask=False) == True)
        assert(list(table.model.df.columns) == ['Ints'])
        assert(table.model.df.shape == (4, 1))

    # Test the renameColumn method
    def test_renameColumn(self):
        table = create_table(self.model)

        # Test renaming a column
        assert(list(table.model.df.columns) == ['Ints', 'Floats', 'Strings'])
        assert(table.renameColumn('Floats', 'New_Column_Name') == True)
        assert(list(table.model.df.columns) == ['Ints', 'New_Column_Name', 'Strings'])

if __name__ == "__main__":
    unittest.main()
