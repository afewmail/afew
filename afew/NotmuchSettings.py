# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

import os

from afew.configparser import RawConfigParser

notmuch_settings = RawConfigParser()


def read_notmuch_settings(path=None):
    if path == None:
        path = os.environ.get('NOTMUCH_CONFIG', os.path.expanduser('~/.notmuch-config'))

    with open(path) as fp:
        notmuch_settings.read_file(fp)

def write_notmuch_settings(path = None):
    if path == None:
        path = os.environ.get('NOTMUCH_CONFIG', os.path.expanduser('~/.notmuch-config'))

    with open(path, 'w+') as fp:
        notmuch_settings.write(fp)


def get_notmuch_new_tags():
    # see issue 158
    return filter(lambda x: x != 'unread', notmuch_settings.get_list('new', 'tags'))


def get_notmuch_new_query():
    return '(%s)' % ' AND '.join('tag:%s' % tag for tag in get_notmuch_new_tags())
