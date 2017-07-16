# coding=utf-8

#
# Copyright (c) dtk <dtk@gmx.de>
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


import notmuch
import logging
import os, shutil
from subprocess import check_call, CalledProcessError

from .Database import Database
from .utils import get_message_summary
from datetime import date, datetime, timedelta
from abc import ABCMeta, abstractmethod
import uuid


class MailMover(Database):
    __metaclass__ = ABCMeta
    '''
    Move mail files matching a given notmuch query into a target maildir folder.
    '''
    def __init__(self, max_age=0, rename=False, dry_run=False, query=None):
        super(MailMover, self).__init__()
        self.db = notmuch.Database(self.db_path)
        self.query = query
        if max_age:
            days = timedelta(int(max_age))
            start = date.today() - days
            now = datetime.now()
            self.query += ' AND {start}..{now}'.format(start=start.strftime('%s'),
                                                       now=now.strftime('%s'))
        self.dry_run = dry_run
        self.rename = rename

    @abstractmethod
    def move(target, rules):
        '''
        Move mails in folder maildir according to the given rules.
        '''
        pass

    #
    # private:
    #

    def _update_db(self, rule_id):
        '''
        Update the database after mail files have been moved in the filesystem.
        '''
        try:
            check_call(['notmuch', 'new'])
        except CalledProcessError as err:
            logging.error("Could not update notmuch database " \
                          "after processing move rule '{}': {}".format(rule_id, err))
            raise SystemExit

    def _log_move_action(self, message, rule_id, destination, dry_run, folder=True):
        '''
        Report which mails have been identified for moving.
        '''
        if not dry_run:
            level = logging.DEBUG
            prefix = 'moving mail'
        else:
            level = logging.INFO
            prefix = 'I would move mail'
        logging.log(level, prefix)
        logging.log(level, "    {}".format(get_message_summary(message).encode('utf8')))
        if folder:
            logging.log(level, "from '{}' to '{}'".format(rule_id, destination))
        else:
            logging.log(level, "to '{}' according to rule '{}'".format(destination, rule_id))
        #logging.debug("rule: '{}' in [{}]".format(tag, message.get_tags()))

    def _get_new_name(self, fname, destination):
        if self.rename:
            return os.path.join(
                            destination,
                            # construct a new filename, composed of a made-up ID and the flags part
                            # of the original filename.
                            str(uuid.uuid1()) + ':' + os.path.basename(fname).split(':')[-1]
                        )
        else:
            return destination


class FolderMailMover(MailMover):
    def __init__(self, max_age=0, rename=False, dry_run=False):
        query = 'folder:{folder} AND {subquery}'
        super(FolderMailMover, self).__init__(max_age, rename, dry_run, query)

    def move(self, maildir, rules):
        # identify and move messages
        logging.info("checking mails in '{}'".format(maildir))
        to_delete_fnames = []
        for query in rules.keys():
            destination = '{}/{}/cur/'.format(self.db_path, rules[query])
            main_query = self.query.format(folder=maildir, subquery=query)
            logging.debug("query: {}".format(main_query))
            messages = notmuch.Query(self.db, main_query).search_messages()
            for message in messages:
                # a single message (identified by Message-ID) can be in several
                # places; only touch the one(s) that exists in this maildir 
                all_message_fnames = message.get_filenames()
                to_move_fnames = [name for name in all_message_fnames
                                  if maildir in name]
                if not to_move_fnames:
                    continue
                self._log_move_action(message, maildir, rules[query],
                                       self.dry_run)
                for fname in to_move_fnames:
                    if self.dry_run:
                        continue
                    try:
                        shutil.copy2(fname, self._get_new_name(fname, destination))
                        to_delete_fnames.append(fname)
                    except shutil.Error as e:
                        # this is ugly, but shutil does not provide more
                        # finely individuated errors
                        if str(e).endswith("already exists"):
                            continue
                        else:
                            raise

        # remove mail from source locations only after all copies are finished
        for fname in set(to_delete_fnames):
            os.remove(fname)

        # update notmuch database
        logging.info("updating database")
        if not self.dry_run:
            self._update_db(maildir)
        else:
            logging.info("Would update database")
