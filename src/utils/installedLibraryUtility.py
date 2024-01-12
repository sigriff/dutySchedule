"""
This module is a utility to show which python libraries have been installed for a virtual environment

The import statements show that the listed libraries are installed and are accessible. The remainder of the code will print which VS Code
interpreter is being used and then lists all the installed libraries and versions

Author: Simon Griffiths
Date: 16-Nov-2023
License: n/a
Dependencies: n/a
Example usage: Just run the module
Version: 1.0.0
"""
import subprocess
import sys
import numpy as np
import pandas as pd
import scipy
import statsmodels
import sklearn #scikit-learn
import matplotlib
import seaborn
import bokeh
import sqlalchemy
import unittest
import pulp

def main() -> None:

    # get the current python interpreter path
    interpreter_path = sys.executable

    # run the pip list command and capture the output
    installed_libraries = subprocess.run(['pip', 'list'], stdout=subprocess.PIPE).stdout.decode('utf-8')

    # print the libraries
    print(f"\npython interpreter: {interpreter_path}")
    print(f"python: {sys.version}")
    print("\nThe following libraries are installed:")
    print(installed_libraries)

if __name__ == "__main__":
    main()