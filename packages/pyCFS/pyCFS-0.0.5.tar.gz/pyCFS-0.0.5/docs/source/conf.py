# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import pyCFS

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = pyCFS.__name__
copyright = "2024, Verein zur Förderung der Software openCFS"
author = " and ".join(pyCFS.__author__)
release = pyCFS.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = []

myst_enable_extensions = ["colon_fence", "dollarmath", "amsmath"]
myst_heading_anchors = 3
myst_dmath_allow_labels = True
myst_dmath_double_inline = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_logo = "./_static/pycfslogo-full-no-text.png"
html_favicon = "./_static/pycfslogo-full-no-text-small.png"
html_title = ""

html_theme_options = {
    "logo": {
        "text": f"pyCFS {release}",
        "image_light": html_logo,
        "image_dark": html_logo,
    },
    "icon_links": [
        {
            "name": "GitLab",
            "url": "https://gitlab.com/openCFS/pycfs",
            "icon": "fa-brands fa-square-gitlab",
            "type": "fontawesome",
        },
        {
            "name": "Home",
            "url": "https://opencfs.org/",
            "icon": "fa-solid fa-house",
            "type": "fontawesome",
        },
    ],
}

# suppress errors :
suppress_warnings = ["myst.header"]
