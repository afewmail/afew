# -*- coding: utf-8 -*-
# SPDX-License-Identifier: ISC
# Copyright (c) Amadeusz Zolnowski <aidecoe@aidecoe.name>

from __future__ import print_function, absolute_import, unicode_literals

import dkim

from .BaseFilter import Filter


def verify_dkim(path):
    '''
    Verify DKIM signature of an e-mail file.

    :param path: Path to the e-mail file.
    :returns: Whether DKIM signature is valid or not.
    '''
    with open(path, 'rb') as message_file:
        message_bytes = message_file.read()

    return dkim.verify(message_bytes)


class DKIMValidityFilter(Filter):
    '''
    Verifies DKIM signature of an e-mail which has DKIM header.
    '''
    message = 'Verify DKIM signature'
    header = 'DKIM-Signature'

    def __init__(self, database, ok_tag='dkim-ok', fail_tag='dkim-fail'):
        super().__init__(database)
        self.dkim_tag = {True: ok_tag, False: fail_tag}

    def handle_message(self, message):
        if message.get_header(self.header):
            dkim_ok = all(map(verify_dkim, message.get_filenames()))
            self.add_tags(message, self.dkim_tag[dkim_ok])
