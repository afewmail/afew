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

from .BaseFilter import Filter
from ..NotmuchSettings import get_notmuch_new_tags, get_notmuch_new_query


class InboxFilter(Filter):
    message = 'Retags all messages not tagged as junk or killed as inbox'
    tags = ['+inbox']
    tags_blacklist = [ 'killed', 'spam' ]

    @property
    def query(self):
        '''
        Need to read the notmuch settings first. Using a property here
        so that the setting is looked up on demand.
        '''
        return get_notmuch_new_query()


    def handle_message(self, message):
        self.remove_tags(message, *get_notmuch_new_tags())
        super(InboxFilter, self).handle_message(message)
