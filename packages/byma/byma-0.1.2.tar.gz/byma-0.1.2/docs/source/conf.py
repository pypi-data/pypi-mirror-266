# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import pathlib
import sys
import os
import re
import importlib
from docutils import nodes
from recommonmark.parser import CommonMarkParser


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ByMa'
copyright = '2024, Lorenzo Zambelli'
author = 'Lorenzo Zambelli'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sys.path.insert(0, os.path.abspath('../sphinxext'))

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.apidoc',
    'autoapi.extension',
    'sphinx.ext.todo',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.graphviz',
    'sphinx.ext.ifconfig',
    'matplotlib.sphinxext.plot_directive',
    'sphinx.ext.mathjax',
    'sphinx_design',
]

source_parsers = {
    '.md': CommonMarkParser,
}

source_suffix = ['.rst', '.md']

# The default replacements for |version| and |release|, also used in various
# other places throughout the built documents.
#

import byma
import byma.nuby

# The short X.Y version (including .devXXXX, rcX, b1 suffixes if present)
# version = re.sub(r'(\d+\.\d+)\.\d+(.*)', r'\1\2', byma.__version__)
version = re.sub(r'(\d+\.\d+\.\d+).*', r'\1', byma.__version__)
# version = re.sub(r'(\.dev\d+).*?$', r'\1', version)
# The full version, including alpha/beta/rc tags.
release = byma.__version__
print("%s %s" % (version, release))

# Else, today_fmt is used as the format for a strftime call.
today_fmt = '%B %d, %Y'

# The reST default role (used for this markup: `text`) to use for all documents.
default_role = "autolink"

autoapi_dirs = [
    "../../byma",
    "../../byma/nuby",
    "../../byma/interface",
    "../../byma/iteral",
    "../../byma/pyplot"
]
autoapi_type = "python"
autoapi_template_dir = "_templates/autoapi"
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]
autoapi_keep_files = True
autodoc_typehints = "signature"
templates_path = ['_templates']
exclude_patterns = []

# -----------------------------------------------------------------------------
# Autosummary
# -----------------------------------------------------------------------------

autosummary_generate = True



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Set up the version switcher.  The versions.json is stored in the doc repo.
if os.environ.get('CIRCLE_JOB', False) and \
        os.environ.get('CIRCLE_BRANCH', '') != 'main':
    # For PR, name is set to its ref
    switcher_version = os.environ['CIRCLE_BRANCH']
elif ".dev" in version:
    switcher_version = "devdocs"
else:
    switcher_version = f"{version}"

html_theme_options = {
#   "logo": {
#       "image_light": "_static/",
#       "image_dark": "_static/",
#   },
  "github_url": "https://gitlab.com/ByteMath/python/ByMa",
  "collapse_navigation": True,
  # Add light/dark mode and documentation version switcher:
}
html_title = "%s v%s Manual" % (project, version)
html_last_updated_fmt = '%b %d, %Y'
# html_css_files = [".css"]
html_context = {"default_mode": "light"}
html_use_modindex = True
html_copy_source = False
html_domain_indices = False
html_file_suffix = '.html'



