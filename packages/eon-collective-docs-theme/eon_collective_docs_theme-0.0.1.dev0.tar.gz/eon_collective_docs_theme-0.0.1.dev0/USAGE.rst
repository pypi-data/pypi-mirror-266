=====
Usage
=====

How to use the "Eon Collective Documentation theme"

Manually specify the name of the theme in 2 sections of the ``conf.py`` file of a Sphinx project. For example:

.. code-block:: python

   # include the theme in the list of extensions to be loaded
   extensions = ['eon_collective_docs_theme', ...]

   # select the theme
   html_theme = 'eon_collective_docs_theme'


Alternatively, if you would like to programmatically append the theme to your extenstions,
consider adding the snippet below at the end of ``conf.py``:

.. code-block:: python

   try:
      extensions
   except NameError:
      extensions = []

   extensions.append('eon_collective_docs_theme')
   html_theme = 'eon_collective_docs_theme'
