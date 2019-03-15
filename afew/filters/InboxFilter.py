# -*- coding: utf-8 -*-
# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>
from __future__ import print_function, absolute_import, unicode_literals

from .BaseFilter import Filter
from ..NotmuchSettings import get_notmuch_new_tags, get_notmuch_new_query


class InboxFilter(Filter):
    message = 'Retags all messages not tagged as junk or killed as inbox'
    tags = ['+inbox']
    tags_blacklist = [ 'killed', 'spam' ]

    @property
    def query(self):
        '''
        Need to read the notmuch settings first. Using a property here
        so that the setting is looked up on demand.
        '''
        return get_notmuch_new_query()


    def handle_message(self, message):
        self.remove_tags(message, *get_notmuch_new_tags())
        super().handle_message(message)
