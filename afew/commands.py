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
import optparse

from afew.Database import Database
from afew.main import main as inner_main
from afew.utils import filter_compat
from afew.FilterRegistry import all_filters
from afew.Settings import user_config_dir, get_filter_chain
from afew.Settings import get_mail_move_rules, get_mail_move_age, get_mail_move_rename
from afew.NotmuchSettings import read_notmuch_settings, get_notmuch_new_query

option_parser = optparse.OptionParser(
    usage='%prog [options] [--] [query]'
)

# the actions
action_group = optparse.OptionGroup(
    option_parser,
    'Actions',
    'Please specify exactly one action (both update actions can be specified simultaneously).'
)
action_group.add_option(
    '-t', '--tag', default=False, action='store_true',
    help='run the tag filters'
)
action_group.add_option(
    '-w', '--watch', default=False, action='store_true',
    help='continuously monitor the mailbox for new files'
)
action_group.add_option(
    '-l', '--learn', default=False,
    help='train the category with the messages matching the given query'
)
action_group.add_option(
    '-u', '--update', default=False, action='store_true',
    help='update the categories [requires no query]'
)
action_group.add_option(
    '-U', '--update-reference', default=False, action='store_true',
    help='update the reference category (takes quite some time) [requires no query]'
)
action_group.add_option(
    '-c', '--classify', default=False, action='store_true',
    help='classify each message matching the given query (to test the trained categories)'
)
action_group.add_option(
    '-m', '--move-mails', default=False, action='store_true',
    help='move mail files between maildir folders'
)
option_parser.add_option_group(action_group)

# query modifiers
query_modifier_group = optparse.OptionGroup(
    option_parser,
    'Query modifiers',
    'Please specify either --all or --new or a query string.'
    ' The default query for the update actions is a random selection of'
    ' REFERENCE_SET_SIZE mails from the last REFERENCE_SET_TIMEFRAME days.'
)
query_modifier_group.add_option(
    '-a', '--all', default=False, action='store_true',
    help='operate on all messages'
)
query_modifier_group.add_option(
    '-n', '--new', default=False, action='store_true',
    help='operate on all new messages'
)
option_parser.add_option_group(query_modifier_group)

# general options
options_group = optparse.OptionGroup(
    option_parser,
    'General options',
)
# TODO: get config via notmuch api
options_group.add_option(
    '-C', '--notmuch-config', default=None,
    help='path to the notmuch configuration file [default: $NOTMUCH_CONFIG or ~/.notmuch-config]'
)
options_group.add_option(
    '-e', '--enable-filters',
    help="filter classes to use, separated by ',' [default: filters specified in afew's config]"
)
options_group.add_option(
    '-d', '--dry-run', default=False, action='store_true',
    help="don't change the db [default: %default]"
)
options_group.add_option(
    '-R', '--reference-set-size', type='int', default=1000,
    help='size of the reference set [default: %default]'
)

options_group.add_option(
    '-T', '--reference-set-timeframe', type='int', default=30, metavar='DAYS',
    help='do not use mails older than DAYS days [default: %default]'
)

options_group.add_option(
    '-v', '--verbose', dest='verbosity', action='count', default=0,
    help='be more verbose, can be given multiple times'
)
option_parser.add_option_group(options_group)


def main():
    options, args = option_parser.parse_args()

    no_actions = len(filter_compat(None, (
        options.tag,
        options.watch,
        options.update or options.update_reference,
        options.learn,
        options.classify,
        options.move_mails
    )))
    if no_actions == 0:
        sys.exit('You need to specify an action')
    elif no_actions > 1:
        sys.exit(
            'Please specify exactly one action (both update actions can be given at once)')

    no_query_modifiers = len(filter_compat(None, (options.all,
                                                  options.new, args)))
    if no_query_modifiers == 0 and not \
       (options.update or options.update_reference or options.watch) and not \
       options.move_mails:
        sys.exit('You need to specify one of --new, --all or a query string')
    elif no_query_modifiers > 1:
        sys.exit('Please specify either --all, --new or a query string')

    read_notmuch_settings(options.notmuch_config)

    if options.new:
        query_string = get_notmuch_new_query()
    elif options.all:
        query_string = ''
    elif not (options.update or options.update_reference):
        query_string = ' '.join(args)
    elif options.update or options.update_reference:
        query_string = '%i..%i' % (
            time.time() - options.reference_set_timeframe * 24 * 60 * 60,
            time.time())
    else:
        sys.exit('Weird... please file a bug containing your command line.')

    loglevel = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
    }[min(2, options.verbosity)]
    logging.basicConfig(level=loglevel)

    sys.path.insert(0, user_config_dir)
    # py2.7 compat hack
    glob_pattern = b'*.py' if sys.version_info[0] == 2 else '*.py'
    for file_name in glob.glob1(user_config_dir,  glob_pattern):
        print('Importing user filter %r' % (file_name, ))
        __import__(file_name[:-3], level=0)

    if options.move_mails:
        options.mail_move_rules = get_mail_move_rules()
        options.mail_move_age = get_mail_move_age()
        options.mail_move_rename = get_mail_move_rename()

    with Database() as database:
        configured_filter_chain = get_filter_chain(database)
        if options.enable_filters:
            options.enable_filters = options.enable_filters.split(',')

            all_filters_set = set(all_filters.keys())
            enabled_filters_set = set(options.enable_filters)
            if not all_filters_set.issuperset(enabled_filters_set):
                sys.exit('Unknown filter(s) selected: %s' % (' '.join(
                    enabled_filters_set.difference(all_filters_set))))

            options.enable_filters = [all_filters[filter_name](database)
                                      for filter_name
                                      in options.enable_filters]
        else:
            options.enable_filters = configured_filter_chain

        inner_main(options, database, query_string)
