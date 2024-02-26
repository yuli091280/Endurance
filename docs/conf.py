import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

project = "Race Walking Visualization"
extensions = ["sphinx.ext.autodoc"]
html_theme = "alabaster"
master_doc = "index"
