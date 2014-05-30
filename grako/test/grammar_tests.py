# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
import unittest
from grako.tool import genmodel
from grako.grammars import ModelContext
from grako.exceptions import FailedSemantics

class GrammarTests(unittest.TestCase):
    def test_keywords_in_rule_names(self):
        grammar = '''
            start
                =
                whitespace
                ;

            whitespace
                =
                    {'x'}+
                ;
        '''
        m = genmodel('Keywords', grammar)
        m.parse('x')

    def test_update_ast(self):
        grammar = '''
            foo = name:"1" [ name: bar ] ;
            bar = { "2" } * ;
        '''
        m = genmodel('Keywords', grammar)
        ast = m.parse('1 2')
        self.assertEqual(ast.name, ['1', '2'])

    def test_stateful(self):
        # Parser for mediawiki-style unordered lists.
        grammar = r'''
        document = @ul [ nl ] $ ;
        ul = "*" ul_start el+:li { nl el:li } * ul_end ;
        li = ul | li_text ;
        (* Quirk: If a text line is followed by a sublist, the sublist does not get its own li.  *)
        li_text = text:text [ ul:li_followed_by_ul ] ;
        li_followed_by_ul = nl @ul ;
        text = ?/.*/? ;
        nl = ?/\n/? ul_marker ;
        (* The following rules are placeholders for state transitions.  *)
        ul_start = () ;
        ul_end = () ;
        (* The following rules are placeholders for state validations and grammar rules.  *)
        ul_marker = () ;
        '''
        class StatefulSemantics(object):
            def __init__(self, parser):
                self._context = parser

            def ul_start(self, ast):
                ctx = self._context
                ctx._state = 1 if ctx._state is None else ctx._state + 1
                return ast

            def ul_end(self, ast):
                ctx = self._context
                ctx._state = None if ctx._state is None or ctx._state <= 1 else ctx._state - 1
                return ast

            def ul_marker(self, ast):
                ctx = self._context
                if ctx._state is not None:
                    if not ctx.buf.match("*" * ctx._state):
                        raise FailedSemantics("not at correct level")
                return ast

            def ul(self, ast):
                return "<ul>" + "".join(ast.el) + "</ul>"

            def li(self, ast):
                return "<li>" + ast + "</li>"

            def li_text(self, ast):
                return ast.text if ast.ul is None else ast.text + ast.ul

        model = genmodel("test", grammar)
        context = ModelContext(model.rules, whitespace='', nameguard=False)
        ast = model.parse('*abc', "document", context=context, semantics=StatefulSemantics(context), whitespace='', nameguard=False)
        self.assertEqual(ast, "<ul><li>abc</li></ul>")
        ast = model.parse('*abc\n', "document", context=context, semantics=StatefulSemantics(context), whitespace='', nameguard=False)
        self.assertEqual(ast, "<ul><li>abc</li></ul>")
        ast = model.parse('*abc\n*def\n', "document", context=context, semantics=StatefulSemantics(context), whitespace='', nameguard=False)
        self.assertEqual(ast, "<ul><li>abc</li><li>def</li></ul>")
        ast = model.parse('**abc', "document", context=context, semantics=StatefulSemantics(context), whitespace='', nameguard=False)
        self.assertEqual(ast, "<ul><li><ul><li>abc</li></ul></li></ul>")
        ast = model.parse('*abc\n**def\n', "document", context=context, semantics=StatefulSemantics(context), whitespace='', nameguard=False)
        self.assertEqual(ast, "<ul><li>abc<ul><li>def</li></ul></li></ul>")
        

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(GrammarTests)


def main():
    unittest.TextTestRunner(verbosity=2).run(suite())

if __name__ == '__main__':
    main()