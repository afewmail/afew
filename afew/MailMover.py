# -*- coding: utf-8 -*-
# SPDX-License-Identifier: ISC
# Copyright (c) dtk <dtk@gmx.de>
"""This module contain the MailMover class"""

import os
import logging
import shutil
import sys
from subprocess import check_call, CalledProcessError
from datetime import date, datetime, timedelta
import uuid
import notmuch
from .Database import Database
from .utils import get_message_summary


class MailMover(Database):
    '''
    Move mail files matching a given notmuch query to a target maildir folder.
    '''


    def __init__(self, max_age=0, rename = False, dry_run=False, notmuch_args=''):
        super(MailMover, self).__init__()
        self.db = notmuch.Database(self.db_path)
        self.query = 'folder:"{folder}" AND {subquery}'
        if max_age:
            days = timedelta(int(max_age))
            start = date.today() - days
            now = datetime.now()
            self.query += ' AND {start}..{now}'.format(
                start=start.strftime('%s'),
                now=now.strftime('%s'))
        self.dry_run = dry_run
        self.rename = rename
        self.notmuch_args = notmuch_args

    """ return the new name """
    def get_new_name(self, fname, destination):
        basename = os.path.basename(fname)
        submaildir =  os.path.split(os.path.split(fname)[0])[1]
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

    """ Move mails in folder maildir according to the given rules. """
    def move(self, maildir, rules):
        '''
        Move mails in folder maildir according to the given rules.
        '''
        # identify and move messages
        logging.info("checking mails in '{}'".format(maildir))
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
                to_move_fnames = [
                    name for name in all_message_fnames
                    if maildir in name]
                if not to_move_fnames:
                    continue
                for fname in to_move_fnames:
                    if self.dry_run:
                        continue
                    else:
                        moved = self.moveMail(fname, destination, True)
        # Return the moved flag
        return moved

    """ Action of moving a mail and upgrade the DB """
    def moveMail(self, mailFrom, mailTo, upgradeDatabase):
        output = False
        """ We need to check that we are not moving a file to itself """
        if mailFrom == mailTo:
            logging.error("Can not move mail to itself: {} -> {}".format(
                mailFrom,
                mailTo))
            raise SystemExit
        else:
            try:
                " mailFrom must be a file "
                if not os.path.isfile(mailFrom):
                    logging.error("mailFrom not a file: {}".format(mailFrom))
                    raise SystemExit
                " mailTo must be a directory "
                if not os.path.isdir(mailTo):
                    logging.error("mailTo not a dir: {}".format(mailTo))
                    raise SystemExit
                filename = os.path.basename(mailFrom)
                logging.info("Copy original mail: {}".format(filename))
                logging.info("{} -> {}".format(
                    os.path.dirname(mailFrom),
                    os.path.dirname(mailTo)))
                # 1 COPY
                shutil.copy2(mailFrom, mailTo)
                mailToFile = os.path.join(mailTo, filename)
                if upgradeDatabase:
                    self.db = notmuch.Database(self.db_path,
                                               mode=notmuch.Database.MODE.READ_WRITE)
                    logging.info("Add new copy to the DB: {}".format(mailToFile))
                    notmuch.Database.add_message(self.db, mailToFile)
                    self.db = notmuch.Database(self.db_path)
                logging.info("Delete original file: {}".format(mailFrom))
                os.remove(mailFrom)
                # 3 REMOVE ORIGINAL
                if upgradeDatabase:
                    self.db = notmuch.Database(self.db_path,
                                               mode=notmuch.Database.MODE.READ_WRITE)
                    logging.info("Cleanup the original mail in DB")
                    # 4 REMOVE ORIGINAL FROM DB
                    notmuch.Database.remove_message(self.db, mailFrom)
                    self.db = notmuch.Database(self.db_path)
                output = True
            except IOError as e:
                logging.error("Error IO: {}".format(e))
                raise SystemExit
            except shutil.Error as e:
                logging.error("shutil: {}".format(e))
                raise SystemExit
            except OSError as e:
                logging.error("OS: {}".format(e))
                raise SystemExit
            except notmuch.NotmuchError as e:
                logging.error("notmuch: {}".format(e.status))
                raise SystemExit
        return output

    #
    # private:
    #

    def __update_db(self, maildir):
        '''
        Update the database after mail files have been moved in the filesystem.
        '''
        try:
            check_call(['notmuch', 'new'] + self.notmuch_args.split())
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
        logging.log(level, "    {}".format(get_message_summary(message).encode('utf8')))
        logging.log(level, "from '{}' to '{}'".format(source, destination))
        #logging.debug("rule: '{}' in [{}]".format(tag, message.get_tags()))
