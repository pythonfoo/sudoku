# Configuration file for the Sphinx documentation builder.
#
# Full list of options can be found in the Sphinx documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

#
# -- Project information -----------------------------------------------------
#

project = "Sudoku"
copyright = ""
author = "Olaf Gladis"

#
# -- General configuration ---------------------------------------------------
#

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    # "sphinx.ext.mathjax",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "myst_parser",
    # "sphinx_inline_tabs",
]
templates_path = ["_templates"]

#
# -- Options for extlinks ----------------------------------------------------
#
extlinks = {
    "pypi": ("https://pypi.org/project/%s/", ""),
}

#
# -- Options for intersphinx -------------------------------------------------
#
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/", None),
}

#
# -- Options for TODOs -------------------------------------------------------
#
todo_include_todos = True

#
# -- Options for Markdown files ----------------------------------------------
#
myst_admonition_enable = True
myst_deflist_enable = True
myst_heading_anchors = 3

#
# -- Options for HTML output -------------------------------------------------
#

html_theme = "furo"
html_title = "Sudoku"

html_static_path = ["_static"]
html_theme_options = {
    "announcement": (
        "Sudoku is under active development, and this documentation is not written yet!"
    ),
}
# import myst_parser


# def docstring(app, what, name, obj, options, lines):
#     md = "\n".join(lines)
#     ast = commonmark.Parser().parse(md)
#     rst = commonmark.ReStructuredTextRenderer().render(ast)
#     lines.clear()
#     lines += rst.splitlines()


# def setup(app):
#     app.connect("autodoc-process-docstring", docstring)
