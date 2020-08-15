# -*- coding: utf-8 -*-
#
# scikit-learn documentation build configuration file, created by
# sphinx-quickstart on Fri Jan  8 09:13:42 2010.
#
# This file is execfile()d with the current directory set to its containing
# dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

from __future__ import print_function
import sys
import os
import warnings

# If extensions (or modules to document with autodoc) are in another
# directory, add these directories to sys.path here. If the directory
# is relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
sys.path.insert(0, os.path.abspath('sphinxext'))

from github_link import make_linkcode_resolve
import sphinx_gallery
import chainladder as cl


class Mock(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return Mock()

    @classmethod
    def __getattr__(cls, name):
        if name in ('__file__', '__path__'):
            return '/dev/null'
        elif name[0] == name[0].upper():
            return type(name, (), {})
        else:
            return Mock()

if os.name != 'nt':
    MOCK_MODULES = ['numpy', 'scipy', 'pandas', 'bokeh', 'sklearn', 'matplotlib.pyplot', 'sparse', 'numba']
    for mod_name in MOCK_MODULES:
        sys.modules[mod_name] = Mock()


# this is needed for some reason...
# see https://github.com/numpy/numpydoc/issues/69
# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
if os.name == 'nt':
    extensions = ['sphinx.ext.autodoc', 'numpydoc', 'sphinx_gallery.gen_gallery',
                  'sphinx.ext.githubpages', 'nbsphinx', 'sphinx.ext.mathjax',
                  'sphinx.ext.autosummary', 'sphinx_gallery.load_style']

else:
    extensions = ['sphinx.ext.autodoc', 'numpydoc', 'nbsphinx',
                  'sphinx.ext.mathjax', 'sphinx.ext.autosummary',
                  'sphinx_gallery.load_style']
numpydoc_class_members_toctree = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']


# this is needed for some reason...
# see https://github.com/numpy/numpydoc/issues/69
numpydoc_class_members_toctree = False


# For maths, use mathjax by default and svg if NO_MATHJAX env variable is set
# (useful for viewing the doc offline)
if os.environ.get('NO_MATHJAX'):
    extensions.append('sphinx.ext.imgmath')
    imgmath_image_format = 'svg'
else:
    extensions.append('sphinx.ext.mathjax')
    mathjax_path = ('https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/'
                    'MathJax.js?config=TeX-AMS_SVG')


autodoc_default_flags = ['members', 'inherited-members']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['templates']

# generate autosummary even if no references
autosummary_generate = True

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'ChainLadder'
copyright = '2017, John Bogaardt'
author = 'John Bogaardt'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.

version = cl.__version__
# The full version, including alpha/beta/rc tags.
release = cl.__version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
#language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'templates', 'includes', 'themes', '**.ipynb_checkpoints']
# The reST default role (used for this markup: `text`) to use for all
# documents.
default_role = 'any'

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'scikit-learn'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {'oldversion': False, 'collapsiblesidebar': True,
                      'google_analytics': False, 'surveybanner': False,
                      'sprintbanner': False}

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = ['themes']

# A shorter title for the navigation bar.  Default is the same as html_title.
html_short_title = 'chainladder'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['images']

# -- Options for HTMLHelp output ------------------------------------------
# If false, no module index is generated.
html_domain_indices = False

# If false, no index is generated.
html_use_index = False

# Output file base name for HTML help builder.
htmlhelp_basename = 'chainladderdoc'


# -- Options for LaTeX output ------------------------------------------------
latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    'preamble': r"""
        \usepackage{amsmath}\usepackage{amsfonts}\usepackage{bm}
        \usepackage{morefloats}\usepackage{enumitem} \setlistdepth{10}
        """
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto/manual]).
latex_documents = [('index', 'user_guide.tex', 'scikit-learn user guide',
                    'scikit-learn developers', 'manual'), ]

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
latex_domain_indices = False

trim_doctests_flags = True

# intersphinx configuration
intersphinx_mapping = {
    'python': ('https://docs.python.org/{.major}'.format(
        sys.version_info), None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/reference', None),
    'matplotlib': ('https://matplotlib.org/', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
    'joblib': ('https://joblib.readthedocs.io/en/latest/', None),
}


sphinx_gallery_conf = {
    'doc_module': 'chainladder',
    'backreferences_dir': os.path.join('modules', 'generated'),
    'reference_url': {'chainladder': None}
}

# The following dictionary contains the information used to create the
# thumbnails for the front page of the scikit-learn home page.
# key: first image in set
# values: (number of plot in set, height of thumbnail)
carousel_thumbs = {'sphx_glr_plot_classifier_comparison_001.png': 600,
                   'sphx_glr_plot_anomaly_comparison_001.png': 372,
                   'sphx_glr_plot_gpr_co2_001.png': 350,
                   'sphx_glr_plot_adaboost_twoclass_001.png': 372,
                   'sphx_glr_plot_compare_methods_001.png': 349}


def make_carousel_thumbs(app, exception):
    """produces the final resized carousel images"""
    if exception is not None:
        return
    print('Preparing carousel images')

    image_dir = os.path.join(app.builder.outdir, '_images')
    for glr_plot, max_width in carousel_thumbs.items():
        image = os.path.join(image_dir, glr_plot)
        if os.path.exists(image):
            c_thumb = os.path.join(image_dir, glr_plot[:-4] + '_carousel.png')
            sphinx_gallery.gen_rst.scale_image(image, c_thumb, max_width, 190)

# Config for sphinx_issues

issues_uri = 'https://github.com/casact/chainladder-python/issues/{issue}'
issues_github_path = 'chainladder-python/chainladder'
issues_user_uri = 'https://github.com/{user}'


def setup(app):
    # to hide/show the prompt in code examples:
    app.add_javascript('js/copybutton.js')
    app.add_javascript('js/extra.js')
    app.connect('build-finished', make_carousel_thumbs)


# The following is used by sphinx.ext.linkcode to provide links to github
linkcode_resolve = make_linkcode_resolve('chainladder',
                                         u'https://github.com/casact/'
                                         'chainladder-python/blob/{revision}/'
                                         '{package}/{path}#L{lineno}')

warnings.filterwarnings("ignore", category=UserWarning,
                        module="matplotlib",
                        message='Matplotlib is currently using agg, which is a'
                                ' non-GUI backend, so cannot show the figure.')
