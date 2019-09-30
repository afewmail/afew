# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

from afew.filters.SentMailsFilter import SentMailsFilter
from afew.NotmuchSettings import get_notmuch_new_tags


class ArchiveSentMailsFilter(SentMailsFilter):
    message = 'Archiving all mails sent by myself to others'

    def __init__(self, database, sent_tag='', to_transforms=''):
        super().__init__(database, sent_tag)

    def handle_message(self, message):
        super().handle_message(message)
        self.remove_tags(message, *get_notmuch_new_tags())
