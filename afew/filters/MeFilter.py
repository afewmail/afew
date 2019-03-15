# -*- coding: utf-8 -*-
# SPDX-License-Identifier: ISC
# Copyright (c) Amadeusz Zolnowski <aidecoe@aidecoe.name>

from __future__ import print_function, absolute_import, unicode_literals

import re

from ..utils import filter_compat
from .BaseFilter import Filter
from ..NotmuchSettings import notmuch_settings


class MeFilter(Filter):
    message = 'Tagging all mails sent directly to myself'
    _bare_email_re = re.compile(r"[^<]*<(?P<email>[^@<>]+@[^@<>]+)>")

    def __init__(self, database, me_tag='to-me', tags_blacklist=[]):
        super().__init__(database, tags_blacklist=tags_blacklist)

        my_addresses = set()
        my_addresses.add(notmuch_settings.get('user', 'primary_email'))
        if notmuch_settings.has_option('user', 'other_email'):
            other_emails = notmuch_settings.get('user', 'other_email').split(';')
            my_addresses.update(filter_compat(None, other_emails))

        self.query = ' OR '.join('to:"%s"' % address
                                 for address in my_addresses)

        self.me_tag = me_tag

    def handle_message(self, message):
        if not self._tag_blacklist.intersection(message.get_tags()):
            self.add_tags(message, self.me_tag)
