# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from .BaseFilter import Filter

import re


class HeaderMatchingFilter(Filter):
    message = 'Tagging based on specific header values matching a given RE'
    header = None
    pattern = None

    def __init__(self, database, **kwargs):
        super(HeaderMatchingFilter, self).__init__(database, **kwargs)
        if self.pattern is not None:
            self.pattern = re.compile(self.pattern, re.I)

    def handle_message(self, message):
        if self.header is not None and self.pattern is not None:
            if not self._tag_blacklist.intersection(message.get_tags()):
                value = message.get_header(self.header)
                match = self.pattern.search(value)
                if match:
                    sub = (lambda tag:
                        tag.format(**match.groupdict()).lower())
                    self.remove_tags(message, *map(sub, self._tags_to_remove))
                    self.add_tags(message, *map(sub, self._tags_to_add))
