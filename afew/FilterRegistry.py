# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

import sys
from importlib.metadata import entry_points

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


# Python 3.10+ uses entry_points(group=...), Python 3.9 uses entry_points()[group]
if sys.version_info >= (3, 10):
    filter_entry_points = entry_points(group='afew.filter')
else:
    filter_entry_points = entry_points().get('afew.filter', [])

all_filters = FilterRegistry(filter_entry_points)


def register_filter(klass):
    '''Decorator function for registering a class as a filter.'''

    all_filters[klass.__name__] = klass
    return klass
