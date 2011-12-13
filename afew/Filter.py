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

import logging
import collections

import notmuch

from .Database import Database

all_filters = dict()
def register_filter(klass):
    all_filters[klass.__name__] = klass
    return klass

@register_filter
class Filter(Database):
    message = 'No message specified for filter'
    tags = ''
    tag_blacklist = ''

    def __init__(self, **kwargs):
        super(Filter, self).__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

        self._add_tags = collections.defaultdict(lambda: set())
        self._remove_tags = collections.defaultdict(lambda: set())
        self._flush_tags = list()

        self._tags_to_add = list()
        self._tags_to_remove = list()
        for tag_action in self.tags.split():
            if tag_action[0] not in '+-':
                raise ValueError('Each tag must be preceded by either + or -')

            (self._tags_to_add if tag_action[0] == '+' else self._tags_to_remove).append(tag_action[1:])

        self._tag_blacklist = set(self.tag_blacklist.split())

    def run(self, query):
        logging.info(self.message)
        for message in self.get_messages(query):
            self.handle_message(message)

    def handle_message(self, message):
        if not self._tag_blacklist.intersection(message.get_tags()):
            self.remove_tags(message, *self._tags_to_remove)
            self.add_tags(message, *self._tags_to_add)

    def add_tags(self, message, *tags):
        if tags:
            logging.debug('Adding tags %s to %s' % (', '.join(tags), message))
            self._add_tags[message.get_message_id()].update(tags)

    def remove_tags(self, message, *tags):
        if tags:
            logging.debug('Removing tags %s from %s' % (', '.join(tags), message))
            self._remove_tags[message.get_message_id()].update(tags)

    def flush_tags(self, message):
        logging.debug('Removing all tags from %s' % message)
        self._flush_tags.append(message.get_message_id())

    def commit(self, dry_run = True):
        dirty_messages = set()
        dirty_messages.update(self._flush_tags)
        dirty_messages.update(self._add_tags.keys())
        dirty_messages.update(self._remove_tags.keys())

        if dry_run:
            logging.info('I would commit changes to %i messages' % len(dirty_messages))
        else:
            logging.info('Committing changes to %i messages' % len(dirty_messages))
            db = notmuch.Database(self.db_path, mode = notmuch.Database.MODE.READ_WRITE)

            for message_id in dirty_messages:
                messages = notmuch.Query(db, 'id:"%s"' % message_id).search_messages()

                for message in messages:
                    if message_id in self._flush_tags:
                        message.remove_all_tags()

                    for tag in self._add_tags.get(message_id, []):
                        message.add_tag(tag)

                    for tag in self._remove_tags.get(message_id, []):
                        message.remove_tag(tag)

