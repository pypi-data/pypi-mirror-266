import eon_collective_docs_theme


def test_theme_info():
    assert isinstance(eon_collective_docs_theme.__version__, str)
    assert len(eon_collective_docs_theme.__version__) >= 5


def test_module_methods():
    assert isinstance(eon_collective_docs_theme.get_html_theme_path(), str)
