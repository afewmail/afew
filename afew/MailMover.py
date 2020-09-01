# SPDX-License-Identifier: ISC
# Copyright (c) dtk <dtk@gmx.de>

import logging
import os
import shutil
import uuid
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from subprocess import check_call, CalledProcessError, DEVNULL

import notmuch

from afew.Database import Database
from afew.utils import get_message_summary


class AbstractMailMover(ABC):
    def __init__(self, rename=False, dry_run=False, notmuch_args='', quiet=False):
        self.db = Database()
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


    def move(self, rule_name, rules):
        logging.info("Processing rule '{}'".format(rule_name))

        moved = False
        fnames_to_delete = []
        for query, dest_maildir in rules.items():
            destination = '{}/{}/'.format(self.db.db_path, dest_maildir)
            for (message, fname) in self.find_matching(rule_name, query):
                moved = True
                self.__log_move_action(message, dest_maildir)
                try:
                    shutil.copy2(fname, self.get_new_name(fname, destination))
                    fnames_to_delete.append(fname)
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

        # close database after we're done using it
        self.db.close()

        # remove mail from source locations only after all copies are finished
        for fname in set(fnames_to_delete):
            os.remove(fname)

        # update notmuch database
        if not self.dry_run:
            if moved:
                logging.info("updating database")
                self.__update_db()
        else:
            logging.info("Would update database")

    def __update_db(self):
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
                          "after syncing: {}".format(err))
            raise SystemExit

    def __log_move_action(self, message, destination):
        """
        Report which mails have been identified for moving.
        """
        if not self.dry_run:
            level = logging.DEBUG
            prefix = 'moving mail'
        else:
            level = logging.INFO
            prefix = 'I would move mail'
        logging.log(level, prefix)
        logging.log(level, "    {}".format(get_message_summary(message).encode('utf8')))
        logging.log(level, "to '{}'".format(destination))


class FolderMailMover(AbstractMailMover):
    def __init__(self, max_age=0, *args, **kwargs):
        super(FolderMailMover, self).__init__(*args, **kwargs)
        self.query = 'folder:"{folder}" AND {subquery}'
        if max_age:
            days = timedelta(int(max_age))
            start = date.today() - days
            now = datetime.now()
            self.query += ' AND {start}..{now}'.format(start=start.strftime('%s'),
                                                       now=now.strftime('%s'))

    def find_matching(self, maildir, query):
        main_query = self.query.format(
            folder=maildir.replace('"', '\\"'),
            subquery=query
        )
        for message in self.db.do_query(main_query).search_messages():
            # a single message (identified by Message-ID) can be in several
            # places; only touch the one(s) that exists in this maildir
            for fname in [fname for fname in message.get_filenames() if maildir in fname]:
                yield (message, fname)
