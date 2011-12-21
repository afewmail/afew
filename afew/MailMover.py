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
from shutil import move
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
        self.query = 'folder:{folder} AND {subquery}'
        if max_age:
            days = timedelta(int(max_age))
            start = date.today() - days
            now = datetime.now()
            self.query += ' AND {start}..{now}'.format(start=start.strftime('%s'),
                                                       now=now.strftime('%s'))
        self.dry_run = dry_run


    def move(self, maildir, rules):
        '''
        Move mails in folder maildir according to the given rules.
        '''
        # identify and move messages
        logging.info("checking mails in '{}'".format(maildir))
        for query in rules.keys():
            destination = '{}/{}/cur/'.format(self.db_path, rules[query])
            main_query = self.query.format(folder=maildir, subquery=query)
            logging.debug("query: {}".format(main_query))
            messages = notmuch.Query(self.db, main_query).search_messages()
            for message in messages:
                if not self.dry_run:
                    self.__log_move_action(message, maildir, rules[query], self.dry_run)
                    move(message.get_filename(), destination)
                else:
                    self.__log_move_action(message, maildir, rules[query], self.dry_run)
                break

        # update notmuch database
        logging.info("updating database")
        if not self.dry_run:
            self.__update_db(maildir)
        else:
            logging.info("Would update database")


    #
    # private:
    #

    def __update_db(self, maildir):
        '''
        Update the database after mail files have been moved in the filesystem.
        '''
        try:
            check_call(['notmuch', 'new'])
        except CalledProcessError as err:
            logging.error("Could not update notmuch database " \
                          "after syncing maildir '{}': {}".format(maildir, err))
            raise SystemExit


    def __log_move_action(self, message, source, destination, dry_run):
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
        logging.log(level, "    {}".format(get_message_summary(message)))
        logging.log(level, "from '{}' to '{}'".format(source, destination))
        #logging.debug("rule: '{}' in [{}]".format(tag, message.get_tags()))

