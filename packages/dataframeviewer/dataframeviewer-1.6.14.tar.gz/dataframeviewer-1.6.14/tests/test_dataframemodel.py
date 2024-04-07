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

import os
import numpy
import pandas
import typing
import datetime
import unittest
import contextlib
from   pandas.testing import assert_frame_equal
from   dataframemodel import DataFrameModel, DataFrameFactory, ColorRule
from   PyQt5.QtCore   import Qt
from   PyQt5.QtGui    import QColor

# Simple context manager to write a dataframe to a temporary file
class DataFrameTempFile(contextlib.AbstractContextManager):

    def __init__(self, df : pandas.DataFrame, filename : str) -> None:
        super().__init__()
        self.df       = df
        self.filename = filename

    def __enter__(self):
        self.df.to_csv(self.filename, index=False)
        self.file = open(self.filename)
        return self
    
    def __exit__(self, __exc_type,  __exc_value,  __traceback):
        self.file.close()
        os.remove(self.filename)
        return super().__exit__(__exc_type, __exc_value, __traceback)

class Test_DataFrameModel(unittest.TestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self.filename      = f".tmp_{self.__class__.__name__}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.fake_filename = "Not a real file"
        self.df = pandas.DataFrame({'Ints'    : list(range(4)), 
                                    'Floats'  : list(numpy.arange(-2 * numpy.pi , 2 * numpy.pi, numpy.pi)),
                                    'Strings' : ['Cat', 'Dog', 'Fish', 'Bird']})
        self.factory = DataFrameFactory.getInstance() 
        self.factory.setDefaultParsers()

    def test_dataframefactory(self):
        # Test Singleton Factory instance
        factory2 = DataFrameFactory.getInstance() 
        assert(self.factory is factory2)

        # Test Empty Model Creation
        empty_df = pandas.DataFrame()
        model    = self.factory.createModel(filename=self.fake_filename, df=empty_df)
        assert(isinstance(model, DataFrameModel))
        assert_frame_equal(empty_df, model.df)

        # Test Normal Model Creation
        with DataFrameTempFile(self.df, self.filename) as tmp:
            model_from_file = self.factory.createModel(tmp.filename)
            model_from_df   = self.factory.createModel(self.fake_filename, tmp.df)
            assert(isinstance(model_from_file, DataFrameModel))
            assert(isinstance(model_from_df  , DataFrameModel))
            assert(model_from_file.filename == tmp.filename)
            assert(model_from_df.filename == self.fake_filename)
            assert_frame_equal(model_from_file.df, model_from_df.df)

    def test_dataframemodel(self):
        model = self.factory.createModel(self.fake_filename, self.df)

        # Test expected model accessors
        assert(model.rowCount()    == 4)
        assert(model.columnCount() == 3)

        for row in range(self.df.shape[0]):
            assert(model.headerData(row, Qt.Vertical, Qt.DisplayRole) == str(row))

        for col in range(self.df.shape[1]):
            assert(model.headerData(col, Qt.Horizontal, Qt.DisplayRole) == self.df.columns[col])

        for i, row in self.df.iterrows():
            for col in range(len(row)):
                index = model.index(i, col)   
                assert(model.data(index) == row[col])
    
    def test_color_rules(self):
        model = self.factory.createModel(self.fake_filename, self.df)
        model.addColorRule('Ints'   , ColorRule(condition='x % 2 == 0', color=QColor('lime')))
        model.addColorRule('Floats' , ColorRule(condition='-4 < x < 4', color=QColor('lime')))
        model.addColorRule('Floats' , ColorRule(condition='abs(x) > 4'  , color=QColor('yellow')))
        model.addColorRule('Floats' , ColorRule(condition='abs(x) < 0.5', color=QColor('red')))
        model.addColorRule('Strings', ColorRule(condition='str(x) == "Dog"', color=QColor('lime')))
        model.addColorRule('Strings', ColorRule(condition='re.search("fish|bird", str(x), re.IGNORECASE)' , color=QColor('red')))
        
        # Check if color rules are applied as expected
        assert(model.data(model.index(0, 0), Qt.BackgroundColorRole) == QColor('lime'))
        assert(model.data(model.index(1, 0), Qt.BackgroundColorRole) == None)
        assert(model.data(model.index(2, 0), Qt.BackgroundColorRole) == QColor('lime'))
        assert(model.data(model.index(3, 0), Qt.BackgroundColorRole) == None)

        assert(model.data(model.index(0, 1), Qt.BackgroundColorRole) == QColor('yellow'))
        assert(model.data(model.index(1, 1), Qt.BackgroundColorRole) == QColor('lime'))
        assert(model.data(model.index(2, 1), Qt.BackgroundColorRole) == QColor('red'))
        assert(model.data(model.index(3, 1), Qt.BackgroundColorRole) == QColor('lime'))

        assert(model.data(model.index(0, 2), Qt.BackgroundColorRole) == None)
        assert(model.data(model.index(1, 2), Qt.BackgroundColorRole) == QColor('lime'))
        assert(model.data(model.index(2, 2), Qt.BackgroundColorRole) == QColor('red'))
        assert(model.data(model.index(3, 2), Qt.BackgroundColorRole) == QColor('red'))

    def test_set_data(self):
        model = self.factory.createModel(self.fake_filename, self.df)

        def assert_set_data(row : int, col : int, value : typing.Any, expected : typing.Any):
            index = model.index(row, col)
            model.setData(index, value)
            assert(model.data(index) == expected)

        # String Data Type Conversion should occur only when possible
        assert_set_data(0, 0,          7,          7)
        assert_set_data(1, 0,       24.5,       24.5)
        assert_set_data(2, 0,       '43',         43)
        assert_set_data(3, 0, 'A String', 'A String')
        assert_set_data(0, 1,       76.9,       76.9)
        assert_set_data(0, 1,     '56.4',       56.4)
        assert_set_data(0, 2,       98.6,     '98.6')
        assert_set_data(1, 2,    'Apple',    'Apple')

        assert(model.headerData(2, Qt.Horizontal, Qt.DisplayRole) == "Strings")
        model.setHeaderData(2, Qt.Horizontal, "New Header")
        assert(model.headerData(2, Qt.Horizontal, Qt.DisplayRole) == "New Header")

if __name__ == "__main__":
    unittest.main()
