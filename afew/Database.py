# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

import os
import time
import logging

import notmuch2

from afew.NotmuchSettings import notmuch_settings, get_notmuch_new_tags


class Database:
    """
    Convenience wrapper around `notmuch`.
    """

    def __init__(self):
        self.db_path = self._calculate_db_path()
        self.handle = None

    def _calculate_db_path(self):
        """
        Calculates the path to use for the database. Supports notmuch's
        methodology including falling back to $MAILDIR or $HOME/mail if a path
        is not specified and using $HOME/<path> if path is relative.
        """
        default_path = os.environ.get('MAILDIR', '{}/mail'.format(os.environ.get('HOME')))
        db_path = notmuch_settings.get('database', 'path', fallback=default_path)

        # If path is relative, notmuch prepends $HOME in front
        if not os.path.isabs(db_path):
            db_path = '{}/{}'.format(os.environ.get('HOME'), db_path)

        return db_path

    def __enter__(self):
        """
        Implements the context manager protocol.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Implements the context manager protocol.
        """
        self.close()

    def open(self, rw=False, retry_for=180, retry_delay=1):
        if rw:
            if self.handle and self.handle.mode == notmuch2.Database.MODE.READ_WRITE:
                return self.handle

            start_time = time.time()
            while True:
                try:
                    self.handle = notmuch2.Database(self.db_path,
                                                    mode=notmuch2.Database.MODE.READ_WRITE)
                    break
                except notmuch2.NotmuchError:
                    time_left = int(retry_for - (time.time() - start_time))

                    if time_left <= 0:
                        raise

                    if time_left % 15 == 0:
                        logging.debug(
                            'Opening the database failed. Will keep trying for another {} seconds'.format(time_left))

                    time.sleep(retry_delay)
        else:
            if not self.handle:
                self.handle = notmuch2.Database(self.db_path,
                                                mode=notmuch2.Database.MODE.READ_ONLY)

        return self.handle

    def close(self):
        """
        Closes the notmuch database if it has been opened.
        """
        if self.handle:
            self.handle.close()
            self.handle = None

    def do_query(self, query):
        """
        Executes a notmuch query.

        :param query: the query to execute
        :type  query: str
        :returns: the query result
        :rtype:   :class:`notmuch.Query`
        """
        logging.debug('Executing query %r' % query)
        return notmuch2.Database.messages(self.open(), query)

    def get_messages(self, query, full_thread=False):
        """
        Get all messages matching the given query.

        :param query: the query to execute using :func:`Database.do_query`
        :type  query: str
        :param full_thread: return all messages from mathing threads
        :type  full_thread: bool
        :returns: an iterator over :class:`notmuch.Message` objects
        """
        if not full_thread:
            for message in self.do_query(query):
                yield message
        else:
            for thread in self.do_query(query):
                for message in self.walk_thread(thread):
                    yield message

    def walk_replies(self, message):
        """
        Returns all replies to the given message.

        :param message: the message to start from
        :type  message: :class:`notmuch.Message`
        :returns: an iterator over :class:`notmuch.Message` objects
        """
        yield message

        # TODO: bindings are *very* unpythonic here... iterator *or* None
        #       is a nono
        replies = message.get_replies()
        if replies is not None:
            for message in replies:
                # TODO: yield from
                for message in self.walk_replies(message):
                    yield message

    def walk_thread(self, thread):
        """
        Returns all messages in the given thread.

        :param thread: the tread you are interested in
        :type  thread: :class:`notmuch.Thread`
        :returns: an iterator over :class:`notmuch.Message` objects
        """
        for message in thread.get_toplevel_messages():
            # TODO: yield from
            for message in self.walk_replies(message):
                yield message

    def add_message(self, path, sync_maildir_flags=False, new_mail_handler=None):
        """
        Adds the given message to the notmuch index.

        :param path: path to the message
        :type  path: str
        :param sync_maildir_flags: if `True` notmuch converts the
                                   standard maildir flags to tags
        :type  sync_maildir_flags: bool
        :param new_mail_handler: callback for new messages
        :type  new_mail_handler: a function that is called with a
                                 :class:`notmuch.Message` object as
                                 its only argument
        :raises: :class:`notmuch.NotmuchError` if adding the message fails
        :returns: a :class:`notmuch.Message` object
        """
        # TODO: it would be nice to update notmuchs directory index here
        handle = self.open(rw=True)
        message, duplicate = handle.add(path, sync_flags=sync_maildir_flags)

        if not duplicate:
            logging.info('Found new mail in {}'.format(path))

            for tag in get_notmuch_new_tags():
                message.tags.add(tag)

            if new_mail_handler:
                new_mail_handler(message)

        return message

    def remove_message(self, path):
        """
        Remove the given message from the notmuch index.

        :param path: path to the message
        :type  path: str
        """
        self.open(rw=True).remove_message(path)
