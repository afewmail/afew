# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

import sys

from afew.MailMover import FolderMailMover

try:
    from .files import watch_for_new_files, quick_find_dirs_hack
except ImportError:
    watch_available = False
else:
    watch_available = True


def main(options, database, query_string):
    if options.tag:
        for filter_ in options.enable_filters:
            filter_.run(query_string)
            filter_.commit(options.dry_run)
    elif options.watch:
        if not watch_available:
            sys.exit('Sorry, this feature requires Linux and pyinotify')
        watch_for_new_files(options, database,
                            quick_find_dirs_hack(database.db_path))
    elif options.move_mails:
        if options.mail_move_kind == 'folder':
            mover_class = FolderMailMover
        else:
            sys.exit('Mail mover kind {:r} is not recognized'.format(options.mail_move_kind))

        for maildir, rules in options.mail_move_rules.items():
            mover = mover_class(
                max_age=options.mail_move_age,
                rename=options.mail_move_rename,
                dry_run=options.dry_run,
                notmuch_args=options.notmuch_args
            )
            mover.move(maildir, rules)
    else:
        sys.exit('Weird... please file a bug containing your command line.')
