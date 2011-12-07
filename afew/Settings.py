# coding=utf-8

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
import ConfigParser
from collections import OrderedDict

from .Filter import all_filters, register_filter

tag_syncher = 'TagSyncher'
sync_folders = 'folders'

settings = ConfigParser.SafeConfigParser()
# preserve the capitalization of the keys.
settings.optionxform = str
settings.readfp(open(os.path.join(os.path.dirname(__file__), 'defaults', 'afew.config')))
settings.read(os.path.join(os.environ.get('XDG_CONFIG_HOME',
                                          os.path.expanduser('~/.config')),
                           'afew', 'config'))

section_re = re.compile(r'''^(?P<name>[a-z_][a-z0-9_]*)(\((?P<parent_class>[a-z_][a-z0-9_]*)\)|\.(?P<index>\d+))?$''', re.I)
def get_filter_chain():
    filter_chain = []

    for section in settings.sections():
        if section == 'global' or section == tag_syncher:
            continue

        match = section_re.match(section)
        if not match:
            raise SyntaxError('Malformed section title %r.' % section)

        if match.group('parent_class'):
            try:
                parent_class = all_filters[match.group('parent_class')]
            except KeyError as e:
                raise NameError('Parent class %r not found in filter type definition %r.' % (match.group('parent_class'), section))

            new_type = type(match.group('name'), (parent_class, ), dict(settings.items(section)))
            register_filter(new_type)
        else:
            try:
                klass = all_filters[match.group('name')]
            except KeyError as e:
                raise NameError('Filter type %r not found.' % match.group('name'))

            filter_chain.append(klass(**dict(settings.items(section))))

    return filter_chain


def get_tag_sync_rules():
    if settings.has_option(tag_syncher, sync_folders):
        all_rules = OrderedDict()

        for folder in settings.get(tag_syncher, sync_folders).split():
            if settings.has_option(tag_syncher, folder):
                rules = OrderedDict()
                for rule in settings.get(tag_syncher, folder).split():
                    tag, destination = rule.split(':')
                    rules[tag] = destination
                all_rules[folder] = rules
            else:
                raise NameError("No rules specified for maildir '{}'.".format(folder))

        return all_rules
    else:
        raise NameError("No folders for synching your tags have been defined.")
