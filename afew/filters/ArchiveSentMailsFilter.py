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

from ..Filter import Filter, register_filter
from ..NotmuchSettings import notmuch_settings

@register_filter
class ArchiveSentMailsFilter(Filter):
    message = 'Archiving all mails sent by myself'

    def __init__(self, *args, **kwargs):
        super(ArchiveSentMailsFilter, self).__init__(*args, **kwargs)

        my_addresses = set()
        my_addresses.add(notmuch_settings.get('user', 'primary_email'))
        if notmuch_settings.has_option('user', 'other_email'):
            my_addresses.update(filter(None, notmuch_settings.get('user', 'other_email').split(';')))

        self.query = ' OR '.join('from:"%s"' % address for address in my_addresses)

    def handle_message(self, message):
        self.remove_tags(message, 'new')
