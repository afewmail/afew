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

import os
import re
import functools
from collections import OrderedDict

from .configparser import SafeConfigParser
from .Filter import all_filters, register_filter

# config values for the MailMover
mail_mover = 'MailMover'
move_folders = 'folders'
move_age = 'max_age'

settings = SafeConfigParser()
# preserve the capitalization of the keys.
settings.optionxform = str

settings.readfp(open(os.path.join(os.path.dirname(__file__), 'defaults', 'afew.config')))
settings.read(os.path.join(os.environ.get('XDG_CONFIG_HOME',
                                          os.path.expanduser('~/.config')),
                           'afew', 'config'))

'All the values for keys listed here are interpreted as ';'-delimited lists'
value_is_a_list = ['tags']

section_re = re.compile(r'''^(?P<name>[a-z_][a-z0-9_]*)(\((?P<parent_class>[a-z_][a-z0-9_]*)\)|\.(?P<index>\d+))?$''', re.I)
def get_filter_chain():
    filter_chain = []

    for section in settings.sections():
        if section == 'global' or section == mail_mover:
            continue

        match = section_re.match(section)
        if not match:
            raise SyntaxError('Malformed section title %r.' % section)

        kwargs = dict(
            (key, settings.get(section, key))
            if key not in value_is_a_list else
            (key, settings.get_list(section, key))
            for key in settings.options(section)
        )

        if match.group('parent_class'):
            try:
                parent_class = all_filters[match.group('parent_class')]
            except KeyError as e:
                raise NameError('Parent class %r not found in filter type definition %r.' % (match.group('parent_class'), section))

            new_type = type(match.group('name'), (parent_class, ), kwargs)
            register_filter(new_type)
        else:
            try:
                klass = all_filters[match.group('name')]
            except KeyError as e:
                raise NameError('Filter type %r not found.' % match.group('name'))

            filter_chain.append(klass(**kwargs))

    return filter_chain


def get_mail_move_rules():
    rule_pattern = re.compile("'(.+?)':(\S+)")
    query_target_pattern = re.compile("")
    if settings.has_option(mail_mover, move_folders):
        all_rules = OrderedDict()

        for folder in settings.get(mail_mover, move_folders).split():
            if settings.has_option(mail_mover, folder):
                rules = OrderedDict()
                raw_rules = re.findall(rule_pattern,
                                       settings.get(mail_mover, folder))
                for rule in raw_rules:
                    rules[rule[0]] = rule[1]
                all_rules[folder] = rules
            else:
                raise NameError("No rules specified for maildir '{}'.".format(folder))

        return all_rules
    else:
        raise NameError("No folders defined to move mails from.")


def get_mail_move_age():
    max_age = 0
    if settings.has_option(mail_mover, move_age):
        max_age = settings.get(mail_mover, move_age)
    return max_age
