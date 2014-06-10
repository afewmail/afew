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

import collections
import logging

import notmuch


class Filter(object):
    message = 'No message specified for filter'
    tags = []
    tags_blacklist = []

    def __init__(self, database, **kwargs):
        super(Filter, self).__init__()

        self.log = logging.getLogger('{}.{}'.format(
            self.__module__, self.__class__.__name__))

        self.database = database
        if 'tags' not in kwargs:
            kwargs['tags'] = self.tags
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.flush_changes()
        self._tags_to_add = []
        self._tags_to_remove = []
        for tag_action in self.tags:
            if tag_action[0] not in '+-':
                raise ValueError('Each tag must be preceded by either + or -')

            (self._tags_to_add if tag_action[0] == '+' else self._tags_to_remove).append(tag_action[1:])

        self._tag_blacklist = set(self.tags_blacklist)

    def flush_changes(self):
        '''
        (Re)Initializes the data structures that hold the enqueued
        changes to the notmuch database.
        '''
        self._add_tags = collections.defaultdict(lambda: set())
        self._remove_tags = collections.defaultdict(lambda: set())
        self._flush_tags = []

    def run(self, query):
        self.log.info(self.message)

        if getattr(self, 'query', None):
            if query:
                query = '(%s) AND (%s)' % (query, self.query)
            else:
                query = self.query

        for message in self.database.get_messages(query):
            self.handle_message(message)

    def handle_message(self, message):
        if not self._tag_blacklist.intersection(message.get_tags()):
            self.remove_tags(message, *self._tags_to_remove)
            self.add_tags(message, *self._tags_to_add)

    def add_tags(self, message, *tags):
        if tags:
            self.log.debug('Adding tags %s to id:%s' % (', '.join(tags),
                                                       message.get_message_id()))
            self._add_tags[message.get_message_id()].update(tags)

    def remove_tags(self, message, *tags):
        if tags:
            self.log.debug('Removing tags %s from id:%s' % (', '.join(tags),
                                                           message.get_message_id()))
            self._remove_tags[message.get_message_id()].update(tags)

    def flush_tags(self, message):
        self.log.debug('Removing all tags from id:%s' %
                      message.get_message_id())
        self._flush_tags.append(message.get_message_id())

    def commit(self, dry_run=True):
        dirty_messages = set()
        dirty_messages.update(self._flush_tags)
        dirty_messages.update(self._add_tags.keys())
        dirty_messages.update(self._remove_tags.keys())

        if not dirty_messages:
            return

        if dry_run:
            self.log.info('I would commit changes to %i messages' % len(dirty_messages))
        else:
            self.log.info('Committing changes to %i messages' % len(dirty_messages))
            db = self.database.open(rw=True)

            for message_id in dirty_messages:
                messages = notmuch.Query(db, 'id:"%s"' % message_id).search_messages()

                for message in messages:
                    if message_id in self._flush_tags:
                        message.remove_all_tags()

                    for tag in self._add_tags.get(message_id, []):
                        message.add_tag(tag)

                    for tag in self._remove_tags.get(message_id, []):
                        message.remove_tag(tag)

        self.flush_changes()

