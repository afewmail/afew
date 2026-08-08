# SPDX-License-Identifier: ISC
# Copyright (c) dtk <dtk@gmx.de>

import collections
import glob
import logging
import os
import shutil
import uuid
from datetime import date, datetime, timedelta
from subprocess import check_call, CalledProcessError, DEVNULL

from afew.Database import Database
from afew.utils import get_message_summary


class MailMover(Database):
    """
    Move mail files matching a given notmuch query into a target maildir folder.
    """

    def __init__(self, max_age=0, rename=False, dry_run=False, notmuch_args='', quiet=False,
                 folder_priorities=None):
        super().__init__()
        self.db = Database()
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
        self.folder_priorities = folder_priorities or {}
        self._resolution_cache = {}

    def get_new_name(self, fname, destination):
        basename = os.path.basename(fname)
        submaildir = os.path.split(os.path.split(fname)[0])[1]
        # 'auto' renames only mbsync files (UID embedded as ,U=NNN), leaving
        # offlineimap and plain maildir names untouched
        if self.rename == 'auto':
            rename = ',U=' in basename
        elif isinstance(self.rename, str):
            rename = self.rename.lower() == 'true'
        else:
            rename = bool(self.rename)
        if rename:
            parts = basename.split(':')
            if len(parts) > 1:
                flagpart = ':' + parts[-1]
            else:
                flagpart = ''
                # construct a new filename, composed of a made-up ID and the flags part
                # of the original filename.
            basename = str(uuid.uuid1()) + flagpart
        return os.path.join(destination, submaildir, basename)

    def _select_targets(self, fnames, destination):
        """Files that actually change folders, keyed by their new name.

        A file is skipped when its source vanished from disk (stale notmuch
        index entry) or when it already lives inside the destination maildir
        tree - the folder itself or one of its subfolders. The latter keeps
        'folder:PATH' prefix queries (which match PATH/sub/* as well) from
        pulling mail out of organizational subfolders into the folder root.
        """
        targets = {}
        for fname in fnames:
            if not os.path.exists(fname):
                logging.warning("source gone, skipping: {}".format(fname))
                continue
            new_name = self.get_new_name(fname, destination)
            if self._same_maildir_tree(fname, new_name):
                continue
            targets[fname] = new_name
        return targets

    @staticmethod
    def _same_maildir_tree(fname, new_name):
        """True when both paths live in the same maildir tree."""
        src_maildir = os.path.dirname(os.path.dirname(fname))
        dst_maildir = os.path.dirname(os.path.dirname(new_name))
        return src_maildir == dst_maildir or \
            src_maildir.startswith(dst_maildir + os.sep)

    def _resolve_account_folder(self, account, tag):
        """Resolve a priority key to the account's folder: the first candidate
        that exists on disk wins ('*' candidates are globs); if none exists,
        the first candidate is used (the folder must be created by the mail
        client or sync tool - afew does not create it)."""
        candidates = self.folder_priorities.get(tag) or ['']
        base = os.path.join(self.db_path, account)
        for candidate in candidates:
            if '*' in candidate:
                matches = sorted(glob.glob(os.path.join(base, candidate)))
                if matches:
                    return os.path.join(account, os.path.basename(matches[0]))
            elif os.path.isdir(os.path.join(base, candidate)):
                return os.path.join(account, candidate)
        return os.path.join(account, candidates[0])

    def _managed_folders(self, account):
        """Existing folders the mover manages for an account: INBOX plus the
        resolved priority folders."""
        folders = [os.path.join(account, 'INBOX')]
        for tag in self.folder_priorities:
            folders.append(self._resolve_account_folder(account, tag))
        return sorted(f for f in folders
                      if os.path.isdir(os.path.join(self.db_path, f)))

    def expand_rules(self, rules):
        """Expand wildcard folder keys (gmail/*) into the account's managed
        folders only: INBOX plus the resolved priority folders. Organizational
        subfolders are left alone - mail there is where the user put it."""
        expanded = collections.OrderedDict()
        for folder, folder_rules in rules.items():
            if '*' not in folder:
                expanded[folder] = folder_rules
                continue
            account = folder[:folder.index('*')].rstrip('/')
            for source in self._managed_folders(account):
                expanded[source] = folder_rules
        return expanded

    def _resolve_folder(self, maildir, tag):
        """Resolve a priority key for the maildir's account (memoized)."""
        key = (maildir, tag)
        if key not in self._resolution_cache:
            self._resolution_cache[key] = self._resolve_account_folder(
                maildir.split('/')[0], tag)
        return self._resolution_cache[key]

    def move(self, maildir, rules):
        """
        Move mails in folder maildir according to the given rules.
        """
        if '*' in maildir:
            for source, source_rules in self.expand_rules({maildir: rules}).items():
                self.move(source, source_rules)
            return
        # identify and move messages
        logging.info("checking mails in '{}'".format(maildir))
        to_delete_fnames = []
        moved = False
        for query in rules.keys():
            dest_rule = rules[query]
            if dest_rule in self.folder_priorities:
                dest_rule = self._resolve_folder(maildir, dest_rule)
            destination = '{}/{}/'.format(self.db_path, dest_rule)
            main_query = self.query.format(
                folder=maildir.replace("\"", "\\\""), subquery=query)
            logging.debug("query: {}".format(main_query))
            messages = self.db.get_messages(main_query)
            for message in messages:
                # a single message (identified by Message-ID) can be in several
                # places; only touch the one(s) that exists in this maildir
                all_message_fnames = (str(name) for name in message.filenames())
                to_move_fnames = [name for name in all_message_fnames
                                  if maildir in name]
                if not to_move_fnames:
                    continue
                targets = self._select_targets(to_move_fnames, destination)
                if not targets:
                    continue
                moved = True
                self.__log_move_action(message, maildir, dest_rule,
                                       self.dry_run)
                for fname, new_name in targets.items():
                    if self.dry_run:
                        continue
                    try:
                        shutil.copy2(fname, new_name)
                        to_delete_fnames.append(fname)
                    except shutil.SameFileError:
                        logging.warning("trying to move '{}' onto itself".format(fname))
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
        finally:
            # the external `notmuch new` bumps the database revision; any
            # handle we hold is stale and would raise on the next query.
            # drop it so the next folder - one instance may run move()
            # several times through wildcard expansion - reopens against
            # the new revision
            self.close()

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
