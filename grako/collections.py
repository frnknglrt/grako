# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
import collections


class CountBoundedDict(collections.OrderedDict):
    def __init__(self, *args, **kwargs):
        self.threshold = kwargs.pop('threshold', 1)
        self.counts = collections.Counter()
        super(CountBoundedDict, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        self.counts[key] += self.threshold
        value = super(CountBoundedDict, self).__getitem__(key)
        super(CountBoundedDict, self).__setitem__(key, value)  # move it to last
        return value

    def __setitem__(self, key, value):
        super(CountBoundedDict, self).__setitem__(key, value)
        self.counts[key] += self.threshold
        t = -self.threshold
        for key in self:
            value = self.counts[key] - 1
            if value < t:
                del self[key]
                del self.counts[key]
            else:
                self.counts[key] = value
