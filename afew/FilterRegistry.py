# -*- coding: utf-8 -*-
# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

from __future__ import print_function, absolute_import, unicode_literals

import pkg_resources


RAISEIT = object()


class FilterRegistry:
    """
    The FilterRegistry is responsible for returning
    filters by key.
    Filters get registered via entry points.
    To avoid any circular dependencies, the registry loads
    the Filters lazily
    """
    def __init__(self, filters):
        self._filteriterator = filters

    @property
    def filter(self):
        if not hasattr(self, '_filter'):
            self._filter = {}
            for f in self._filteriterator:
                self._filter[f.name] = f.load()
        return self._filter

    def get(self, key, default=RAISEIT):
        if default == RAISEIT:
            return self.filter[key]
        else:
            return self.filter.get(key, default)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.filter[key] = value

    def __delitem__(self, key):
        del self.filter[key]

    def keys(self):
        return self.filter.keys()

    def values(self):
        return self.filter.values()

    def items(self):
        return self.filter.items()


all_filters = FilterRegistry(pkg_resources.iter_entry_points('afew.filter'))

def register_filter(klass):
    '''Decorator function for registering a class as a filter.'''

    all_filters[klass.__name__] = klass
    return klass

