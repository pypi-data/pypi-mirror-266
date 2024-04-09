# [Eon Collective Documentation theme](https://github.com/janerose-njogu/eon-collective-docs-theme)

The Eon Collective Documentation theme contains all files required to build a Sphinx extension that provides the theme.

> 📘 FYI
> 
> Supports Python >= 3.8


## Assumptions
This guide assumes that you have set up Sphinx in your project. All you need to do is install this theme and include it within your conf.py file.

It is also assumed that you understand Sphinx.

## Installation

```sh
pip install eon-collective-docs-theme
```

## Usage

In your conf.py file of a Sphinx documentation, specify the "Eon Collective Documentation theme" as an extension.

```python
# include the theme in the list of extensions to be loaded
extensions = ['eon_collective_docs_theme', …]

# select the theme
html_theme = 'eon_collective_docs_theme'
```

## Credits

The Eon Collective Documentation theme is based on the [Sphinx Wagtail theme](https://github.com/wagtail/sphinx_wagtail_theme). 

Read more about Sphinx Wagtail theme in their [documentation](https://sphinx-wagtail-theme.readthedocs.io/en/latest/).
