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
import collections

from .configparser import SafeConfigParser
from afew.FilterRegistry import all_filters

user_config_dir = os.path.join(os.environ.get('XDG_CONFIG_HOME',
                                              os.path.expanduser('~/.config')),
                               'afew')
user_config_dir=os.path.expandvars(user_config_dir)

settings = SafeConfigParser()
# preserve the capitalization of the keys.
settings.optionxform = str

settings.readfp(open(os.path.join(os.path.dirname(__file__), 'defaults', 'afew.config')))
settings.read(os.path.join(user_config_dir, 'config'))

# All the values for keys listed here are interpreted as ;-delimited lists
value_is_a_list = ['tags', 'tags_blacklist']
mail_mover_section = 'MailMover'

section_re = re.compile(r'^(?P<name>[a-z_][a-z0-9_]*)(\((?P<parent_class>[a-z_][a-z0-9_]*)\)|\.(?P<index>\d+))?$', re.I)
def get_filter_chain(database):
    filter_chain = []

    for section in settings.sections():
        if section == 'global' or section == mail_mover_section:
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
            except KeyError:
                raise NameError('Parent class %r not found in filter type definition %r.' % (match.group('parent_class'), section))

            new_type = type(match.group('name'), (parent_class, ), kwargs)
            all_filters[match.group('name')] = new_type
        else:
            try:
                klass = all_filters[match.group('name')]
            except KeyError:
                raise NameError('Filter type %r not found.' % match.group('name'))
            filter_chain.append(klass(database, **kwargs))

    return filter_chain

def get_mail_move_rules():
    rule_pattern = re.compile(r"'(.+?)':((?P<quote>['\"])(.*?)(?P=quote)|\S+)")
    if settings.has_option(mail_mover_section, 'folders'):
        all_rules = collections.OrderedDict()

        for folder in settings.get(mail_mover_section, 'folders').split():
            if settings.has_option(mail_mover_section, folder):
                rules = collections.OrderedDict()
                raw_rules = re.findall(rule_pattern,
                                       settings.get(mail_mover_section, folder))
                for rule in raw_rules:
                    query = rule[0]
                    destination = rule[3] or rule[1]
                    rules[query] = destination
                all_rules[folder] = rules
            else:
                raise NameError("No rules specified for maildir '{}'.".format(folder))

        return all_rules
    else:
        raise NameError("No folders defined to move mails from.")

def get_mail_move_age():
    max_age = 0
    if settings.has_option(mail_mover_section, 'max_age'):
        max_age = settings.get(mail_mover_section, 'max_age')
    return max_age

def get_mail_move_rename():
    rename = False
    if settings.has_option(mail_mover_section, 'rename'):
        rename = settings.get(mail_mover_section, 'rename').lower() == 'true'
    return rename
