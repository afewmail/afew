# coding=utf-8

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

from .utils import extract_mail_body

class Database(object):
    def __init__(self, db_path):
        self.db_path = db_path
        self.db = notmuch.Database(db_path)

    def do_query(self, query):
        if hasattr(self, 'query'):
            if query:
                query = '(%s) AND (%s)' % (query, self.query)
            else:
                query = self.query

        logging.debug('Executing query %r' % query)
        return notmuch.Query(self.db, query)

    def get_messages(self, query, full_thread = False):
        if not full_thread:
            for message in self.do_query(query).search_messages():
                yield message
        else:
            for thread in self.do_query(query).search_threads():
                for message in self.walk_thread(thread):
                    yield message


    def mail_bodies_matching(self, *args, **kwargs):
        query = self.get_messages(*args, **kwargs)
        for message in query:
            yield extract_mail_body(message)

    def walk_replies(self, message):
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
        for message in thread.get_toplevel_messages():
            # TODO: yield from
            for message in self.walk_replies(message):
                yield message
