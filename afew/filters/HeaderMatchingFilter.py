# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from ..Filter import Filter, register_filter

import re


@register_filter
class HeaderMatchingFilter(Filter):
    message = 'Tagging based on specific header values matching a given RE'

    def __init__(self, header, pattern, **kwargs):
        super(HeaderMatchingFilter, self).__init__(**kwargs)
        self.header = header
        self.pattern = pattern
        self.compiled_pattern = re.compile(pattern, re.I)

    def handle_message(self, message):
        value = message.get_header(self.header)
        match = self.compiled_pattern.search(value)

        if match:
            sub = lambda tag: tag.format(**match.groupdict())
            self.remove_tags(message, *map(sub, self._tags_to_remove))
            self.add_tags(message, *map(sub, self._tags_to_add))
