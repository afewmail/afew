# -*- coding: utf-8 -*-
# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

import configparser

class GetListMixIn:
    def get_list(self, section, key, delimiter = ';',
                 filter_ = lambda value: value.strip(),
                 include_falsish = False):
        result = (filter_(value)
                  for value in self.get(section, key).split(delimiter))

        if include_falsish:
            return result
        else:
            return filter(None, result)

class ConfigParser(configparser.ConfigParser, GetListMixIn): pass
class RawConfigParser(configparser.RawConfigParser, GetListMixIn): pass
