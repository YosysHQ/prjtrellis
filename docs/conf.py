# -*- coding: utf-8 -*-
#
# Updated documentation of the configuration options is available at
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from re import sub as re_sub
from os import environ, popen, path as os_path
from sys import path as sys_path

sys_path.insert(0, os_path.abspath('.'))

from markdown_code_symlinks import MarkdownCodeSymlinks

# -- General configuration ------------------------------------------------

project = 'Project Trellis'
author = 'Project Trellis Authors'
copyright = f'2018, {author}'

extensions = [
    'sphinx.ext.imgmath', 'sphinx.ext.autodoc', 'sphinx.ext.doctest',
    'sphinx.ext.autosummary', 'sphinx.ext.napoleon', 'sphinx.ext.todo',
    'recommonmark'
]

templates_path = ['_templates']

source_suffix = ['.rst', '.md']
source_parsers = {
    '.md': 'recommonmark.parser.CommonMarkParser',
}

master_doc = 'index'

release = re_sub('^v', '', popen('git describe ').read().strip())
version = release

language = None

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

pygments_style = 'sphinx'

todo_include_todos = True

# -- Options for HTML output ----------------------------------------------

html_theme = 'sphinx_rtd_theme'

on_rtd = environ.get('READTHEDOCS', None) == 'True'
if not on_rtd:
    html_context = {
        "display_github": True,  # Integrate GitHub
        "github_user": "symbiflow",  # Username
        "github_repo": "prjtrellis",  # Repo name
        "github_version": "master",  # Version
        "conf_py_path": "/doc/",
    }

html_static_path = ['_static']

html_sidebars = {
    '**': [
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
    ]
}

# -- Options for HTMLHelp output ------------------------------------------

htmlhelp_basename = 'prjtrellis'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {}

latex_documents = [
    (
        master_doc, 'ProjectTrellis.tex', u'Project Trellis Documentation',
        u'SymbiFlow Team', 'manual'),
]

# -- Options for manual page output ---------------------------------------

man_pages = [
    (master_doc, 'projecttrellis', u'Project Trellis Documentation', [author], 1)
]

# -- Options for Texinfo output -------------------------------------------

texinfo_documents = [
    (
        master_doc, 'ProjectTrellis', u'Project Trellis Documentation', author,
        'ProjectTrellis', 'One line description of project.', 'Miscellaneous'),
]

intersphinx_mapping = {'https://docs.python.org/': None}


def setup(app):
    MarkdownCodeSymlinks.find_links()
    app.add_config_value(
        'recommonmark_config', {
            'github_code_repo': 'https://github.com/SymbiFlow/prjtrellis',
        }, True)
    app.add_transform(MarkdownCodeSymlinks)
