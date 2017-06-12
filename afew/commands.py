#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals

#
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>
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

import glob
import sys
import time
import logging
import argparse

from afew.Database import Database
from afew.main import main as inner_main
from afew.utils import filter_compat
from afew.FilterRegistry import all_filters
from afew.Settings import user_config_dir, get_filter_chain, \
        get_mail_move_rules, get_mail_move_age, get_mail_move_rename
from afew.NotmuchSettings import read_notmuch_settings, get_notmuch_new_query
from afew.version import version

parser = argparse.ArgumentParser()
parser.add_argument('-V', '--version', action='version', version=version)

# the actions
action_group = parser.add_argument_group(
    'Actions',
    'Please specify exactly one action.'
)
action_group.add_argument(
    '-t', '--tag', action='store_true',
    help='run the tag filters'
)
action_group.add_argument(
    '-w', '--watch', action='store_true',
    help='continuously monitor the mailbox for new files'
)
action_group.add_argument(
    '-m', '--move-mails', action='store_true',
    help='move mail files between maildir folders'
)

# query modifiers
query_modifier_group = parser.add_argument_group(
    'Query modifiers',
    'Please specify either --all or --new or a query string.'
)
query_modifier_group.add_argument(
    '-a', '--all', action='store_true',
    help='operate on all messages'
)
query_modifier_group.add_argument(
    '-n', '--new', action='store_true',
    help='operate on all new messages'
)
query_modifier_group.add_argument(
    'query', nargs='*', help='a notmuch query to find messages to work on'
)

# general options
options_group = parser.add_argument_group('General options')
# TODO: get config via notmuch api
options_group.add_argument(
    '-C', '--notmuch-config', default=None,
    help='path to the notmuch configuration file [default: $NOTMUCH_CONFIG or'
    ' ~/.notmuch-config]'
)
options_group.add_argument(
    '-e', '--enable-filters',
    help="filter classes to use, separated by ',' [default: filters specified"
    " in afew's config]"
)
options_group.add_argument(
    '-d', '--dry-run', default=False, action='store_true',
    help="don't change the db [default: %(default)s]"
)
options_group.add_argument(
    '-R', '--reference-set-size', type=int, default=1000,
    help='size of the reference set [default: %(default)s]'
)

options_group.add_argument(
    '-T', '--reference-set-timeframe', type=int, default=30, metavar='DAYS',
    help='do not use mails older than DAYS days [default: %(default)s]'
)

options_group.add_argument(
    '-v', '--verbose', dest='verbosity', action='count', default=0,
    help='be more verbose, can be given multiple times'
)


def main():
    args = parser.parse_args()

    no_actions = len(filter_compat(None, (
        args.tag,
        args.watch,
        args.move_mails
    )))
    if no_actions == 0:
        sys.exit('You need to specify an action')
    elif no_actions > 1:
        sys.exit('Please specify exactly one action')

    no_query_modifiers = len(filter_compat(None, (args.all,
                                                  args.new, args.query)))
    if no_query_modifiers == 0 and not args.watch \
        and not args.move_mails:
        sys.exit('You need to specify one of --new, --all or a query string')
    elif no_query_modifiers > 1:
        sys.exit('Please specify either --all, --new or a query string')

    read_notmuch_settings(args.notmuch_config)

    if args.new:
        query_string = get_notmuch_new_query()
    elif args.all:
        query_string = ''
    else:
        query_string = ' '.join(args.query)

    loglevel = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
    }[min(2, args.verbosity)]
    logging.basicConfig(level=loglevel)

    sys.path.insert(0, user_config_dir)
    # py2.7 compat hack
    glob_pattern = b'*.py' if sys.version_info[0] == 2 else '*.py'
    for file_name in glob.glob1(user_config_dir,  glob_pattern):
        logging.info('Importing user filter %r' % (file_name, ))
        __import__(file_name[:-3], level=0)

    if args.move_mails:
        args.mail_move_rules = get_mail_move_rules()
        args.mail_move_age = get_mail_move_age()
        args.mail_move_rename = get_mail_move_rename()

    with Database() as database:
        configured_filter_chain = get_filter_chain(database)
        if args.enable_filters:
            args.enable_filters = args.enable_filters.split(',')

            all_filters_set = set(all_filters.keys())
            enabled_filters_set = set(args.enable_filters)
            if not all_filters_set.issuperset(enabled_filters_set):
                sys.exit('Unknown filter(s) selected: %s' % (' '.join(
                    enabled_filters_set.difference(all_filters_set))))

            args.enable_filters = [all_filters[filter_name](database)
                                   for filter_name
                                   in args.enable_filters]
        else:
            args.enable_filters = configured_filter_chain

        inner_main(args, database, query_string)
