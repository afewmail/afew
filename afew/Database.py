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

import notmuch

from .NotmuchSettings import notmuch_settings
from .utils import extract_mail_body

class Database(object):
    '''
    Convenience wrapper around `notmuch`.
    '''

    def __init__(self):
        self.db_path = notmuch_settings.get('database', 'path')

    def do_query(self, query):
        '''
        Executes a notmuch query.

        If the current object has an `query` field, the intersection
        of both queries is returned.

        :param query: the query to execute
        :type  query: str
        :returns: the query result
        :rtype:   :class:`notmuch.Query`
        '''
        if hasattr(self, 'query'):
            if query:
                query = '(%s) AND (%s)' % (query, self.query)
            else:
                query = self.query

        logging.debug('Executing query %r' % query)
        db = notmuch.Database(self.db_path)
        return notmuch.Query(db, query)

    def get_messages(self, query, full_thread = False):
        '''
        Get all messages mathing the given query.

        :param query: the query to execute using :func:`Database.do_query`
        :type  query: str
        :param full_thread: return all messages from mathing threads
        :type  full_thread: bool
        :returns: an iterator over :class:`notmuch.Message` objects
        '''
        if not full_thread:
            for message in self.do_query(query).search_messages():
                yield message
        else:
            for thread in self.do_query(query).search_threads():
                for message in self.walk_thread(thread):
                    yield message


    def mail_bodies_matching(self, *args, **kwargs):
        '''
        Filters each message yielded from
        :func:`Database.get_messages` through
        :func:`afew.utils.extract_mail_body`.

        This functions accepts the same arguments as
        :func:`Database.get_messages`.

        :returns: an iterator over :class:`list` of :class:`str`
        '''
        query = self.get_messages(*args, **kwargs)
        for message in query:
            yield extract_mail_body(message)

    def walk_replies(self, message):
        '''
        Returns all replies to the given message.

        :param message: the message to start from
        :type  message: :class:`notmuch.Message`
        :returns: an iterator over :class:`notmuch.Message` objects
        '''
        yield message

        # TODO: bindings are *very* unpythonic here... iterator *or* None
        #       is a nono
        replies = message.get_replies()
        if replies != None:
            for message in replies:
                # TODO: yield from
                for message in self.walk_replies(message):
                    yield message

    def walk_thread(self, thread):
        '''
        Returns all messages in the given thread.

        :param message: the tread you are interested in
        :type  message: :class:`notmuch.Thread`
        :returns: an iterator over :class:`notmuch.Message` objects
        '''
        for message in thread.get_toplevel_messages():
            # TODO: yield from
            for message in self.walk_replies(message):
                yield message
