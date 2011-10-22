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
from ..NotmuchSettings import notmuch_settings
import re
import logging

@register_filter
class FolderNameFilter(Filter):
    message = 'Tags all new messages with their folder'
    
    def __init__(self, folder_blacklist='', maildir_separator='.'):
        super(FolderNameFilter, self).__init__()

        self.__filename_pattern = '{mail_root}/(?P<maildirs>.*)/(cur|new)/[^/]+'.format(
            mail_root=notmuch_settings.get('database', 'path').rstrip('/'))
        
        self.__folder_blacklist = set(folder_blacklist.split())
        self.__maildir_separator = maildir_separator


    def handle_message(self, message):
        maildirs = re.match(self.__filename_pattern, message.get_filename())
        if maildirs:
            tags = set(maildirs.group('maildirs').split(self.__maildir_separator))
            logging.debug('found tags {0} for message \'{1}\''.format(tags, message.get_header('subject').encode('utf8')))
            # remove blacklisted folders
            tags = tags - self.__folder_blacklist
            self.add_tags(message, *tags)
        else:
            logging.error('Could not extract folder names from message \'{0}\''.format(message))
