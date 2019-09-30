# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

from afew.filters.BaseFilter import Filter


class KillThreadsFilter(Filter):
    message = 'Looking for messages in killed threads that are not yet killed'
    query = 'NOT tag:killed'

    def handle_message(self, message):
        query = self.database.get_messages('thread:"%s" AND tag:killed' % message.get_thread_id())

        if len(list(query)):
            self.add_tags(message, 'killed')
