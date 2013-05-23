# -*- coding: utf-8 -*-
"""
Exceptions used in Grako parser generation and in generated parsers.

The parameters of the Failed... hierarchy of exceptions are the ones required
to be able to report accurate error messages as late as possible with the aid
of the .buffering.Buffer class, and with as little overhead as possible for
exceptions that will not be parsing errors (remember that Grako uses the
exception system to backtrack).
"""
from __future__ import print_function, division, absolute_import, unicode_literals


class GrakoException(Exception):
    pass


class OptionSucceeded(GrakoException):
    pass


class GrammarError(GrakoException):
    pass


class SemanticError(GrakoException):
    pass


class MissingSemanticFor(SemanticError):
    pass


class ParseError(GrakoException):
    pass


class FailedSemantics(ParseError):
    pass


class FailedParseBase(ParseError):
    def __init__(self, buf, item):
        self.buf = buf
        self.pos = buf.pos
        self.item = item

    @property
    def message(self):
        return self.item

    def __str__(self):
        info = self.buf.line_info(self.pos)
        template = "{}({}:{}) {} :\n{}\n{}^"
        return template.format(info.filename,
                               info.line + 1, info.col + 1,
                               self.message,
                               info.text,
                               ' ' * info.col
                               )


class FailedParse(FailedParseBase):
    pass


class FailedToken(FailedParse):
    def __init__(self, buf, token):
        super(FailedToken, self).__init__(buf, token)
        self.token = token

    @property
    def message(self):
        return "expecting '%s'" % self.token


class FailedPattern(FailedParse):
    def __init__(self, buf, pattern):
        super(FailedPattern, self).__init__(buf, pattern)
        self.pattern = pattern

    @property
    def message(self):
        return "expecting '%s'" % self.pattern


class FailedMatch(FailedParse):
    def __init__(self, buf, name, item):
        super(FailedMatch, self).__init__(buf, item)
        self.name = name

    @property
    def message(self):
        return "expecting '%s'" % self.name


class FailedRef(FailedParseBase):
    def __init__(self, buf, name):
        super(FailedRef, self).__init__(buf, name)
        self.name = name

    @property
    def message(self):
        return "could not resolve reference to rule '%s'" % self.name


class FailedCut(FailedParse):
    def __init__(self, nested):
        super(FailedCut, self).__init__(nested.buf, nested.item)
        self.pos = nested.pos
        self.nested = nested

    @property
    def message(self):
        return self.nested.message


class FailedChoice(FailedParse):
    @property
    def message(self):
        return 'no viable option'


class FailedLookahead(FailedParse):
    @property
    def message(self):
        return 'failed lookahead'
