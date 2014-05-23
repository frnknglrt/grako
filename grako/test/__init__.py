# -*- coding: utf-8 -*-
"""
The Grako test suite.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

if __name__ == '__main__':
    import unittest
    from . import bootstrap_test
    from . import buffering_test
    from . import grammar_test
    from . import codegen_test
    from . import parsing_test

    suite = unittest.TestSuite(tests=[
        bootstrap_test.suite(),
        buffering_test.suite(),
        grammar_test.suite(),
        codegen_test.suite(),
        parsing_test.suite()
    ])

    unittest.TextTestRunner(verbosity=2).run(suite)
