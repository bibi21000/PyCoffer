# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from sphinx_pyproject import SphinxConfig

import sys
from pathlib import Path

sys.path.insert(0, str(Path('..', 'pycoffer').resolve()))

config = SphinxConfig("../pyproject.toml", globalns=globals())

project = 'PyCoffer'
# ~ author = config["authors"]
author = 'bibi21000 aka Sébastien GALLET'
# ~ author = 'bibi21000'
# ~ copyright = '2025, %s' % author
# ~ release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = config["extensions"]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

