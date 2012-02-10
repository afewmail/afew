# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals

#
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

import os

from .configparser import RawConfigParser

notmuch_settings = RawConfigParser()

def read_notmuch_settings(path = None):
    if path == None:
        path = os.environ.get('NOTMUCH_CONFIG', os.path.expanduser('~/.notmuch-config'))

    notmuch_settings.readfp(open(path))

def get_notmuch_new_tags():
    return notmuch_settings.get_list('new', 'tags')

def get_notmuch_new_query():
    return '(%s)' % ' AND '.join('tag:%s' % tag for tag in get_notmuch_new_tags())
