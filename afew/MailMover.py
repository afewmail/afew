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


class MailMover(Database):
    '''
    Move mail files matching a given notmuch query into a target maildir folder.
    '''


    def __init__(self, max_age=0, dry_run=False):
        super(MailMover, self).__init__()
        self.db = notmuch.Database(self.db_path)
        self.query = '{subquery}'
        if max_age:
            days = timedelta(int(max_age))
            start = date.today() - days
            now = datetime.now()
            self.query += ' AND {start}..{now}'.format(start=start.strftime('%s'),
                                                       now=now.strftime('%s'))
        self.dry_run = dry_run


    def move(self, rule_id, rules):
        '''
        Move mails in folder maildir according to the given rules.
        '''
        # identify and move messages
        logging.info("Processing rule '{}'".format(rule_id))
        to_delete_fnames = []
        for query in rules.keys():
            destination = '{}/{}/cur/'.format(self.db_path, rules[query])
            main_query = self.query.format(subquery=query)
            logging.debug("query: {}".format(main_query))
            messages = notmuch.Query(self.db, main_query).search_messages()
            for message in messages:
                # a single message (identified by Message-ID) can be in several
                # places; only touch the one(s) that exists in this maildir
                to_move_fnames = [name for name in message.get_filenames()]
                if not to_move_fnames:
                    continue
                self.__log_move_action(message, rule_id, rules[query],
                                       self.dry_run)
                for fname in to_move_fnames:
                    if self.dry_run:
                        continue
                    try:
                        shutil.copy2(fname, destination)
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
            self.__update_db(rule_id)
        else:
            logging.info("Would update database")


    #
    # private:
    #

    def __update_db(self, rule_id):
        '''
        Update the database after mail files have been moved in the filesystem.
        '''
        try:
            check_call(['notmuch', 'new'])
        except CalledProcessError as err:
            logging.error("Could not update notmuch database " \
                          "after syncing moving rule '{}': {}".format(rule_id, err))
            raise SystemExit


    def __log_move_action(self, message, rule_id, destination, dry_run):
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
        logging.log(level, "according to rule '{}' to '{}'".format(rule_id, destination))
        #logging.debug("rule: '{}' in [{}]".format(tag, message.get_tags()))

