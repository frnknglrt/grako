# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
from ..rendering import Renderer


class ParserGenerator(object):

    def codegen(self, grammar):
        pass

    def _render(self, template, fields):
        return Renderer(template).render(fields)
