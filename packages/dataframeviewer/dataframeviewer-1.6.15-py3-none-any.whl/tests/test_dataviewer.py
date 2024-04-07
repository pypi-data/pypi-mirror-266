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
import typing
import unittest
import warnings
from   unittest.mock              import patch, call, Mock
import dataframeviewer
from   dataframeviewer.dataviewer import DataViewer, DataViewerApplication
from   tableviewer                import create_table
from   PyQt5.QtWidgets            import QApplication
from   types                      import SimpleNamespace

# Must construct a QApplication instance before running any unit tests with QWidgets
app = QApplication(sys.argv)

# Ignore QTimer warnings during unit testing
warnings.filterwarnings(action='ignore', message='QBasicTimer::start: QBasicTimer can only be used with threads started with QThread')

class Test_DataViewer(unittest.TestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        self.log_filename = f".log_{__class__.__name__}.txt"

    # Return a namespace to emulate command line arguments
    def create_command_line_args(self, **kwargs) -> SimpleNamespace:
        def set_default(key : str, value : typing.Any):
            if not(key) in kwargs.keys():
                kwargs[key] = value
        
        set_default('filename'      , [])
        set_default('filenames'     , [])
        set_default('settings'      , [])
        set_default('plot'          , [])
        set_default('directory'     , "")
        set_default('log_filename'  , self.log_filename)
        set_default('no_gui'        , False)
        set_default('enable_regex'  , False)
        set_default('join_plots'    , False)
        set_default('quiet'         , False)
        set_default('verbose'       , False)

        return SimpleNamespace(**kwargs)
        
    def test_openDir(self):
        dataviewer = DataViewer()
        with patch.object(dataviewer, 'fsModel') as mock_fs_model:
            dataviewer.openDir('A_Directory')
            mock_fs_model.setRootPath.assert_called_with('A_Directory')

    def test_openFiles(self):
        dataviewer = DataViewer()
        with patch.object(dataviewer, 'factory') as mock_factory:
            dataviewer.openFiles(['File_1', 'File_2'])
            mock_factory.createModels.assert_called_with(['File_1', 'File_2'])

    # Disable logging while testing the command line
    @patch('logging.getLogger')
    @patch('logging.FileHandler')
    @patch('logging.StreamHandler')
    @patch('dataviewerutils.QLogger')
    def test_runCommandLine(self, *mocks):
        dv_app = DataViewerApplication()
        with patch.object(dv_app, 'factory') as mock_factory, patch.object(dataframeviewer.dataviewer, 'plt') as mock_plt:
            mock_model = Mock()
            mock_model.plotColumns.return_value   = True
            mock_factory.createModel.return_value = mock_model
            ret_code = dv_app.runCommandLine(args=self.create_command_line_args(filename=[['Test']], 
                                                                                plot=[['Plot']]))
            assert(ret_code == 0)
            mock_factory.createModel.assert_called_once_with('Test')
            mock_model.plotColumns.assert_called_once_with(x=None, y=['Plot'], interactive=False)
            mock_plt.show.assert_called_once()

            ret_code = dv_app.runCommandLine(args=self.create_command_line_args(filename=[['Test_1'], ['Test_2']], 
                                                                                filenames=[['Test_3', 'Test_4'], ['Test_5']], 
                                                                                plot=[['Plot_1'], ['Plot_2', 'Plot_3']]))
            assert(ret_code == 0)
            assert(mock_factory.createModel.call_count == 6)
            assert(mock_factory.createModel.call_args_list[1] == call('Test_1'))
            assert(mock_factory.createModel.call_args_list[2] == call('Test_2'))
            assert(mock_factory.createModel.call_args_list[3] == call('Test_3'))
            assert(mock_factory.createModel.call_args_list[4] == call('Test_4'))
            assert(mock_factory.createModel.call_args_list[5] == call('Test_5'))
            assert(mock_model.plotColumns.call_count == 11)
            assert(mock_plt.show.call_count == 2)

if __name__ == "__main__":
    unittest.main()
