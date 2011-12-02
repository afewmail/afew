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
        messages = notmuch.Query(self.db, self.query.format(folder=maildir)).search_messages()
        for message in messages:
            print u"{} -- {}".format(message, message.get_header('Subject'))
            mail_tags = list(message.get_tags())
            for tag in rules.keys():
                if self.__rule_matches(tag, mail_tags):
                    print " WOULD MOVE TO: {}/{}/cur/ ".format(self.db_path,
                                                               rules[tag])
                    break


    def __rule_matches(self, test_tag, existing_tags):
        return (self.__is_positive_tag(test_tag) and test_tag in existing_tags) or \
               (self.__is_negative_tag(test_tag) and not test_tag[1:] in existing_tags)


    def __is_positive_tag(self, tag): return not self.__is_negative_tag(tag)
    def __is_negative_tag(self, tag): return tag.startswith('!')
