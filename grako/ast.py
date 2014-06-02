# -*- coding: utf-8 -*-
"""
Define the AST class, a direct descendant of dict that's used during parsing
to store the values of named elements of grammar rules.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping


class AST(MutableMapping):

    def __init__(self, *args, **kwargs):
        super(AST, self).__init__()
        base = dict(*args, **kwargs)
        super(AST, self).__setattr__('_base', base)
        super(AST, self).__setattr__('_order', [])

    @property
    def parseinfo(self):
        """ Make the special attribute `_parseinfo` be available
            as a property without an underscore in the name.
            This patch helps with backwards compatibility.
        """
        return self._parseinfo

    def __contains__(self, key):
        return key in self._base

    def __setitem__(self, key, value):
        self._add(key, value)

    def __getitem__(self, key):
        return self._base.get(key, None)

    def __delitem__(self, key):
        del self._base[key]

    def __iter__(self):
        base = self._base
        return (key for key in self._order if key in base)

    def __len__(self):
        return len(self._base)

    def __getattr(self, name):
        base = super(AST, self).__getattribute__('_base')
        if name == '_base':
            return base
        if name in base:
            return base[name]

    __setattr__ = __setitem__

    def __getattribute__(self, name):
        try:
            return super(AST, self).__getattribute__(name)
        except AttributeError:
            base = super(AST, self).__getattribute__('_base')
            if name == '_base':
                return base
            if name in base:
                return base[name]

    def _define(self, keys, list_keys=None):
        for key in list_keys or []:
            if key not in self._base:
                self._base[key] = []
        for key in keys:
            if key not in self._base:
                self._base[key] = None

    def _copy(self):
        haslists = any(isinstance(v, list) for v in self.values())
        if not haslists:
            return AST(self)
        return AST(
            (k, v[:] if isinstance(v, list) else v)
            for k, v in self.items()
        )

    def _add(self, key, value, force_list=False):
        previous = self._base.get(key, None)
        if previous is None:
            if force_list:
                self._base[key] = [value]
            else:
                self._base[key] = value
            self._order.append(key)
        elif isinstance(previous, list):
            previous.append(value)
        else:
            self._base[key] = [previous, value]
        return self

    def _append(self, key, value):
        return self._add(key, value, force_list=True)

    def __json__(self):
        return self._base

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, super(AST, self).__repr__())
