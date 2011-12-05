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


import notmuch
import logging
from shutil import move
from subprocess import check_call, CalledProcessError

from .Database import Database


class TagSyncher(Database):
    '''
    Move files of tagged mails into the maildir folder corresponding to the
    respective tag.
    '''


    def __init__(self):
        super(TagSyncher, self).__init__()
        self.db = notmuch.Database(self.db_path)
        self.query = 'folder:{folder}'


    def sync(self, maildir, rules):
        '''
        Move mails in folder maildir according to the given rules.
        '''
        # identify and move messages
        logging.info("syncing tags in '{}'".format(maildir))
        messages = notmuch.Query(self.db, self.query.format(folder=maildir)).search_messages()
        for message in messages:
            mail_tags = list(message.get_tags())
            for tag in rules.keys():
                if self.__rule_matches(tag, mail_tags):
                    destination = '{}/{}/cur/'.format(self.db_path, rules[tag])
                    logging.debug("{} -- {} [{}]".format(message,
                                                  message.get_header('Subject'),
                                       message.get_filename().rsplit('/', 1)[1])
                                 )      
                    logging.debug("    MOVING TO: {}".format(destination))
                    move(message.get_filename(), destination)                                           
                    break

        # update notmuch database
        logging.info("updating database")
        try:
            check_call(['notmuch', 'new'])
        except CalledProcessError as err:
            logging.error("Could not update notmuch database " \
                          "after syncing maildir '{}': {}".format(maildir, err))
            raise SystemExit 
            

    def __rule_matches(self, test_tag, existing_tags):
        return (self.__is_positive_tag(test_tag) and test_tag in existing_tags) or \
               (self.__is_negative_tag(test_tag) and not test_tag[1:] in existing_tags)


    def __is_positive_tag(self, tag): return not self.__is_negative_tag(tag)
    def __is_negative_tag(self, tag): return tag.startswith('!')
