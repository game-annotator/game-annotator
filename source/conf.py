import os
import sys
sys.path.insert(0, os.path.abspath('..'))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_annotator.settings')
django.setup()

# -- Project information -----------------------------------------------------

project = 'GameAnnotator'
copyright = '2026, Pankaj Kumar G, Arun Kumar M N, Anitha M L'
author = 'Pankaj Kumar G, Arun Kumar M N, Anitha M L'
release = '1.0.0'
version = '1.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

templates_path = []
exclude_patterns = ['_build']

# -- Autodoc settings --------------------------------------------------------

autodoc_member_order = 'bysource'
autodoc_default_options = {
    'members': True,
    'undoc-members': False,
    'show-inheritance': True,
    'special-members': '__str__',
}
add_module_names = False

# -- Napoleon (Google-style docstrings) --------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_use_rtype = True

# -- Intersphinx: cross-links to Django and Python docs ----------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'django': ('https://docs.djangoproject.com/en/stable/', 'https://docs.djangoproject.com/en/stable/_objects/'),
}

# -- HTML output -------------------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = []
html_show_sphinx = False
html_theme_options = {
    'navigation_depth': 3,
    'titles_only': False,
}
