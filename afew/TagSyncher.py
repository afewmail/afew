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
from .utils import get_message_summary


class TagSyncher(Database):
    '''
    Move files of tagged mails into the maildir folder corresponding to the
    respective tag.
    '''


    def __init__(self, dry_run=False):
        super(TagSyncher, self).__init__()
        self.db = notmuch.Database(self.db_path)
        self.query = 'folder:{folder}'
        self.dry_run = dry_run


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
                    if not self.dry_run:
                        self.__log_move_action(message, maildir, tag, rules, self.dry_run)
                        move(message.get_filename(), destination)                                           
                    else:
                        self.__log_move_action(message, maildir, tag, rules, self.dry_run)
                    break

        # update notmuch database
        logging.info("updating database")
        if not self.dry_run:
            self.__update_db(maildir)
        else:
            logging.info("Would update database")


    #
    # private:
    #

    def __rule_matches(self, test_tag, existing_tags):
        '''
        Returns true if a mail is tagged with a positive tag or
                               is not tagged with a negative tag.
        '''
        return (self.__is_positive_tag(test_tag) and test_tag in existing_tags) or \
               (self.__is_negative_tag(test_tag) and not test_tag[1:] in existing_tags)


    def __is_positive_tag(self, tag): return not self.__is_negative_tag(tag)
    def __is_negative_tag(self, tag): return tag.startswith('!')


    def __update_db(self, maildir):
        '''
        Update the database after mail files have been moved in the filesystem.
        '''
        try:
            check_call(['notmuch', 'new'])
        except CalledProcessError as err:
            logging.error("Could not update notmuch database " \
                          "after syncing maildir '{}': {}".format(maildir, err))
            raise SystemExit


    def __log_move_action(self, message, maildir, tag, rules, dry_run):
        '''
        Report which mails have been identified for moving.
        '''
        if not dry_run:
            level = logging.DEBUG
            prefix = 'moving mail'
        else:
            level = logging.INFO
            prefix = 'I would move mail'
        logging.log(level, prefix)
        logging.log(level, "    {}".format(get_message_summary(message)))
        logging.log(level, "from '{}' to '{}'".format(maildir, rules[tag]))
        logging.debug("rule: '{}' in [{}]".format(tag, message.get_tags()))
            
