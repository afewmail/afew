# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals

#
# Copyright (c) Amadeusz Zolnowski <aidecoe@aidecoe.name>
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

import re

from ..utils import filter_compat
from .BaseFilter import Filter
from ..NotmuchSettings import notmuch_settings


class MeFilter(Filter):
    message = 'Tagging all mails sent directly to myself'
    _bare_email_re = re.compile(r"[^<]*<(?P<email>[^@<>]+@[^@<>]+)>")

    def __init__(self, database, me_tag='to-me'):
        super(MeFilter, self).__init__(database)

        my_addresses = set()
        my_addresses.add(notmuch_settings.get('user', 'primary_email'))
        if notmuch_settings.has_option('user', 'other_email'):
            other_emails = notmuch_settings.get('user', 'other_email').split(';')
            my_addresses.update(filter_compat(None, other_emails))

        self.query = ' OR '.join('to:"%s"' % address
                                 for address in my_addresses)

        self.me_tag = me_tag

    def handle_message(self, message):
        self.add_tags(message, self.me_tag)
