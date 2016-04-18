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
import uuid
from datetime import date, datetime, timedelta
from subprocess import check_call, CalledProcessError
from .Database import Database
from .utils import get_message_summary


class MailArchiver(Database):
    """
    Move mail files matching a given notmuch query into archive folders.
    """

    def __init__(self, max_age=0, rename=False, dry_run=False):
        super(MailArchiver, self).__init__()
        self.db = notmuch.Database(self.db_path)
        self.query = "folder:{folder} AND {subquery}"
        if max_age:
            days = timedelta(int(max_age))
            start = date.today() - days
            now = datetime.now()
            self.query += " AND {start}..{now}".format(start=start.strftime("%s"),
                                                       now=now.strftime("%s"))
        self.dry_run = dry_run
        self.rename = rename

    def get_new_name(self, fname, destination):
        if self.rename:
            return os.path.join(destination,
                    str(uuid.uuid1()) + ":" + os.path.basename(fname).split(":")[-1])
        else:
            return destination

    def move(self, maildir, rules):
        logging.info("checking mails in '{}'".format(maildir))
        to_delete_fnames = set()
        for query in rules.keys():
            main_query = self.query.format(folder=maildir, subquery=query)
            logging.debug("query: {}".format(main_query))
            messages = notmuch.Query(self.db, main_query).search_messages()
            for message in messages:
                # A single message (identified by Message-ID) can be in
                # several places; only touch the one(s) in this maildir.
                to_move_fnames = [name for name in message.get_filenames()
                        if maildir in name]
                if not to_move_fnames:
                    continue
                # TODO: For now only the message date is available to build
                # the destination folder name, maybe other fields should be
                # exposed as well.
                dst_folder = rules[query].format(
                        date=datetime.fromtimestamp(message.get_date()))
                dst_folder = "{}/{}/cur".format(self.db_path, dst_folder)
                self.__log_move_action(message, maildir, dst_folder, self.dry_run)
                if self.dry_run:
                    continue
                if not os.path.isdir(dst_folder):
                    logging.debug("creating directory '{}'".format(dst_folder))
                    os.makedirs(dst_folder)
                for fname in to_move_fnames:
                    try:
                        shutil.copy2(fname, self.get_new_name(fname, dst_folder))
                        to_delete_fnames.add(fname)
                    except shutil.SameFileError:
                        pass
                    except shutil.Error as e:
                        if not str(e).endswith("already exists"):
                            raise

        # Remove mail from source location
        [os.remove(fname) for fname in to_delete_fnames]

        if not self.dry_run:
            logging.info("updating database")
            self.__update_db(maildir)
        else:
            logging.info("Would update database")

    def __update_db(self, maildir):
        try:
            check_call(["notmuch", "new"])
        except CalledProcessError as err:
            logging.error("Could not update notmuch database " \
                          "after syncing maildir '{}': {}".format(maildir, err))
            raise SystemExit

    @staticmethod
    def __log_move_action(message, source, destination, dry_run):
        if dry_run:
            level = logging.INFO
            prefix = "I would move mail"
        else:
            level = logging.DEBUG
            prefix = "moving mail"
        logging.log(level, prefix)
        logging.log(level, "    {}".format(get_message_summary(message).encode("utf-8")))
        logging.log(level, "from '{}' to '{}'".format(source, destination))
