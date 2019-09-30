# SPDX-License-Identifier: ISC
# Copyright (c) Amadeusz Zolnowski <aidecoe@aidecoe.name>

import re

from afew.filters.BaseFilter import Filter
from afew.NotmuchSettings import notmuch_settings


class MeFilter(Filter):
    message = 'Tagging all mails sent directly to myself'
    _bare_email_re = re.compile(r"[^<]*<(?P<email>[^@<>]+@[^@<>]+)>")

    def __init__(self, database, me_tag='to-me', tags_blacklist=[]):
        super().__init__(database, tags_blacklist=tags_blacklist)

        my_addresses = set()
        my_addresses.add(notmuch_settings.get('user', 'primary_email'))
        if notmuch_settings.has_option('user', 'other_email'):
            for other_email in notmuch_settings.get('user', 'other_email').split(';'):
                my_addresses.add(other_email)

        self.query = ' OR '.join('to:"%s"' % address
                                 for address in my_addresses)

        self.me_tag = me_tag

    def handle_message(self, message):
        if not self._tag_blacklist.intersection(message.get_tags()):
            self.add_tags(message, self.me_tag)
