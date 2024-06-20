# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

from afew.filters.SentMailsFilter import SentMailsFilter
from afew.NotmuchSettings import get_notmuch_new_tags


class ArchiveSentMailsFilter(SentMailsFilter):
    message = 'Archiving all mails sent by myself to others'

    def __init__(self, database, sent_tag='', to_transforms='', archive_thread=False):
        super().__init__(database, sent_tag)
        self.archive_thread = archive_thread

    def handle_message(self, message):
        super().handle_message(message)
        self.remove_tags(message, *get_notmuch_new_tags())
        # Reply and Archive: remove inbox tag from thread when replying
        if self.archive_thread:
            threadquery = f'thread:{message.get_thread_id()} and tag:inbox'
            inbox_in_thread = self.database.get_messages(threadquery)
            for msg in inbox_in_thread:
                self.remove_tags(msg, 'inbox')
