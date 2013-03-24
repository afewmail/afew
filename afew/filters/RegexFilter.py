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
class RegexFilter(Filter):
    message = 'your regex'
    query = ''
    header_field = 'To'
    regex_string = r''
    regex_group = None
    generic_tag = None

    def __init__(self):
        self.regex = re.compile(self.regex_string, re.IGNORE_CASE)

    def handle_message(self, message):
        if self.header_field.lower() == 'to':
            header_field_list = ['To', 'Cc', 'Bcc']
        else:
            header_field_list = [self.header_field]

        for header in header_field_list:
            header_line = message.get_header(self.header_field)
            match = self.regex.search(header_line)

            if match:
                if self.generic_tag:
                    self.add_tags(message, self.generic_tag,
                        match.group(self.regex_group))
                else:
                    self.add_tags(message, match.group(self.regex_group))
