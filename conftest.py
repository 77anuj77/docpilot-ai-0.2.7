import os
import sys

# Allow tests to import the package directly from src/ when it is not installed.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
