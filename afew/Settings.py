# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

import os
import re
import collections
import shlex

from afew.configparser import ConfigParser
from afew.FilterRegistry import all_filters

user_config_dir = os.path.join(os.environ.get('XDG_CONFIG_HOME',
                                              os.path.expanduser('~/.config')),
                               'afew')
user_config_dir = os.path.expandvars(user_config_dir)

settings = ConfigParser()
# preserve the capitalization of the keys.
settings.optionxform = str

settings.readfp(open(os.path.join(os.path.dirname(__file__), 'defaults', 'afew.config')))
settings.read(os.path.join(user_config_dir, 'config'))

# All the values for keys listed here are interpreted as ;-delimited lists
value_is_a_list = ['tags', 'tags_blacklist']
folder_mail_mover_section = 'MailMover'

section_re = re.compile(r'^(?P<name>[a-z_][a-z0-9_]*)(\((?P<parent_class>[a-z_][a-z0-9_]*)\)|\.(?P<index>\d+))?$', re.I)
def get_filter_chain(database):
    filter_chain = []

    for section in settings.sections():
        if section in ['global', folder_mail_mover_section]:
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
                raise NameError(
                    'Parent class %r not found in filter type definition %r.' % (match.group('parent_class'), section))

            new_type = type(match.group('name'), (parent_class,), kwargs)
            all_filters[match.group('name')] = new_type
        else:
            try:
                klass = all_filters[match.group('name')]
            except KeyError:
                raise NameError('Filter type %r not found.' % match.group('name'))
            filter_chain.append(klass(database, **kwargs))

    return filter_chain

def get_mail_move_kind():
    return settings.get('global', 'mail_mover_kind', fallback='folder')

def get_mail_move_section(kind):
    if kind == 'folder':
        return folder_mail_mover_section

def get_mail_move_rules(kind):
    section = get_mail_move_section(kind)
    if kind == 'query':
        rule_id_key = 'rules'
    else:
        rule_id_key = 'folders'

    rule_pattern = re.compile(r"'(.+?)':((?P<quote>['\"])(.*?)(?P=quote)|\S+)")
    if settings.has_option(section, rule_id_key):
        all_rules = collections.OrderedDict()

        for folder in shlex.split(settings.get(section, rule_id_key)):
            if settings.has_option(section, folder):
                rules = collections.OrderedDict()
                raw_rules = re.findall(rule_pattern,
                                       settings.get(section, folder))
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

def get_mail_move_age(section):
    max_age = 0
    if settings.has_option(section, 'max_age'):
        max_age = settings.get(section, 'max_age')
    return max_age

def get_mail_move_rename(section):
    rename = False
    if settings.has_option(section, 'rename'):
        rename = settings.get(section, 'rename').lower() == 'true'
    return rename
