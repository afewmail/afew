# coding=utf-8

#
# Copyright (c) dtk <dtk@gmx.de>
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
import re
import logging

@register_filter
class FolderNameFilter(Filter):
    message = 'Tags all new messages with their folder'
    folder_blacklist = ['INBOX']

    def handle_message(self, message):
        filename_pattern = '(/.+)/(?P<maildirs>.*)/(cur|new)/[^/]+'
        maildirs = re.match(filename_pattern, message.get_filename())
        if maildirs:
            #todo: make separator configurable
            tags = maildirs.group('maildirs').split('.')
            logging.debug('found tags {0} for message \'{1}\''.format(tags, message.get_filename()))
            # remove blacklisted folder
            tags = set(tags) - set(self.folder_blacklist)
            self.add_tags(message, *tags)
        else:
            #todo: error handling in tag filters?
            logging.error('Could not extract folder names from message \'{0}\''.format(message))
