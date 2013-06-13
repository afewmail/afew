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

import re

from ..utils import filter_compat
from .BaseFilter import Filter
from ..NotmuchSettings import notmuch_settings


class SentMailsFilter(Filter):
    message = 'Tagging all mails sent by myself to others'
    _bare_email_re = re.compile(r"[^<]*<(?P<email>[^@<>]+@[^@<>]+)>")

    def __init__(self, database, sent_tag='', to_transforms=''):
        super(SentMailsFilter, self).__init__(database)

        my_addresses = set()
        my_addresses.add(notmuch_settings.get('user', 'primary_email'))
        if notmuch_settings.has_option('user', 'other_email'):
            my_addresses.update(filter_compat(None, notmuch_settings.get('user', 'other_email').split(';')))

        self.query = (
            '(' +
            ' OR '.join('from:"%s"' % address for address in my_addresses)
            + ') AND NOT (' +
            ' OR '.join('to:"%s"'   % address for address in my_addresses)
            + ')'
        )

        self.sent_tag = sent_tag
        self.to_transforms = to_transforms
        if to_transforms:
            self.__email_to_tags = self.__build_email_to_tags(to_transforms)


    def handle_message(self, message):
        if self.sent_tag:
            self.add_tags(message, self.sent_tag)
        if self.to_transforms:
            for header in ('To', 'Cc', 'Bcc'):
                email = self.__get_bare_email(message.get_header(header))
                for tag in self.__pick_tags(email):
                    self.add_tags(message, tag)
                else:
                    break


    def __build_email_to_tags(self, to_transforms):
        email_to_tags = dict()

        for rule in to_transforms.split():
            if ':' in rule:
                email, tags = rule.split(':')
                email_to_tags[email] = tuple(tags.split(';'))
            else:
                email = rule
                email_to_tags[email] = tuple()

        return email_to_tags


    def __get_bare_email(self, email):
        if not '<' in email:
            return email
        else:
            match = self._bare_email_re.search(email)
            return match.group('email')


    def __pick_tags(self, email):
        if email in self.__email_to_tags:
            tags = self.__email_to_tags[email]
            if tags:
                return tags
            else:
                user_part, domain_part = email.split('@')
                return (user_part, )

        return tuple()
