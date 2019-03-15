#  -*- coding: utf-8 -*-
# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

from __future__ import print_function, absolute_import, unicode_literals

import collections
import logging

import notmuch


class Filter:
    message = 'No message specified for filter'
    tags = []
    tags_blacklist = []

    def __init__(self, database, **kwargs):
        super().__init__()

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
            filtered_tags = list(tags)
            self.log.debug('Removing tags %s from id:%s' % (', '.join(filtered_tags),
                                                           message.get_message_id()))
            self._remove_tags[message.get_message_id()].update(filtered_tags)

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
                message = db.find_message(message_id)

                if message_id in self._flush_tags:
                    message.remove_all_tags()

                for tag in self._add_tags.get(message_id, []):
                    message.add_tag(tag)

                for tag in self._remove_tags.get(message_id, []):
                    message.remove_tag(tag)

        self.flush_changes()
