# SPDX-License-Identifier: ISC
# Copyright (c) Amadeusz Zolnowski <aidecoe@aidecoe.name>

import re

from afew.filters.BaseFilter import Filter
from afew.NotmuchSettings import notmuch_settings


class MeFilter(Filter):
    message = 'Tagging all mails sent directly to myself'
    _bare_email_re = re.compile(r"[^<]*<(?P<email>[^@<>]+@[^@<>]+)>")

    def __init__(self, database, me_tag=None, tags_blacklist=[]):
        super().__init__(database, tags_blacklist=tags_blacklist)

        my_addresses = set()
        my_addresses.add(notmuch_settings.get('user', 'primary_email'))
        if notmuch_settings.has_option('user', 'other_email'):
            for other_email in notmuch_settings.get_list('user', 'other_email'):
                my_addresses.add(other_email)

        self.query = ' OR '.join('to:"%s"' % address
                                 for address in my_addresses)

        # The me_tag option does nothing that couldn't be done with the
        # "normal" tags option. If the me_tag is explicitly configured or there
        # is no tags option make use of it.
        if not me_tag is None or (not self._tags_to_add and not self._tags_to_remove):
            if me_tag is None:
                me_tag = 'to-me'
            self._tags_to_add.append(me_tag)
