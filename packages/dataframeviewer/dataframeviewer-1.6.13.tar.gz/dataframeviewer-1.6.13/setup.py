#!/usr/bin/python

import os
from setuptools import setup, find_packages
from dataframeviewer.dataviewer import APPLICATION_VERSION

MODULE_NAME  = 'dataframeviewer'
FOLDER_NAME  = MODULE_NAME
VERSION      = APPLICATION_VERSION
DESCRIPTION  = 'PyQt5 application to visualize pandas DataFrames'

with open("README.rst", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

# Setting up
setup(
    # The name must match the folder name in the same directory
    name=MODULE_NAME, 
    folder=FOLDER_NAME,
    version=VERSION,
    author="Rafael Arvelo",
    author_email="rafaelarvelo1@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_descripion_content_type="text/x-rst",
    packages=find_packages() +
                [os.path.join(FOLDER_NAME, p) for p in find_packages(where=FOLDER_NAME)],
    package_data={"dataframeviewer" : ["data/example.csv",
                                       "data/stocks/FB.csv",
                                       "data/stocks/GOOG.csv",
                                       "dataframeviewer/docs/user_manual.pdf",
                                       "ui/images/app_icon.png",
                                       "table_settings/examples/stock_settings.json"]},
    install_requires=['pandas', 'numpy', 'PyQt5', 'openpyxl', 'matplotlib', 'qdarkstyle'],
    entry_points={'console_scripts' : ['dataframeviewer=dataframeviewer.dataviewer:main']},
    python_requires='>=3.6',
    classifiers= [
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
