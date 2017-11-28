# -*- coding: utf-8 -*-
# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

from __future__ import print_function, absolute_import, unicode_literals

try:
    # py3k
    import configparser
except ImportError:
    import ConfigParser as configparser

class GetListMixIn(object):
    def get_list(self, section, key, delimiter = ';',
                 filter_ = lambda value: value.strip(),
                 include_falsish = False):
        result = (filter_(value)
                  for value in self.get(section, key).split(delimiter))

        if include_falsish:
            return result
        else:
            return filter(None, result)

class SafeConfigParser(configparser.SafeConfigParser, GetListMixIn): pass
class RawConfigParser(configparser.RawConfigParser, GetListMixIn): pass
