# -*- coding: utf-8 -*-
# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

from __future__ import print_function, absolute_import, unicode_literals

from ..filters.SentMailsFilter import SentMailsFilter
from ..NotmuchSettings import get_notmuch_new_tags

class ArchiveSentMailsFilter(SentMailsFilter):
    message = 'Archiving all mails sent by myself to others'

    def __init__(self, database, sent_tag=''):
        super(ArchiveSentMailsFilter, self).__init__(database, sent_tag)

    def handle_message(self, message):
        super(ArchiveSentMailsFilter, self).handle_message(message)
        self.remove_tags(message, *get_notmuch_new_tags())
