# -*- coding: utf-8 -*-
# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

from __future__ import print_function, absolute_import, unicode_literals

import os

from .configparser import RawConfigParser

notmuch_settings = RawConfigParser()

def read_notmuch_settings(path = None):
    if path == None:
        path = os.environ.get('NOTMUCH_CONFIG', os.path.expanduser('~/.notmuch-config'))

    notmuch_settings.readfp(open(path))

def get_notmuch_new_tags():
    # see issue 158
    return filter(lambda x: x != 'unread', notmuch_settings.get_list('new', 'tags'))

def get_notmuch_new_query():
    return '(%s)' % ' AND '.join('tag:%s' % tag for tag in get_notmuch_new_tags())
