# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals

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

from .BaseFilter import Filter
from ..NotmuchSettings import notmuch_settings
import re
import shlex


class FolderNameFilter(Filter):
    message = 'Tags all new messages with their folder'

    def __init__(self, database, folder_blacklist='', folder_transforms='',
            maildir_separator='.', folder_explicit_list=''):
        super(FolderNameFilter, self).__init__(database)

        self.__filename_pattern = '{mail_root}/(?P<maildirs>.*)/(cur|new)/[^/]+'.format(
            mail_root=notmuch_settings.get('database', 'path').rstrip('/'))
        self.__folder_explicit_list = set(folder_explicit_list.split())
        self.__folder_blacklist = set(folder_blacklist.split())
        self.__folder_transforms = self.__parse_transforms(folder_transforms)
        self.__maildir_separator = maildir_separator


    def handle_message(self, message):
        maildirs = re.match(self.__filename_pattern, message.get_filename())
        if maildirs:
            folders = set(maildirs.group('maildirs').split(self.__maildir_separator))
            self.log.debug('found folders {} for message {!r}'.format(
                folders, message.get_header('subject')))

            # remove blacklisted folders
            clean_folders = folders - self.__folder_blacklist
            if self.__folder_explicit_list:
                # only explicitly listed folders
                clean_folders &= self.__folder_explicit_list
            # apply transformations
            transformed_folders = self.__transform_folders(clean_folders)

            self.add_tags(message, *transformed_folders)


    def __transform_folders(self, folders):
        '''
        Transforms the given collection of folders according to the transformation rules.
        '''
        transformations = set()
        for folder in folders:
            if folder in self.__folder_transforms:
                transformations.add(self.__folder_transforms[folder])
            else:
                transformations.add(folder)
        return transformations


    def __parse_transforms(self, transformation_description):
        '''
        Parses the transformation rules specified in the config file.
        '''
        transformations = dict()
        for rule in shlex.split(transformation_description):
            folder, tag = rule.split(':')
            transformations[folder] = tag
        return transformations

