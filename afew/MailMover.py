# SPDX-License-Identifier: ISC
# Copyright (c) dtk <dtk@gmx.de>

import logging
import os
import shutil
import uuid
from datetime import date, datetime, timedelta
from subprocess import check_call, CalledProcessError, DEVNULL

import notmuch

from afew.Database import Database
from afew.utils import get_message_summary


class MailMover(Database):
    """
    Move mail files matching a given notmuch query into a target maildir folder.
    """

    def __init__(self, max_age=0, rename=False, dry_run=False, notmuch_args='', quiet=False):
        super().__init__()
        self.db = notmuch.Database(self.db_path)
        self.query = 'folder:"{folder}" AND {subquery}'
        if max_age:
            days = timedelta(int(max_age))
            start = date.today() - days
            now = datetime.now()
            self.query += ' AND {start}..{now}'.format(start=start.strftime('%s'),
                                                       now=now.strftime('%s'))
        self.dry_run = dry_run
        self.rename = rename
        self.notmuch_args = notmuch_args
        self.quiet = quiet

    def get_new_name(self, fname, destination):
        basename = os.path.basename(fname)
        submaildir = os.path.split(os.path.split(fname)[0])[1]
        if self.rename:
            parts = basename.split(':')
            if len(parts) > 1:
                flagpart = ':' + parts[-1]
            else:
                flagpart = ''
                # construct a new filename, composed of a made-up ID and the flags part
                # of the original filename.
            basename = str(uuid.uuid1()) + flagpart
        return os.path.join(destination, submaildir, basename)

    def move(self, maildir, rules):
        """
        Move mails in folder maildir according to the given rules.
        """
        # identify and move messages
        logging.info("checking mails in '{}'".format(maildir))
        to_delete_fnames = []
        moved = False
        for query in rules.keys():
            destination = '{}/{}/'.format(self.db_path, rules[query])
            main_query = self.query.format(
                folder=maildir.replace("\"", "\\\""), subquery=query)
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
                moved = True
                self.__log_move_action(message, maildir, rules[query],
                                       self.dry_run)
                for fname in to_move_fnames:
                    if self.dry_run:
                        continue
                    try:
                        shutil.copy2(fname, self.get_new_name(fname, destination))
                        to_delete_fnames.append(fname)
                    except shutil.SameFileError:
                        logging.warn("trying to move '{}' onto itself".format(fname))
                        continue
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
        if not self.dry_run:
            if moved:
                logging.info("updating database")
                self.__update_db(maildir)
        else:
            logging.info("Would update database")

    def __update_db(self, maildir):
        """
        Update the database after mail files have been moved in the filesystem.
        """
        try:
            if self.quiet:
                check_call(['notmuch', 'new'] + self.notmuch_args.split(), stdout=DEVNULL, stderr=DEVNULL)
            else:
                check_call(['notmuch', 'new'] + self.notmuch_args.split())
        except CalledProcessError as err:
            logging.error("Could not update notmuch database "
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
        logging.log(level, "    {}".format(get_message_summary(message).encode('utf8')))
        logging.log(level, "from '{}' to '{}'".format(source, destination))
