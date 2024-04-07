import os
import sys
import glob
from   os.path import dirname, basename, isfile, join

# Update PYTHONPATH
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.join(current_path, "ui"))
sys.path.append(os.path.join(current_path, "ui", "images"))

# Import main function
from .dataviewer import main

# Import all .py files in this directory
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]