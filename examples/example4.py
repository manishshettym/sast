def execute_pytest(capture='all', flags='-rapP'):
    'Execute module as pytest with detailed summary report.\n\n    Parameters\n    ----------\n    capture : str\n        Log or stdout/stderr capture option. ex: log (only logger),\n        all (includes stdout/stderr)\n    flags : str\n        Which tests to show logs and results for.\n    '
    fname = os.path.basename(__file__)
    pytest.main(['-q', '--show-capture={}'.format(capture), fname, flags])