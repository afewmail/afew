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

from ..Filter import Filter, register_filter

@register_filter
class ListMailsFilter(Filter):
    message = 'Tagging mailing list posts'
    list_tag = 'lists'
    query = 'NOT tag:%s' % list_tag

    def __init__(self, whitelist=''):
        super(ListMailsFilter, self).__init__()
        self.whitelist = set(whitelist.split())

    list_id_re = re.compile(r"<(?P<list_id>[a-z0-9!#$%&'*+/=?^_`{|}~-]+)\.", re.I)
    def handle_message(self, message):
        list_id_header = message.get_header('List-Id')
        match = self.list_id_re.search(list_id_header)

        if not match:
            return

        list_id = match.group('list_id')
        self.add_tags(message, *([self.list_tag] + ([list_id] if
            list_id in self.whitelist or not self.whitelist else [])))
