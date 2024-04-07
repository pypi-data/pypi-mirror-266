import os
import sys

# Update PYTHONPATH
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from dataviewer import main

# Execute the application
main(sys.argv[1:])