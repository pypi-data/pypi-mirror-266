# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
import os
sys.path.append(os.path.join('..','src'))
sys.path.append(os.path.join('..'))

import pytomlpp
f = os.path.realpath(os.path.join(__file__,'..','..','..',"pyproject.toml"))
details = pytomlpp.load(f)


# project = 'RegexRiot'
project = details['project']['name']
copyright = '2024, Rahul Kandekar'
author = 'Rahul Kandekar'
# import re
# with(open(os.path.realpath(os.path.join(__file__,'..','..','..',"pyproject.toml")), 'r')) as f:
#     for ln in f.readlines():
#         if re.match(r'^version.*(\d+\.\d+\.\d+).*', ln):
#             match = re.match(r'^version.*(\d+\.\d+\.\d+).*', ln)
#             break
release = details['project']['version']

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'furo'
# html_theme = 'sphinx_rtd_theme'
html_theme = 'furo'
html_static_path = ['_static']
